"""ChatGPT sign-in authentication for OpenAI."""

import asyncio
import base64
import hashlib
import json
import os
import secrets
import time
import uuid
import webbrowser
from collections.abc import Iterator
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from threading import Lock
from typing import Any, Self
from urllib.parse import parse_qs, urlencode, urlsplit

import httpx
from pydantic import Field

from celeste.auth import Authentication
from celeste.exceptions import CredentialsError

AUTHORIZE_URL = "https://auth.openai.com/api/accounts/authorize"
TOKEN_URL = "https://auth.openai.com/api/accounts/oauth/token"  # nosec B105
RESOURCE = "https://api.openai.com/v1"
PLAN_SCOPE = "chatgpt.tokens.use.direct"
SCOPE = f"openid profile email offline_access resource.invoke {PLAN_SCOPE}"
# Seconds a renewal may hold the lock file; a real one takes about a second.
LOCK_TIMEOUT = 30

_thread_lock = Lock()


def _tokens(**fields: str) -> dict[str, Any]:
    """Request tokens for an authorization code or a refresh token."""
    response = httpx.post(TOKEN_URL, data={**fields, "resource": RESOURCE})
    if response.is_error:
        msg = (
            f"ChatGPT refused the sign-in ({response.status_code}): {response.text} "
            "Sign in again with ChatGPT.login()."
        )
        raise CredentialsError(msg)
    tokens: dict[str, Any] = response.json()
    return tokens


@contextmanager
def _renewing(path: Path) -> Iterator[None]:
    """Hold the sign-in's lock file: its refresh token rotates, so one process renews at a time."""
    lock = path.with_suffix(".lock")
    deadline = time.monotonic() + LOCK_TIMEOUT
    while True:
        try:
            os.close(os.open(lock, os.O_CREAT | os.O_EXCL))
            break
        except FileExistsError:
            # A lock held this long was left by a process that died while renewing.
            if time.monotonic() > deadline:
                lock.unlink(missing_ok=True)
            time.sleep(0.05)
    try:
        yield
    finally:
        lock.unlink(missing_ok=True)


class ChatGPT(Authentication):
    """Sign in with ChatGPT: OpenAI text requests are billed to the ChatGPT plan, not an API key.

    Sign in once per machine with ChatGPT.login(); the sign-in is kept in `path` and renewed as needed.
    """

    path: Path = Field(
        default_factory=lambda: Path.home() / ".config" / "celeste" / "chatgpt.json"
    )

    async def aget_headers(self) -> dict[str, str]:
        """Renew the access token without blocking the event loop."""
        return await asyncio.to_thread(self.get_headers)

    def get_headers(self) -> dict[str, str]:
        """Return the bearer header, renewing the access token when it is about to expire."""
        session = self._read()
        if session["expires_at"] - time.time() < 60:
            with _thread_lock, _renewing(self.path):
                # Another thread or process may have renewed it while this one waited.
                session = self._read()
                if session["expires_at"] - time.time() < 60:
                    session = self._save(
                        session["client_id"],
                        session["ext_agent_host_id"],
                        _tokens(
                            grant_type="refresh_token",
                            client_id=session["client_id"],
                            refresh_token=session["refresh_token"],
                        ),
                    )
        return {"Authorization": f"Bearer {session['access_token']}"}

    @classmethod
    def login(cls, path: Path | None = None) -> Self:
        """Sign in with ChatGPT in the browser and keep the sign-in for this machine."""
        auth = cls(path=path) if path else cls()
        saved = json.loads(auth.path.read_text()) if auth.path.exists() else {}
        host_id = saved.get("ext_agent_host_id", uuid.uuid4().urn)
        verifier, state = secrets.token_urlsafe(64), secrets.token_urlsafe(32)
        callback: dict[str, str] = {}

        class Callback(BaseHTTPRequestHandler):
            """Receive OpenAI's redirect on the loopback address."""

            def do_GET(self) -> None:
                """Keep the redirect's query and send the user back to their terminal."""
                url = urlsplit(self.path)
                if url.path == "/auth/callback":
                    callback.update({k: v[0] for k, v in parse_qs(url.query).items()})
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"You can close this tab.")

            def log_message(self, format: str, *args: object) -> None:  # noqa: A002
                """Keep the authorization code out of the logs."""

        with HTTPServer(("127.0.0.1", 0), Callback) as server:
            # OpenAI fixes the host and path of the redirect; only the port may vary.
            redirect_uri = f"http://127.0.0.1:{server.server_port}/auth/callback"
            challenge = hashlib.sha256(verifier.encode()).digest()
            query = {
                "response_type": "code",
                "client_id": saved.get("client_id", "dynamic_agent_client"),
                "ext_agent_host_id": host_id,
                "redirect_uri": redirect_uri,
                "scope": SCOPE,
                "resource": RESOURCE,
                "state": state,
                "nonce": secrets.token_urlsafe(32),
                "code_challenge": base64.urlsafe_b64encode(challenge)
                .rstrip(b"=")
                .decode(),
                "code_challenge_method": "S256",
            }
            # The first sign-in registers the app; OpenAI then issues the client id to keep.
            if "client_id" not in saved:
                query["agent_name_hint"] = "Celeste"
            url = f"{AUTHORIZE_URL}?{urlencode(query)}"
            print(f"Sign in with ChatGPT: {url}")
            webbrowser.open(url)
            while not callback:
                server.handle_request()

        if callback.get("state") != state or "code" not in callback:
            msg = f"ChatGPT sign-in failed: {callback.get('error', 'the callback does not match this sign-in')}"
            raise CredentialsError(msg)
        client_id = saved.get("client_id") or callback["client_id"]
        tokens = _tokens(
            grant_type="authorization_code",
            client_id=client_id,
            code=callback["code"],
            code_verifier=verifier,
            redirect_uri=redirect_uri,
        )
        if PLAN_SCOPE not in tokens["scope"].split():
            msg = "ChatGPT sign-in did not allow this app to use the plan."
            raise CredentialsError(msg)
        auth._save(client_id, host_id, tokens)
        return auth

    def _read(self) -> dict[str, Any]:
        """Read the sign-in kept by login()."""
        try:
            session: dict[str, Any] = json.loads(self.path.read_text())
        except FileNotFoundError:
            msg = f"No ChatGPT sign-in at {self.path}. Sign in with ChatGPT.login()."
            raise CredentialsError(msg) from None
        return session

    def _save(
        self, client_id: str, host_id: str, tokens: dict[str, Any]
    ) -> dict[str, Any]:
        """Write the sign-in atomically, readable by its owner only."""
        session = {
            "client_id": client_id,
            "ext_agent_host_id": host_id,
            "access_token": tokens["access_token"],
            "refresh_token": tokens["refresh_token"],
            "expires_at": time.time() + tokens["expires_in"],
        }
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_suffix(".tmp")
        temporary.unlink(missing_ok=True)
        descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(descriptor, "w") as file:
            json.dump(session, file)
        temporary.replace(self.path)
        return session


__all__ = ["ChatGPT"]
