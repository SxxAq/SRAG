
# API Authentication Guide

All API requests must include a valid API key. Developers can generate and manage keys
from the Developer Dashboard. Use the following header format:

    Authorization: Bearer <YOUR_API_KEY>

Expired or revoked keys will result in a 401 Unauthorized response. API keys should be
stored securely and never exposed in client-side code. For rotating keys, the old key
remains active for 24 hours to ensure smooth migration.
    