
# Main application entry point
from fastapi import FastAPI

app = FastAPI(title="Beast Mode DevPost Integration")

@app.get("/")
async def root():
    return {"message": "Beast Mode DevPost Integration Demo"}

@app.get("/health")
async def health():
    return {"status": "healthy", "systematic": True}
