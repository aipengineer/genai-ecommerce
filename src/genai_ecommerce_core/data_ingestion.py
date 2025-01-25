import asyncio
from contextlib import asynccontextmanager

from sqlalchemy.orm import Session

from genai_ecommerce_core.client import AboutYouClient, download_image_with_retries
from genai_ecommerce_core.database import bulk_insert_products, init_db


@asynccontextmanager
async def get_db():
    db = await init_db("sqlite:///ecommerce.db")
    try:
        yield db
    finally:
        db.close()


async def ingest_data():
    async with get_db() as db:
        client = AboutYouClient()
        page = 1

        while True:
            try:
                print(f"Fetching page {page}...")
                response = await client.get_products(limit=100, page=page)
                if not response.entities:
                    print("No more products to process. Exiting.")
                    break

                products = []
                for product in response.entities:
                    if not product.get("categories") or not product["categories"][0]:
                        print(
                            f"Skipping product {product['id']} due to missing categories."
                        )
                        continue

                    product_data = {
                        "id": product["id"],
                        "name": product["name"],
                        "description": product.get("description"),
                        "price": product["priceRange"]["min"]["withTax"] / 100.0,
                        "category": product["categories"][0][0][
                            "categorySlug"
                        ],  # Use the first slug
                    }
                    products.append(product_data)

                    # Download images
                    if product.get("images"):
                        for image in product["images"]:
                            image_url = f"https://cdn.aboutyou.com/{image['hash']}"
                            local_image_path = f"data/images/{product_data['category']}/{image['hash'].split('/')[-1]}"
                            if not os.path.exists(local_image_path):
                                await download_image_with_retries(
                                    image_url, local_image_path
                                )
                            else:
                                print(f"Image already exists: {local_image_path}")

                bulk_insert_products(db, products)
                print(f"Page {page}: Inserted {len(products)} products.")
                page += 1

            except Exception as e:
                print(f"Error processing page {page}: {e}")
                break


if __name__ == "__main__":
    asyncio.run(ingest_data())
