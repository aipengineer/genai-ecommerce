#genai-ecommerce/src/genai_ecommerce_core/client.py
"""API client for AboutYou e-commerce platform."""

import asyncio
from typing import Dict, Any, Optional
import httpx
from .models import ProductResponse


class AboutYouClient:
    """Client for AboutYou API."""

    BASE_URL = "https://api-cloud.aboutyou.de/v1"
    
    def __init__(self) -> None:
        """Initialize client with default headers."""
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                         "AppleWebKit/537.36 (KHTML, like Gecko) "
                         "Chrome/121.0.0.0 Safari/537.36",
            "Accept": "application/json",
            "Accept-Language": "en-US,en;q=0.9",
        }
        self._rate_limit_delay = 1.0  # Delay between requests in seconds

    async def get_products(
        self,
        with_attributes: Optional[str] = None,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
    ) -> ProductResponse:
        """
        Fetch products from the API.

        Args:
            with_attributes: Comma-separated list of attributes to include
            limit: Number of products to fetch
            filters: Additional filters to apply

        Returns:
            ProductResponse object containing products and pagination info
        """
        params = {
            "with": with_attributes or "categories,priceRange",
            "limit": limit,
        }
        if filters:
            for key, value in filters.items():
                params[f"filters[{key}]"] = value

        async with httpx.AsyncClient(headers=self.headers) as client:
            response = await client.get(
                f"{self.BASE_URL}/products",
                params=params,
            )
            response.raise_for_status()
            await asyncio.sleep(self._rate_limit_delay)
            
            return ProductResponse.model_validate(response.json())