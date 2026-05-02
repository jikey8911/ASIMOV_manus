from fastapi import FastAPI
import uvicorn
import redis
import asyncpg

app = FastAPI(title="ASIMOV Backend")

@app.get("/")
def read_root():
    return {"message": "ASIMOV Backend is running"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
