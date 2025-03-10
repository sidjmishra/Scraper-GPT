from fastapi import FastAPI
from pydantic import BaseModel
import asyncio

from scraper_bot.scraper import scrape_website

app = FastAPI()

class ScraperModel(BaseModel):
    url: str
    max_pages: int

@app.post("/api/scrape_web")
async def process_data(payload: ScraperModel):
    try:
        data = payload.model_dump()
        result = await scrape_website(data["url"], data["max_pages"])
        
        if not result:
            return {"success": False, "detail": "No data found for the web url"}

        return {"success": True, "detail": result}
    except Exception as e:
        print(f"Error Scrapping: {str(e)}")
        return {"success": False, "detail": "Error while scrapping web"}
