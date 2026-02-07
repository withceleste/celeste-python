"""Tests for Vertex AI URL routing across all Vertex-enabled providers."""

from unittest.mock import MagicMock, patch

import pytest
from pydantic import SecretStr

from celeste.auth import AuthHeader
from celeste.models import Model
from celeste.providers.google.auth import (
    VERTEX_GLOBAL_BASE_URL,
    GoogleADC,
)

# --- GoogleADC helpers ---


class TestGoogleADCResolvedProjectId:
    """Test resolved_project_id property."""

    @patch("google.auth.default")
    @patch("google.auth.transport.requests.Request")
    def test_returns_explicit_project_id(
        self, mock_request: MagicMock, mock_default: MagicMock
    ) -> None:
        """Explicit project_id takes priority over ADC-inferred project."""
        mock_creds = MagicMock()
        mock_creds.valid = True
        mock_creds.token = "fake-token"  # nosec B105
        mock_default.return_value = (mock_creds, "adc-project")

        auth = GoogleADC(project_id="explicit-project")
        assert auth.resolved_project_id == "explicit-project"

    @patch("google.auth.default")
    @patch("google.auth.transport.requests.Request")
    def test_falls_back_to_adc_project(
        self, mock_request: MagicMock, mock_default: MagicMock
    ) -> None:
        """Falls back to project from ADC credentials when no explicit project_id."""
        mock_creds = MagicMock()
        mock_creds.valid = True
        mock_creds.token = "fake-token"  # nosec B105
        mock_default.return_value = (mock_creds, "adc-project")

        auth = GoogleADC()
        assert auth.resolved_project_id == "adc-project"

    @patch("google.auth.default")
    @patch("google.auth.transport.requests.Request")
    def test_returns_none_when_no_project(
        self, mock_request: MagicMock, mock_default: MagicMock
    ) -> None:
        """Returns None when neither explicit nor ADC project is available."""
        mock_creds = MagicMock()
        mock_creds.valid = True
        mock_creds.token = "fake-token"  # nosec B105
        mock_default.return_value = (mock_creds, None)

        auth = GoogleADC()
        assert auth.resolved_project_id is None


class TestGoogleADCGetVertexBaseUrl:
    """Test get_vertex_base_url method."""

    def test_global_location(self) -> None:
        """Global location returns the global Vertex AI endpoint."""
        auth = GoogleADC(location="global")
        assert auth.get_vertex_base_url() == VERTEX_GLOBAL_BASE_URL

    def test_regional_location(self) -> None:
        """Regional location returns location-prefixed endpoint."""
        auth = GoogleADC(location="us-central1")
        assert (
            auth.get_vertex_base_url()
            == "https://us-central1-aiplatform.googleapis.com"
        )

    def test_europe_location(self) -> None:
        """European location returns correct regional endpoint."""
        auth = GoogleADC(location="europe-west4")
        assert (
            auth.get_vertex_base_url()
            == "https://europe-west4-aiplatform.googleapis.com"
        )


# --- Helpers for client URL testing ---


def _make_mock_model(model_id: str = "gemini-2.0-flash") -> Model:
    """Create a minimal Model for testing."""
    return Model(id=model_id, provider="google", display_name="Test Model")


def _make_adc(
    project_id: str | None = "test-project",
    location: str = "us-central1",
) -> GoogleADC:
    """Create a GoogleADC with pre-loaded credentials to avoid real auth calls."""
    auth = GoogleADC(project_id=project_id, location=location)
    # Pre-set private attrs so resolved_project_id doesn't trigger real google.auth
    object.__setattr__(auth, "_credentials", MagicMock(valid=True, token="fake"))  # nosec B106
    object.__setattr__(auth, "_project", "adc-fallback-project")
    return auth


def _make_api_key() -> AuthHeader:
    """Create a simple API key auth."""
    return AuthHeader(
        secret=SecretStr("test-api-key"),
        header="x-goog-api-key",
        prefix="",
    )


# --- GenerateContent routing ---


