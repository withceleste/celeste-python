"""Google Cloud authentication using ADC."""

from typing import Any, ClassVar

from pydantic import ConfigDict

from celeste.auth import Authentication


class GoogleADC(Authentication):
    """Google Application Default Credentials authentication.

    Uses google-auth library for automatic credential discovery from:
    1. GOOGLE_APPLICATION_CREDENTIALS env var
    2. gcloud auth application-default login
    3. Attached service account (on GCP)
    """

    scopes: ClassVar[list[str]] = ["https://www.googleapis.com/auth/cloud-platform"]
    project_id: str | None = None

    model_config: ClassVar[ConfigDict] = ConfigDict(arbitrary_types_allowed=True)

    _credentials: Any = None
    _auth_request: Any = None
    _project: str | None = None

    def get_headers(self) -> dict[str, str]:
        """Return OAuth Bearer token header with quota project."""
        token, project = self._get_access_token()
        headers = {"Authorization": f"Bearer {token}"}
        if project:
            headers["x-goog-user-project"] = project
        return headers

    def _get_access_token(self) -> tuple[str, str | None]:
        """Get OAuth access token using Application Default Credentials."""
        import google.auth
        import google.auth.transport.requests

        if self._credentials is None:
            self._credentials, self._project = google.auth.default(scopes=self.scopes)
            self._auth_request = google.auth.transport.requests.Request()

        if not self._credentials.valid:
            self._credentials.refresh(self._auth_request)

        return self._credentials.token, self.project_id or self._project


__all__ = ["GoogleADC"]
