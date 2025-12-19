"""Google provider package for Celeste AI."""


def register_provider() -> None:
    """Register Google provider auth types."""
    from celeste.auth import register_auth
    from celeste_google.auth import GoogleADC

    register_auth("google_adc", GoogleADC)


__all__ = ["register_provider"]
