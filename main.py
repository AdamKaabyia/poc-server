from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import random
import os
from dotenv import load_dotenv
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pymongo.errors import PyMongoError

# Load environment variables
load_dotenv()

app = FastAPI()

# MongoDB setup
MONGODB_URI = os.getenv('MONGODB_URI')
client = MongoClient(MONGODB_URI, server_api=ServerApi('1'))

try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)
    raise HTTPException(status_code=500, detail=f"MongoDB connection error: {str(e)}")

db = client['telegram']
collection = db['telegram_test']
log_collection = db['interaction_logs']  # New collection for logging interactions


class Info(BaseModel):
    info: str


class InteractionLog(BaseModel):
    user_query: str
    bot_response: str


@app.post("/generate")
async def generate_number():
    number = random.randint(0, 1000)
    try:
        collection.insert_one({"number": number})
        return {"message": "Number generated and stored successfully", "number": number}
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@app.post("/store")
async def store_info(info: Info):
    try:
        collection.insert_one({"info": info.info})
        return {"message": "Information stored successfully"}
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@app.post("/log_interaction")
async def log_interaction(log: InteractionLog):
    try:
        log_collection.insert_one(log.dict())
        return {"message": "Interaction logged successfully"}
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while logging interaction: {str(e)}")


@app.get("/health")
async def health_check():
    try:
        # Check if the database is accessible
        db.command("ping")
        return {"message": "MongoDB connection is healthy"}
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"MongoDB connection error: {str(e)}")


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
