"""GraphQL client for the Predecessor API."""
import aiohttp
from typing import Any


class PredecessorAPI:
    """Async client for the Predecessor GraphQL API."""
    
    def __init__(self, api_url: str) -> None:
        self.api_url = api_url
        self._session: aiohttp.ClientSession | None = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create the aiohttp session."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session
    
    async def close(self) -> None:
        """Close the HTTP session."""
        if self._session and not self._session.closed:
            await self._session.close()
    
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
        
        async with session.post(
            self.api_url,
            json=payload,
            headers={"Content-Type": "application/json"}
        ) as response:
            response.raise_for_status()
            result = await response.json()
        
        if "errors" in result:
            raise Exception(f"GraphQL errors: {result['errors']}")
        
        return result.get("data", {})