class TestGenerateContentRouting:
    """Test _build_url in GoogleGenerateContentClient."""

    def _make_client(self, auth: AuthHeader | GoogleADC) -> MagicMock:
        from celeste.providers.google.generate_content.client import (
            GoogleGenerateContentClient,
        )

        client = MagicMock(spec=GoogleGenerateContentClient)
        client.auth = auth
        client.model = _make_mock_model()
        # Bind the real methods
        client._build_url = GoogleGenerateContentClient._build_url.__get__(client)
        client._get_vertex_endpoint = (
            GoogleGenerateContentClient._get_vertex_endpoint.__get__(client)
        )
        return client

    def test_api_key_uses_gemini_endpoint(self) -> None:
        from celeste.providers.google.generate_content import config

        client = self._make_client(_make_api_key())
        url = client._build_url(config.GoogleGenerateContentEndpoint.GENERATE_CONTENT)
        assert (
            url
            == "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
        )

    def test_adc_uses_vertex_endpoint(self) -> None:
        client = self._make_client(_make_adc())
        from celeste.providers.google.generate_content import config

        url = client._build_url(config.GoogleGenerateContentEndpoint.GENERATE_CONTENT)
        assert "us-central1-aiplatform.googleapis.com" in url
        assert "projects/test-project" in url
        assert "locations/us-central1" in url
        assert "gemini-2.0-flash:generateContent" in url

    def test_adc_global_location(self) -> None:
        from celeste.providers.google.generate_content import config

        client = self._make_client(_make_adc(location="global"))
        url = client._build_url(config.GoogleGenerateContentEndpoint.GENERATE_CONTENT)
        assert url.startswith("https://aiplatform.googleapis.com")

    def test_adc_stream_endpoint(self) -> None:
        from celeste.providers.google.generate_content import config

        client = self._make_client(_make_adc())
        url = client._build_url(
            config.GoogleGenerateContentEndpoint.STREAM_GENERATE_CONTENT
        )
        assert "streamGenerateContent" in url
        assert "us-central1-aiplatform.googleapis.com" in url

    def test_adc_no_project_raises(self) -> None:
        client = self._make_client(_make_adc(project_id=None))
        # Override the fallback too
        object.__setattr__(client.auth, "_project", None)
        from celeste.providers.google.generate_content import config

        with pytest.raises(ValueError, match="Vertex AI requires a project_id"):
            client._build_url(config.GoogleGenerateContentEndpoint.GENERATE_CONTENT)


# --- Anthropic Messages routing ---


class TestAnthropicMessagesRouting:
    """Test _build_url in AnthropicMessagesClient."""

    def _make_client(self, auth: AuthHeader | GoogleADC) -> MagicMock:
        from celeste.providers.anthropic.messages.client import AnthropicMessagesClient

        client = MagicMock(spec=AnthropicMessagesClient)
        client.auth = auth
        client.model = _make_mock_model("claude-sonnet-4-5-20250929")
        client._build_url = AnthropicMessagesClient._build_url.__get__(client)
        client._get_vertex_endpoint = (
            AnthropicMessagesClient._get_vertex_endpoint.__get__(client)
        )
        return client

    def test_api_key_uses_anthropic_endpoint(self) -> None:
        from celeste.providers.anthropic.messages import config

        client = self._make_client(_make_api_key())
        url = client._build_url(config.AnthropicMessagesEndpoint.CREATE_MESSAGE)
        assert url == "https://api.anthropic.com/v1/messages"

    def test_adc_uses_vertex_rawpredict(self) -> None:
        from celeste.providers.anthropic.messages import config

        client = self._make_client(_make_adc())
        url = client._build_url(
            config.AnthropicMessagesEndpoint.CREATE_MESSAGE, streaming=False
        )
        assert "us-central1-aiplatform.googleapis.com" in url
        assert "projects/test-project" in url
        assert "publishers/anthropic" in url
        assert "rawPredict" in url

    def test_adc_streaming_uses_stream_rawpredict(self) -> None:
        from celeste.providers.anthropic.messages import config

        client = self._make_client(_make_adc())
        url = client._build_url(
            config.AnthropicMessagesEndpoint.CREATE_MESSAGE, streaming=True
        )
        assert "streamRawPredict" in url

    def test_adc_no_project_raises(self) -> None:
        from celeste.providers.anthropic.messages import config

        client = self._make_client(_make_adc(project_id=None))
        object.__setattr__(client.auth, "_project", None)
        with pytest.raises(ValueError, match="Vertex AI requires a project_id"):
            client._build_url(config.AnthropicMessagesEndpoint.CREATE_MESSAGE)


