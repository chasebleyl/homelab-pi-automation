"""GraphQL client for the Predecessor API."""
import aiohttp
import base64
import time
from typing import Any, Optional


class PredecessorAPI:
    """Async client for the Predecessor GraphQL API with OAuth2 support."""

    def __init__(
        self,
        api_url: str,
        oauth_token_url: Optional[str] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
    ) -> None:
        """
        Initialize the API client.

        Args:
            api_url: The GraphQL API endpoint URL
            oauth_token_url: OAuth2 token endpoint (optional, enables auth)
            client_id: OAuth2 client ID (required if oauth_token_url set)
            client_secret: OAuth2 client secret (required if oauth_token_url set)
        """
        self.api_url = api_url
        self.oauth_token_url = oauth_token_url
        self.client_id = client_id
        self.client_secret = client_secret
        self._session: aiohttp.ClientSession | None = None
        self._access_token: Optional[str] = None
        self._token_expires_at: float = 0

    @property
    def has_auth(self) -> bool:
        """Check if OAuth2 credentials are configured."""
        return bool(self.oauth_token_url and self.client_id and self.client_secret)

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create the aiohttp session."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def close(self) -> None:
        """Close the HTTP session."""
        if self._session and not self._session.closed:
            await self._session.close()

    async def _get_access_token(self) -> Optional[str]:
        """
        Get a valid access token, fetching a new one if needed.

        Returns:
            Access token string, or None if auth not configured
        """
        if not self.has_auth:
            return None

        # Check if we have a valid cached token (with 60s buffer)
        if self._access_token and time.time() < (self._token_expires_at - 60):
            return self._access_token

        # Fetch new token
        session = await self._get_session()

        # Create Basic auth header from client credentials
        credentials = f"{self.client_id}:{self.client_secret}"
        basic_auth = base64.b64encode(credentials.encode()).decode()

        async with session.post(
            self.oauth_token_url,
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Authorization": f"Basic {basic_auth}",
            },
            data="grant_type=client_credentials",
        ) as response:
            if response.status != 200:
                error_text = await response.text()
                raise Exception(f"OAuth2 token request failed: {response.status} - {error_text}")

            token_data = await response.json()

        self._access_token = token_data["access_token"]
        expires_in = token_data.get("expires_in", 1800)  # Default 30 min
        self._token_expires_at = time.time() + expires_in

        return self._access_token

    async def query(self, query: str, variables: dict[str, Any] | None = None) -> dict[str, Any]:
        """
        Execute a GraphQL query against the Predecessor API.

        Args:
            query: The GraphQL query string
            variables: Optional variables for the query

        Returns:
            The data portion of the GraphQL response

        Raises:
            Exception: If the API returns errors
        """
        session = await self._get_session()

        payload = {"query": query}
        if variables:
            payload["variables"] = variables

        headers = {"Content-Type": "application/json"}

        # Add auth header if configured
        access_token = await self._get_access_token()
        if access_token:
            headers["Authorization"] = f"Bearer {access_token}"

        async with session.post(
            self.api_url,
            json=payload,
            headers=headers,
        ) as response:
            response.raise_for_status()
            result = await response.json()

        if "errors" in result:
            raise Exception(f"GraphQL errors: {result['errors']}")

        return result.get("data", {})
