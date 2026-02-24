"""HuggingFace provider package for Celeste AI."""

from celeste.core import Provider
from celeste.credentials import register_auth

register_auth(  # nosec B106 - env var name, not hardcoded password
    provider=Provider.HUGGINGFACE,
    secret_name="HF_TOKEN",
    header="Authorization",
    prefix="Bearer ",
)
