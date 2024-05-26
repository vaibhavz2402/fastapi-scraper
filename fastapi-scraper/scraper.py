import requests
from bs4 import BeautifulSoup
from pydantic import ValidationError
import re
import urllib.request
from slugify import slugify

from constants import HOST, PORT
from products import Product
import time


class WebScraper:
    def __init__(self, base_url):
        self.base_url = base_url

    def scrape_page(self, page_num: int, attempt: int) -> list[object]:
        try:
            url = self.base_url + ("" if page_num < 1 else f'page/{page_num + 1}/')
            response = requests.get(url)
            try:
                response.raise_for_status()  # Raise an exception for non-200 response codes
            except requests.exceptions.HTTPError as err:
                print(f"Failed to fetch the webpage: {err}")
                return self._handle_retry(page_num, attempt)

            soup = BeautifulSoup(response.content, 'html.parser')
            scraped_products = soup.find("ul", {"class": "products columns-4"})

            # Handling case when page is loaded but 404 banner is shown instead of products
            if not scraped_products:
                return self._handle_retry(page_num, attempt)

            return self._extract_products(page_num, scraped_products)

        except Exception as err:
            print(err, f"Skipping the scrape of page {page_num}")
            return []

    def _handle_retry(self, page_num: int, attempt: int) -> list[object]:
        if attempt < 2:
            print("Retrying after 5 seconds")
            time.sleep(5)
            return self.scrape_page(page_num, attempt + 1)

        raise Exception("Page Not Serviceable.")

    def _extract_products(self, page_num: int, scraped_products: BeautifulSoup) -> list[object]:
        products = []
        for li in scraped_products.find_all("li", {"class": ["product"]}):
            price_data = li.find("span", {"class": "woocommerce-Price-amount amount"})
            price = None
            if price_data:
                price = float(price_data.get_text()[1:])

            image_attribute = li.find("div", {"class": "mf-product-thumbnail"})
            image_src = image_attribute.a.img.get("data-lazy-src", None) if image_attribute else None
            image_alt = image_attribute.a.img.get("alt", None) if image_attribute else None

            # Since title does not contain full name, utilising alt name, as it has full name of the product.
            # Added fall back on title if img_alt is not present
            name = image_alt if image_alt else li.find("h2", {"class": "woo-loop-product__title"}).get_text()

            file_name = slugify(image_src.split("/")[-1].split(".")[0]) + ".jpg"
            urllib.request.urlretrieve(image_src, "./data/images/" + file_name)

            try:
                product_data = {
                    "image": f"{HOST}:{PORT}/images/{file_name}",
                    "name": re.sub(r'\s*-\s*Dentalstall\s*India$', '', name).strip(),
                    "price": price,
                    "page": page_num
                }
                product_model = Product(**product_data)
                products.append(product_model.dict())
            except ValidationError as err:
                # Skipping addition of products, in case validation is failed.
                print(f"Skipped inserting product due to ValidationError: {err}")

        return products
