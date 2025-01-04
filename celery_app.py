from celery import Celery, shared_task
import httpx
from bs4 import BeautifulSoup

celery_app = Celery(
    'my_celery_app',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0'
)

celery_app.conf.update(result_expires=3600)

TIMEOUT = 30

@shared_task(name="tasks.fetch_and_scrape")
def fetch_and_scrape(url, sample):
    try:
        response = httpx.get(url, timeout=TIMEOUT)
        response.raise_for_status()
    except httpx.RequestError as e:
        return {"url": url, "error": f"Error fetching URL: {str(e)}"}

    soup = BeautifulSoup(response.text, "html.parser")
    elements = soup.select(sample)

    if not elements:
        return {"url": url, "error": "No data found matching the given sample."}

    extracted_data = ", ".join([element.get_text(strip=True) for element in elements])
    return {"url": url, "data_count": len(elements), "extracted_data": extracted_data}