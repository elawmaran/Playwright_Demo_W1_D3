
from fastapi import FastAPI

# Create the FastAPI application
app = FastAPI()


# Home endpoint
@app.get("/")
async def root():
    return {"message": "Hello World"}


# Get item by ID, with an optional query parameter
@app.get("/items/{item_id}")
async def read_item(item_id: int, q: str | None = None):
    return {
        "item_id": item_id,
        "q": q
    }
