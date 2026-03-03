"""
Backend API module for SRAG (Semantic Retrieval-Augmented Generation).

Import app using: from backend.app import app
"""

# Lazy imports to avoid circular dependencies
def __getattr__(name):
    if name == "app":
        from .app import app
        return app
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = [
    "app",
    "models",
    "database",
    "crud",
]