# --- Imagen routing ---


class TestImagenRouting:
    """Test _build_url in GoogleImagenClient."""

    def _make_client(self, auth: AuthHeader | GoogleADC) -> MagicMock:
        from celeste.providers.google.imagen.client import GoogleImagenClient

        client = MagicMock(spec=GoogleImagenClient)
        client.auth = auth
        client.model = _make_mock_model("imagen-3.0-generate-002")
        client._build_url = GoogleImagenClient._build_url.__get__(client)
        client._get_vertex_endpoint = GoogleImagenClient._get_vertex_endpoint.__get__(
            client
        )
        return client

    def test_api_key_uses_gemini_endpoint(self) -> None:
        from celeste.providers.google.imagen import config

        client = self._make_client(_make_api_key())
        url = client._build_url(config.GoogleImagenEndpoint.CREATE_IMAGE)
        assert (
            url
            == "https://generativelanguage.googleapis.com/v1beta/models/imagen-3.0-generate-002:predict"
        )

    def test_adc_uses_vertex_endpoint(self) -> None:
        from celeste.providers.google.imagen import config

        client = self._make_client(_make_adc())
        url = client._build_url(config.GoogleImagenEndpoint.CREATE_IMAGE)
        assert "us-central1-aiplatform.googleapis.com" in url
        assert "projects/test-project" in url
        assert "publishers/google" in url
        assert "imagen-3.0-generate-002:predict" in url

    def test_adc_no_project_raises(self) -> None:
        from celeste.providers.google.imagen import config

        client = self._make_client(_make_adc(project_id=None))
        object.__setattr__(client.auth, "_project", None)
        with pytest.raises(ValueError, match="Vertex AI requires a project_id"):
            client._build_url(config.GoogleImagenEndpoint.CREATE_IMAGE)


# --- Embeddings routing ---


class TestEmbeddingsRouting:
    """Test _build_url in GoogleEmbeddingsClient."""

    def _make_client(self, auth: AuthHeader | GoogleADC) -> MagicMock:
        from celeste.providers.google.embeddings.client import GoogleEmbeddingsClient

        client = MagicMock(spec=GoogleEmbeddingsClient)
        client.auth = auth
        client.model = _make_mock_model("text-embedding-004")
        client._build_url = GoogleEmbeddingsClient._build_url.__get__(client)
        client._get_vertex_endpoint = (
            GoogleEmbeddingsClient._get_vertex_endpoint.__get__(client)
        )
        return client

    def test_api_key_uses_gemini_endpoint(self) -> None:
        from celeste.providers.google.embeddings import config

        client = self._make_client(_make_api_key())
        url = client._build_url(config.GoogleEmbeddingsEndpoint.EMBED_CONTENT)
        assert (
            url
            == "https://generativelanguage.googleapis.com/v1beta/models/text-embedding-004:embedContent"
        )

    def test_adc_uses_vertex_endpoint(self) -> None:
        from celeste.providers.google.embeddings import config

        client = self._make_client(_make_adc())
        url = client._build_url(config.GoogleEmbeddingsEndpoint.EMBED_CONTENT)
        assert "us-central1-aiplatform.googleapis.com" in url
        assert "projects/test-project" in url
        assert "publishers/google" in url
        assert "text-embedding-004:predict" in url

    def test_adc_batch_uses_vertex_endpoint(self) -> None:
        from celeste.providers.google.embeddings import config

        client = self._make_client(_make_adc())
        url = client._build_url(config.GoogleEmbeddingsEndpoint.BATCH_EMBED_CONTENTS)
        assert "us-central1-aiplatform.googleapis.com" in url
        assert "text-embedding-004:predict" in url

    def test_adc_no_project_raises(self) -> None:
        from celeste.providers.google.embeddings import config

        client = self._make_client(_make_adc(project_id=None))
        object.__setattr__(client.auth, "_project", None)
        with pytest.raises(ValueError, match="Vertex AI requires a project_id"):
            client._build_url(config.GoogleEmbeddingsEndpoint.EMBED_CONTENT)


# --- Veo routing ---


