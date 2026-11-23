import logging
from typing import Dict, Any, List, Optional
from config import TAVILY_API_KEY

logger = logging.getLogger(__name__)

class TavilySearchClient:
    """
    Client for Tavily Search API.
    Used to discover public websites, IR portals, corporate registries, and published financial disclosures.
    """
    def __init__(self, api_key: str = TAVILY_API_KEY):
        self.api_key = api_key.strip()
        self._client = None
        if self.api_key:
            try:
                from tavily import TavilyClient
                self._client = TavilyClient(api_key=self.api_key)
            except Exception as e:
                logger.warning(f"Could not initialize TavilyClient: {e}")

    def is_configured(self) -> bool:
        return bool(self._client)

    def search_organisation(self, query: str) -> List[Dict[str, Any]]:
        """
        Searches web for organization background, official website, registry info.
        """
        if not self._client:
            logger.info("Tavily API key not configured or client unavailable.")
            return []

        search_query = f"{query} official corporate website company profile stock exchange industry"
        try:
            response = self._client.search(
                query=search_query,
                search_depth="advanced",
                include_domains=None,
                max_results=5
            )
            return response.get("results", [])
        except Exception as e:
            logger.error(f"Tavily search error: {e}")
            return []

    def search_financial_reports(self, org_name: str) -> List[Dict[str, Any]]:
        """
        Discovers official annual reports, quarterly filings, balance sheet disclosures.
        """
        if not self._client:
            return []

        search_query = f"{org_name} annual report financial statements revenue profit balance sheet investor relations"
        try:
            response = self._client.search(
                query=search_query,
                search_depth="advanced",
                max_results=6
            )
            return response.get("results", [])
        except Exception as e:
            logger.error(f"Tavily financial search error: {e}")
            return []
