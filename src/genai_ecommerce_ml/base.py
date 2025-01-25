# genai-ecommerce/src/genai_ecommerce_ml/base.py
"""Base classes for recommender systems."""

from abc import ABC, abstractmethod

from genai_ecommerce_core.models import Product


class BaseRecommender(ABC):
    """Base class for all recommender systems."""

    @abstractmethod
    async def fit(self, products: list[Product]) -> None:
        """Train the recommender system."""
        pass

    @abstractmethod
    async def recommend(
        self, product: Product, n_recommendations: int = 5
    ) -> list[Product]:
        """Get recommendations for a product."""
        pass

    @abstractmethod
    async def save(self, path: str) -> None:
        """Save model to disk."""
        pass

    @abstractmethod
    async def load(self, path: str) -> None:
        """Load model from disk."""
        pass
