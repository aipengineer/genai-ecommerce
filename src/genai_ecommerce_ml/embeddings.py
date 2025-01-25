"""Embedding-based recommender system."""

from typing import List, Dict, Any
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import joblib

from .base import BaseRecommender
from genai_ecommerce_core.models import Product


class EmbeddingRecommender(BaseRecommender):
    """Product recommender using text and image embeddings."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.text_model = SentenceTransformer(model_name)
        self.products: List[Product] = []
        self.embeddings: np.ndarray = None

    def _get_product_text(self, product: Product) -> str:
        """Combine product text fields for embedding."""
        text_parts = [
            product.name,
            product.description or "",
            product.brand or "",
            *[attr.value for attr in product.attributes],
            *[cat.name for cat in product.categories],
        ]
        return " ".join(text_parts)

    async def fit(self, products: List[Product]) -> None:
        """Generate embeddings for all products."""
        self.products = products
        texts = [self._get_product_text(p) for p in products]
        self.embeddings = self.text_model.encode(texts, convert_to_tensor=True)

    async def recommend(
        self, product: Product, n_recommendations: int = 5
    ) -> List[Product]:
        """Get recommendations based on embedding similarity."""
        text = self._get_product_text(product)
        query_embedding = self.text_model.encode([text], convert_to_tensor=True)

        # Calculate similarities
        similarities = cosine_similarity(query_embedding, self.embeddings)[0]

        # Get top similar products
        similar_indices = np.argsort(similarities)[::-1]
        recommendations = []

        for idx in similar_indices:
            if self.products[idx].id != product.id:
                recommendations.append(self.products[idx])
                if len(recommendations) >= n_recommendations:
                    break

        return recommendations

    async def save(self, path: str) -> None:
        """Save model to disk."""
        model_data = {
            "products": [p.model_dump() for p in self.products],
            "embeddings": self.embeddings.cpu().numpy(),
        }
        joblib.dump(model_data, path)

    async def load(self, path: str) -> None:
        """Load model from disk."""
        model_data = joblib.load(path)
        self.products = [Product.model_validate(p) for p in model_data["products"]]
        self.embeddings = model_data["embeddings"]