class TestVeoRouting:
    """Test _build_url and _build_poll_url in GoogleVeoClient."""

    def _make_client(self, auth: AuthHeader | GoogleADC) -> MagicMock:
        from celeste.providers.google.veo.client import GoogleVeoClient

        client = MagicMock(spec=GoogleVeoClient)
        client.auth = auth
        client.model = _make_mock_model("veo-2.0-generate-001")
        client._build_url = GoogleVeoClient._build_url.__get__(client)
        client._get_vertex_endpoint = GoogleVeoClient._get_vertex_endpoint.__get__(
            client
        )
        client._build_poll_url = GoogleVeoClient._build_poll_url.__get__(client)
        return client

    def test_api_key_uses_gemini_endpoint(self) -> None:
        from celeste.providers.google.veo import config

        client = self._make_client(_make_api_key())
        url = client._build_url(config.GoogleVeoEndpoint.CREATE_VIDEO)
        assert (
            url
            == "https://generativelanguage.googleapis.com/v1beta/models/veo-2.0-generate-001:predictLongRunning"
        )

    def test_adc_uses_vertex_endpoint(self) -> None:
        from celeste.providers.google.veo import config

        client = self._make_client(_make_adc())
        url = client._build_url(config.GoogleVeoEndpoint.CREATE_VIDEO)
        assert "us-central1-aiplatform.googleapis.com" in url
        assert "projects/test-project" in url
        assert "publishers/google" in url
        assert "veo-2.0-generate-001:predictLongRunning" in url

    def test_api_key_poll_url(self) -> None:
        client = self._make_client(_make_api_key())
        url = client._build_poll_url("operations/abc123")
        assert (
            url == "https://generativelanguage.googleapis.com/v1beta/operations/abc123"
        )

    def test_adc_poll_url(self) -> None:
        client = self._make_client(_make_adc())
        url = client._build_poll_url(
            "projects/test-project/locations/us-central1/operations/abc123"
        )
        assert "us-central1-aiplatform.googleapis.com" in url
        assert "fetchPredictOperation" in url

    def test_adc_no_project_raises(self) -> None:
        from celeste.providers.google.veo import config

        client = self._make_client(_make_adc(project_id=None))
        object.__setattr__(client.auth, "_project", None)
        with pytest.raises(ValueError, match="Vertex AI requires a project_id"):
            client._build_url(config.GoogleVeoEndpoint.CREATE_VIDEO)


# --- Mistral routing ---


class TestMistralRouting:
    """Test _build_url in MistralChatClient."""

    def _make_client(self, auth: AuthHeader | GoogleADC) -> MagicMock:
        from celeste.providers.mistral.chat.client import MistralChatClient

        client = MagicMock(spec=MistralChatClient)
        client.auth = auth
        client.model = _make_mock_model("mistral-large-2411")
        client._build_url = MistralChatClient._build_url.__get__(client)
        client._get_vertex_endpoint = MistralChatClient._get_vertex_endpoint.__get__(
            client
        )
        return client

    def test_api_key_uses_mistral_endpoint(self) -> None:
        from celeste.providers.mistral.chat import config

        client = self._make_client(_make_api_key())
        url = client._build_url(config.MistralChatEndpoint.CREATE_CHAT_COMPLETION)
        assert url == "https://api.mistral.ai/v1/chat/completions"

    def test_adc_uses_vertex_rawpredict(self) -> None:
        from celeste.providers.mistral.chat import config

        client = self._make_client(_make_adc())
        url = client._build_url(config.MistralChatEndpoint.CREATE_CHAT_COMPLETION)
        assert "us-central1-aiplatform.googleapis.com" in url
        assert "projects/test-project" in url
        assert "publishers/mistralai" in url
        assert "mistral-large-2411:rawPredict" in url

    def test_adc_streaming_uses_stream_rawpredict(self) -> None:
        from celeste.providers.mistral.chat import config

        client = self._make_client(_make_adc())
        url = client._build_url(
            config.MistralChatEndpoint.CREATE_CHAT_COMPLETION, streaming=True
        )
        assert "streamRawPredict" in url
        assert "publishers/mistralai" in url

    def test_adc_global_location(self) -> None:
        from celeste.providers.mistral.chat import config

        client = self._make_client(_make_adc(location="global"))
        url = client._build_url(config.MistralChatEndpoint.CREATE_CHAT_COMPLETION)
        assert url.startswith("https://aiplatform.googleapis.com")

    def test_adc_no_project_raises(self) -> None:
        from celeste.providers.mistral.chat import config

        client = self._make_client(_make_adc(project_id=None))
        object.__setattr__(client.auth, "_project", None)
        with pytest.raises(ValueError, match="Vertex AI requires a project_id"):
            client._build_url(config.MistralChatEndpoint.CREATE_CHAT_COMPLETION)


