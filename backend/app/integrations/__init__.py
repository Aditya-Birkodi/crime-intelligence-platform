"""Catalyst service adapters.

All AI/data plane integrations for production MUST go through these clients.
Do not call third-party LLM, vector DB, or object-storage APIs from app code.

TODO: Replace HTTP/SDK placeholders with official Zoho Catalyst Python SDK calls.
"""
