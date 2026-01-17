"""Aggregated models for text modality."""

from celeste.models import Model

from .providers.anthropic.models import MODELS as ANTHROPIC_MODELS
from .providers.cohere.models import MODELS as COHERE_MODELS
from .providers.deepseek.models import MODELS as DEEPSEEK_MODELS
from .providers.google.models import MODELS as GOOGLE_MODELS
from .providers.groq.models import MODELS as GROQ_MODELS
from .providers.mistral.models import MODELS as MISTRAL_MODELS
from .providers.moonshot.models import MODELS as MOONSHOT_MODELS
from .providers.ollama.models import MODELS as OLLAMA_MODELS
from .providers.openai.models import MODELS as OPENAI_MODELS
from .providers.xai.models import MODELS as XAI_MODELS

MODELS: list[Model] = [
    *ANTHROPIC_MODELS,
    *COHERE_MODELS,
    *DEEPSEEK_MODELS,
    *GOOGLE_MODELS,
    *GROQ_MODELS,
    *OLLAMA_MODELS,
    *MISTRAL_MODELS,
    *MOONSHOT_MODELS,
    *OPENAI_MODELS,
    *XAI_MODELS,
]
