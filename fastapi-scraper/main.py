import json

import redis
from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.staticfiles import StaticFiles

from auth import authenticate_token
from constants import HOST, PORT
from scraper import WebScraper
from typing import List, Optional
from datastorage import DataStorage
from products import Product
from config.db import pool

app = FastAPI()

app.mount("/images", StaticFiles(directory="./data/images"), name="images")


def get_redis():
    return redis.Redis(connection_pool=pool)


@app.get("/")
async def root():
    return {"message": "Welcome to the FastAPI Web Scraper"}


@app.get("/scrape", response_model=List[Product])
async def scrape_page(authenticated: bool = Depends(authenticate_token),
                      offset_page: Optional[int] = Query(0, description="Page number to start scraping scrape"),
                      limit: Optional[int] = Query(5, description="Limit for scraping number of pages"),
                      cache=Depends(get_redis)):
    """
     This endpoint will scrape data from the page numbers provided in the parameters.
     After scraping all the products will be added to the database (json file)
    """
    try:
        url = "https://dentalstall.com/shop/"
        scraper = WebScraper(url)

        print("Starting scraper...")

        allProducts = []
        for i in range(offset_page, offset_page + limit):
            products = scraper.scrape_page(i, 0)
            if products:
                allProducts.extend(products)

        print("Scraped", len(allProducts), "products from page", offset_page, "to", offset_page + limit)

        # Save scraped data to JSON file
        insertedProductCount = await DataStorage().insert_data_to_json(allProducts, "data/database/scraped_data.json", cache)

        print("Inserted", insertedProductCount, "products in database")
        return allProducts

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/find-product-db", response_model=Product | None)
async def find_product_db(authenticated: bool = Depends(authenticate_token),
                          name: str = Query(..., description="Product name"),
                          cache=Depends(get_redis)):
    """
     This endpoint will find the product in the redis database based on product name
    """
    try:
        product = cache.get(name)
        if product:
            product = json.loads(product)

        return product

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=HOST, port=PORT)
