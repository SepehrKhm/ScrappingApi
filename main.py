from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from celery import group
from celery_app import celery_app,fetch_and_scrape

app = FastAPI()

class ScrapeRequest(BaseModel):
    urls: List[str]
    sample: str

@app.post("/scrape")
async def scrape_data(request: ScrapeRequest):
    task_group = group(fetch_and_scrape.s(url, request.sample) for url in request.urls)
    task_result = task_group.apply_async()

    return {"message": "Scraping tasks have been dispatched.", "task_id": task_result.id}

@app.get("/scrape/results/{task_id}")
async def get_scrape_results(task_id: str):
    result = fetch_and_scrape.AsyncResult(task_id)
    
    if result.state == 'PENDING':
        return {"state": result.state, "status": "The task is still in progress."}
    elif result.state == 'SUCCESS':
        return {"state": result.state, "result": result.result}
    elif result.state == 'FAILURE':
        return {"state": result.state, "error": str(result.info)}
    else:
        return {"state": result.state, "status": "Unknown state."}