# --- DeepSeek routing ---


class TestDeepSeekRouting:
    """Test _build_url in DeepSeekChatClient."""

    def _make_client(self, auth: AuthHeader | GoogleADC) -> MagicMock:
        from celeste.providers.deepseek.chat.client import DeepSeekChatClient

        client = MagicMock(spec=DeepSeekChatClient)
        client.auth = auth
        client.model = _make_mock_model("deepseek-ai/deepseek-v3-0324")
        client._build_url = DeepSeekChatClient._build_url.__get__(client)
        client._get_vertex_endpoint = DeepSeekChatClient._get_vertex_endpoint.__get__(
            client
        )
        return client

    def test_api_key_uses_deepseek_endpoint(self) -> None:
        from celeste.providers.deepseek.chat import config

        client = self._make_client(_make_api_key())
        url = client._build_url(config.DeepSeekChatEndpoint.CREATE_CHAT)
        assert url == "https://api.deepseek.com/v1/chat/completions"

    def test_adc_uses_vertex_openai_compatible(self) -> None:
        from celeste.providers.deepseek.chat import config

        client = self._make_client(_make_adc())
        url = client._build_url(config.DeepSeekChatEndpoint.CREATE_CHAT)
        assert "us-central1-aiplatform.googleapis.com" in url
        assert "projects/test-project" in url
        assert "endpoints/openapi/chat/completions" in url

    def test_adc_url_has_no_model_id(self) -> None:
        """Model ID should be in request body only, not in the URL."""
        from celeste.providers.deepseek.chat import config

        client = self._make_client(_make_adc())
        url = client._build_url(config.DeepSeekChatEndpoint.CREATE_CHAT)
        assert "deepseek" not in url.lower().split("endpoints")[1]

    def test_adc_global_location(self) -> None:
        from celeste.providers.deepseek.chat import config

        client = self._make_client(_make_adc(location="global"))
        url = client._build_url(config.DeepSeekChatEndpoint.CREATE_CHAT)
        assert url.startswith("https://aiplatform.googleapis.com")

    def test_adc_no_project_raises(self) -> None:
        from celeste.providers.deepseek.chat import config

        client = self._make_client(_make_adc(project_id=None))
        object.__setattr__(client.auth, "_project", None)
        with pytest.raises(ValueError, match="Vertex AI requires a project_id"):
            client._build_url(config.DeepSeekChatEndpoint.CREATE_CHAT)


# --- Cloud TTS auth preservation ---


class TestCloudTTSAuthPreservation:
    """Test that Cloud TTS preserves user-provided GoogleADC."""

    def test_preserves_user_provided_adc(self) -> None:
        """User-provided GoogleADC should not be overwritten by model_post_init logic."""
        # Test the conditional logic: isinstance check should preserve existing GoogleADC
        user_adc = GoogleADC(project_id="my-project", location="europe-west4")
        assert isinstance(user_adc, GoogleADC)

        # Verify the source code has the isinstance guard
        import inspect

        from celeste.providers.google.cloud_tts.client import GoogleCloudTTSClient

        source = inspect.getsource(GoogleCloudTTSClient.model_post_init)
        assert "isinstance(self.auth, GoogleADC)" in source

    def test_non_adc_auth_gets_replaced(self) -> None:
        """Non-GoogleADC auth should trigger replacement (verified via source inspection)."""
        api_key = _make_api_key()
        assert not isinstance(api_key, GoogleADC)

        import inspect

        from celeste.providers.google.cloud_tts.client import GoogleCloudTTSClient

        source = inspect.getsource(GoogleCloudTTSClient.model_post_init)
        # Ensure the conditional creates new GoogleADC when auth is not GoogleADC
        assert "if not isinstance(self.auth, GoogleADC)" in source
        assert 'object.__setattr__(self, "auth", GoogleADC())' in source
