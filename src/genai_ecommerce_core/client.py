# genai-ecommerce/src/genai_ecommerce_core/client.py
"""API client for AboutYou e-commerce platform."""

import asyncio
import os
from pathlib import Path
from typing import Any

import httpx

from .models import ProductResponse


async def download_image(url: str, local_path: str) -> None:
    """
    Download an image from a URL and save it locally.
    """
    # Ensure the directory exists
    Path(os.path.dirname(local_path)).mkdir(parents=True, exist_ok=True)
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            with open(local_path, "wb") as f:
                f.write(response.content)
        print(f"Downloaded image to {local_path}")
    except Exception as error:
        print(f"Failed to download image {url}: {error}")


async def download_image_with_retries(
    url: str, local_path: str, retries: int = 3
) -> None:
    """
    Attempt to download an image with retries on failure.

    Args:
        url: The URL of the image to download.
        local_path: The local file path where the image will be saved.
        retries: The number of retry attempts.
    """
    for attempt in range(retries):
        try:
            await download_image(url, local_path)
            return
        except Exception:
            if attempt < retries - 1:
                wait_time = 2**attempt
                msg = (
                    f"Retrying image download in {wait_time}s: {url} "
                    f"(attempt {attempt + 1})"
                )
                print(msg)
                await asyncio.sleep(wait_time)
            else:
                print(f"Failed to download image after {retries} attempts: {url}")


class AboutYouClient:
    """Client for AboutYou API."""

    BASE_URL = "https://api-cloud.aboutyou.de/v1"

    def __init__(self) -> None:
        """Initialize client with default headers."""
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/121.0.0.0 Safari/537.36"
            ),
            "Accept": (
                "text/html,application/xhtml+xml,application/xml;q=0.9,"
                "image/avif,image/webp,image/apng,*/*;q=0.8,"
                "application/signed-exchange;v=b3;q=0.9"
            ),
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Referer": "https://www.aboutyou.de/",
            "Origin": "https://www.aboutyou.de",
            "Upgrade-Insecure-Requests": "1",
        }
        self._rate_limit_delay = 1.0  # Delay between requests in seconds

    async def get_products(
        self,
        with_attributes: str | None = None,
        page: int = 1,  # Page-based pagination
        filters: dict[str, Any] | None = None,
    ) -> ProductResponse:
        """
        Fetch products from the API.

        Args:
            with_attributes: Comma-separated list of attributes to include.
            page: Page number to fetch.
            filters: Additional filters to apply.

        Returns:
            ProductResponse object containing products and pagination info.
        """
        params = {
            "with": with_attributes or "categories,priceRange",
            "page": page,  # Use page-based pagination
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
