# fastapi-scraper


## Cmd to run the app
uvicorn main:app --reload


This app will scrap the pages provided in the scraper or it will take 5 as default.
After scraping the data, it will be stored in json file and new/updated values will be updated in cache.

/find-products-db api will only get data from redis only.
