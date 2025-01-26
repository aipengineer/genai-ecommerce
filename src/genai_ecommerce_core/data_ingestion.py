# genai-ecommerce/src/genai_ecommerce_core/data_ingestion.py
import asyncio
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession

from genai_ecommerce_core.client import AboutYouClient
from genai_ecommerce_core.database import bulk_insert_products, init_db
from genai_ecommerce_core.models import ProductResponse


@asynccontextmanager
async def get_db() -> AsyncSession:
    """
    Async context manager to initialize and close the database session.
    """
    db_url = "sqlite+aiosqlite:///ecommerce.db"
    session_maker = await init_db(db_url)
    async with session_maker() as db:
        try:
            yield db
        finally:
            await db.close()


def parse_product(product: dict) -> ProductResponse:
    """
    Parse and transform raw product data into the ProductResponse model.

    Args:
        product: Raw product data from the API.

    Returns:
        A ProductResponse object.
    """
    try:
        # Extract and transform price information
        price_data = product.get("priceRange", {}).get("min", {})
        price = {
            "amount": price_data.get("withTax", 0) / 100.0,
            "currency": price_data.get("currencyCode", "USD"),
        }

        # Extract and transform categories (flattening the nested lists)
        categories = []
        if "categories" in product:
            for category_list in product["categories"]:
                if isinstance(category_list, list):
                    for cat in category_list:
                        categories.append(
                            {
                                "id": cat.get("categoryId", 0),
                                "name": cat.get("categoryName", "Unknown"),
                                "parent_id": None,  # Parent-child relationships aren't clear in this structure
                                "level": 0,  # Default level
                                "path": cat.get("categorySlug", ""),
                            }
                        )

        # Extract and transform images
        images = []
        if "images" in product:
            for img in product["images"]:
                images.append(
                    {
                        "url": f"https://cdn.aboutyou.com/{img.get('hash', '')}",
                        "type": "standard",
                    }
                )

        # Construct the parsed product
        parsed_product = {
            "id": product.get("id", 0),
            "name": product.get("name", "Unknown"),
            "price": price,
            "categories": categories,
            "images": images,
            "created_at": product.get("createdAt"),
            "updated_at": product.get("updatedAt"),
        }

        # Validate and return the parsed product
        return ProductResponse.parse_obj(parsed_product)

    except Exception as e:
        print(f"Validation error for product {product.get('id', 'unknown')}: {e}")
        raise


async def ingest_data() -> None:
    """
    Fetch data from AboutYou API and store it in the database.
    """
    async with get_db() as db:
        client = AboutYouClient()
        page = 1

        try:
            while True:
                print(f"Fetching page {page}...")
                response = await client.get_products(page=page)
                print(response)

                # Exit loop if there are no more products
                if not response.entities:
                    print("No more products to process. Exiting.")
                    break

                products = []

                # Process each product in the response
                for raw_product in response.entities:
                    try:
                        # Parse and validate product data
                        parsed_product = parse_product(raw_product)

                        # Transform parsed data into a dictionary for the database
                        product_data = {
                            "id": parsed_product.id,
                            "name": parsed_product.name,
                            "price": parsed_product.price.amount
                            if parsed_product.price
                            else 0.0,
                            "category": parsed_product.categories[0].name
                            if parsed_product.categories
                            else "Unknown",
                            "images": [
                                {"url": img.url, "type": img.type}
                                for img in parsed_product.images or []
                            ],
                        }

                        # Append to products list for bulk insert
                        products.append(product_data)

                    except Exception as e:
                        msg = (
                            f"Error processing product"
                            f" {raw_product.get('id', 'unknown')}: {e}"
                        )
                        print(msg)

                # Insert products into the database
                if products:
                    await bulk_insert_products(db, products)
                    print(f"Page {page}: Inserted {len(products)} products.")

                page += 1

        except Exception as e:
            print(f"Error processing page {page}: {e}")
        finally:
            await client.close()


if __name__ == "__main__":
    asyncio.run(ingest_data())
