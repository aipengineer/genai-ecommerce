# genai-ecommerce/src/genai_ecommerce_core/client.py
"""API client for AboutYou e-commerce platform."""

import asyncio
import os
import subprocess
from pathlib import Path
from typing import Any

import httpx

from .models import ApiResponse


async def download_image(url: str, local_path: str) -> None:
    """
    Download an image from a URL and save it locally.
    """
    Path(os.path.dirname(local_path)).mkdir(parents=True, exist_ok=True)
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        with open(local_path, "wb") as f:
            f.write(response.content)
        print(f"Downloaded image to {local_path}")


async def download_image_with_retries(
    url: str, local_path: str, retries: int = 3
) -> None:
    """
    Attempt to download an image with retries on failure.
    """
    for attempt in range(retries):
        try:
            await download_image(url, local_path)
            return
        except Exception:
            if attempt < retries - 1:
                wait_time = 2**attempt
                msg = (
                    f"Retrying image download in {wait_time}s: {url}"
                    f" (attempt {attempt + 1})"
                )
                print(msg)
                await asyncio.sleep(wait_time)
            else:
                print(f"Failed to download image after {retries} attempts: {url}")


class AboutYouClient:
    """Client for AboutYou API."""

    BASE_URL = "https://api-cloud.aboutyou.de/v1"

    def __init__(self) -> None:
        """Initialize client with default headers and persistent session."""
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.2 Safari/605.1.15",
            "Accept": "application/json",
            "Accept-Encoding": "gzip, deflate",
            "Referer": "https://www.aboutyou.de",
            "Connection": "keep-alive",
        }
        self._rate_limit_delay = 1.0  # Delay between requests in seconds
        self.cookies = ""

    async def fetch_initial_cookies(self) -> None:
        """
        Perform an initial GET request to the homepage to fetch dynamic cookies.
        """
        async with httpx.AsyncClient(headers=self.headers) as client:
            url = "https://en.aboutyou.de/your-shop"
            response = await client.get(url)
            response.raise_for_status()
            # Extract the freshest cookie
            self.cookies = "; ".join(
                [f"{cookie.name}={cookie.value}" for cookie in client.cookies.jar]
            )
            print(f"Fetched cookies: {self.cookies}")

    def get_products_with_curl(
        self, page: int, with_attributes: str | None = None
    ) -> str:
        """
        Use curl to fetch products from the API with the dynamic cookie.
        """
        # Construct the curl command
        command = [
            "curl",
            "-X",
            "GET",
            f"{self.BASE_URL}/products?with={with_attributes or 'categories,priceRange'}&page={page}",
            "-H",
            f"User-Agent: {self.headers['User-Agent']}",
            "-H",
            "Accept: application/json",
            "-H",
            "Accept-Encoding: gzip, deflate",
            "-H",
            f"Referer: {self.headers['Referer']}",
            "-H",
            "Connection: keep-alive",
            "-H",
            f"Cookie: {self.cookies}",
            "--compressed",
        ]

        # Debug: Print the curl command
        print(f"Executing command: {' '.join(command)}")

        # Execute the command
        result = subprocess.run(command, capture_output=True, text=True)

        if result.returncode != 0:
            raise RuntimeError(f"Curl request failed: {result.stderr}")

        return result.stdout

    async def get_products(
        self,
        with_attributes: str | None = None,
        page: int = 1,
        filters: dict[str, Any] | None = None,
    ) -> ApiResponse:
        """
        Fetch products from the API using curl and a fresh cookie.
        """
        # Ensure cookies are fresh
        await self.fetch_initial_cookies()

        # Fetch products using curl
        response_json = self.get_products_with_curl(
            page=page, with_attributes=with_attributes
        )
        print(f"Response JSON (limited): {response_json[:500]}")

        # Parse and return the API response
        return ApiResponse.model_validate_json(response_json)

    async def close(self) -> None:
        """Close the HTTP client session."""
        pass  # No persistent session to close since we use subprocess for curl
