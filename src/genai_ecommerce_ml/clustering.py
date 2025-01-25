"""Clustering-based recommender system."""

from typing import List, Dict, Any
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import joblib

from .base import BaseRecommender
from genai_ecommerce_core.models import Product


class ClusteringRecommender(BaseRecommender):
    """Product recommender using K-means clustering."""

    def __init__(self, n_clusters: int = 10):
        self.n_clusters = n_clusters
        self.kmeans = KMeans(n_clusters=n_clusters)
        self.scaler = StandardScaler()
        self.products: List[Product] = []
        self.features: np.ndarray = None

    def _extract_features(self, product: Product) -> List[float]:
        """Extract numerical features from product."""
        features = [
            product.price.amount,
            len(product.attributes),
            len(product.categories),
            float(bool(product.description)),  # Has description
            len(product.images),
        ]
        if product.price.original_amount:
            features.append(product.price.discount_percentage or 0.0)
        else:
            features.append(0.0)
        return features

    async def fit(self, products: List[Product]) -> None:
        """Train the clustering model."""
        self.products = products
        features = [self._extract_features(p) for p in products]
        self.features = self.scaler.fit_transform(features)
        self.kmeans.fit(self.features)

    async def recommend(
        self, product: Product, n_recommendations: int = 5
    ) -> List[Product]:
        """Get recommendations based on cluster membership."""
        features = self._extract_features(product)
        scaled_features = self.scaler.transform([features])
        cluster = self.kmeans.predict(scaled_features)[0]

        # Find products in same cluster
        cluster_mask = self.kmeans.labels_ == cluster
        cluster_products = [p for i, p in enumerate(self.products) if cluster_mask[i]]

        # Sort by price similarity
        target_price = product.price.amount
        sorted_products = sorted(
            cluster_products, key=lambda p: abs(p.price.amount - target_price)
        )

        # Remove the input product if present
        recommendations = [p for p in sorted_products if p.id != product.id]
        return recommendations[:n_recommendations]

    async def save(self, path: str) -> None:
        """Save model to disk."""
        model_data = {
            "kmeans": self.kmeans,
            "scaler": self.scaler,
            "products": [p.model_dump() for p in self.products],
            "features": self.features,
        }
        joblib.dump(model_data, path)

    async def load(self, path: str) -> None:
        """Load model from disk."""
        model_data = joblib.load(path)
        self.kmeans = model_data["kmeans"]
        self.scaler = model_data["scaler"]
        self.products = [Product.model_validate(p) for p in model_data["products"]]
        self.features = model_data["features"]
