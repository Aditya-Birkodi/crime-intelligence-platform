"""Security helpers — Catalyst Authentication integration stubs.

TODO: Validate Catalyst Auth tokens / JWTs and map roles to police ranks.
"""

from __future__ import annotations


def hash_secret(value: str) -> str:
    """Placeholder secret hashing.

    TODO: Replace with proper password / token hashing if needed outside Catalyst Auth.
    """
    raise NotImplementedError(
        "TODO: Implement hashing or delegate to Catalyst Authentication"
    )


def verify_bearer_token(token: str) -> bool:
    """Placeholder bearer verification.

    TODO: Integrate Catalyst Authentication token introspection.
    """
    _ = token
    raise NotImplementedError("TODO: Verify token via Catalyst Authentication")
