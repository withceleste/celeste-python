"""Google Cloud authentication using ADC."""

from typing import Any, ClassVar

from pydantic import ConfigDict

from celeste.auth import Authentication
from celeste.exceptions import MissingDependencyError

VERTEX_BASE_URL = "https://{location}-aiplatform.googleapis.com"
VERTEX_GLOBAL_BASE_URL = "https://aiplatform.googleapis.com"


class GoogleADC(Authentication):
    """Google Application Default Credentials authentication.

    Uses google-auth library for automatic credential discovery from:
    1. GOOGLE_APPLICATION_CREDENTIALS env var
    2. gcloud auth application-default login
    3. Attached service account (on GCP)
    """

    scopes: ClassVar[list[str]] = ["https://www.googleapis.com/auth/cloud-platform"]
    project_id: str | None = None
    location: str = "global"

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
        try:
            import google.auth
            import google.auth.transport.requests
        except ImportError as e:
            raise MissingDependencyError(library="google-auth", extra="gcp") from e

        if self._credentials is None:
            self._credentials, self._project = google.auth.default(scopes=self.scopes)
            self._auth_request = google.auth.transport.requests.Request()

        if not self._credentials.valid:
            self._credentials.refresh(self._auth_request)

        return self._credentials.token, self.project_id or self._project

    @property
    def resolved_project_id(self) -> str | None:
        """Return effective project_id (explicit or from ADC credentials)."""
        if self._credentials is None:
            self._get_access_token()
        return self.project_id or self._project

    def get_vertex_base_url(self) -> str:
        """Return the Vertex AI base URL for the configured location."""
        if self.location == "global":
            return VERTEX_GLOBAL_BASE_URL
        return VERTEX_BASE_URL.format(location=self.location)

    def build_url(self, vertex_endpoint: str, model_id: str | None = None) -> str:
        """Build a complete Vertex AI URL from an endpoint template.

        Args:
            vertex_endpoint: Endpoint template with {project_id}, {location}, and
                optionally {model_id} placeholders.
            model_id: Model identifier for endpoints that include it in the path.
        """
        project_id = self.resolved_project_id
        if project_id is None:
            raise ValueError(
                "Vertex AI requires a project_id. "
                "Pass project_id to GoogleADC() or ensure credentials have a project."
            )
        base_url = self.get_vertex_base_url()
        if model_id is not None:
            endpoint = vertex_endpoint.format(
                project_id=project_id, location=self.location, model_id=model_id
            )
        else:
            endpoint = vertex_endpoint.format(
                project_id=project_id, location=self.location
            )
        return f"{base_url}{endpoint}"


__all__ = ["GoogleADC"]
