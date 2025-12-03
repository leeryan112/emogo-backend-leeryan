from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
import os

app = FastAPI()

# =====================================================
#   MongoDB (Motor) Connection - ASYNC
# =====================================================
MONGODB_URI = os.getenv("MONGODB_URI")  # 在 Render 中設定
DB_NAME = "emogo"

@app.on_event("startup")
async def startup_db_client():
    app.mongodb_client = AsyncIOMotorClient(MONGODB_URI)
    app.mongodb = app.mongodb_client[DB_NAME]

@app.on_event("shutdown")
async def shutdown_db_client():
    app.mongodb_client.close()

# =====================================================
#   CORS（前端 fetch 必須）
# =====================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================================================
#   Data Models
# =====================================================
class Vlog(BaseModel):
    user_id: str
    video_url: str
    timestamp: float

class Sentiment(BaseModel):
    user_id: str
    text: str
    timestamp: float

class GPS(BaseModel):
    user_id: str
    lat: float
    lng: float
    timestamp: float

# =====================================================
#   POST endpoints (Async)
# =====================================================
@app.post("/vlogs")
async def upload_vlog(data: Vlog):
    record = data.dict()
    record["server_received_at"] = datetime.utcnow()
    await app.mongodb["vlogs"].insert_one(record)
    return {"status": "ok", "stored": record}

@app.post("/sentiments")
async def upload_sentiment(data: Sentiment):
    record = data.dict()
    record["server_received_at"] = datetime.utcnow()
    await app.mongodb["sentiments"].insert_one(record)
    return {"status": "ok", "stored": record}

@app.post("/gps")
async def upload_gps(data: GPS):
    record = data.dict()
    record["server_received_at"] = datetime.utcnow()
    await app.mongodb["gps"].insert_one(record)
    return {"status": "ok", "stored": record}

# =====================================================
#   Export HTML Page
# =====================================================
templates = Jinja2Templates(directory="templates")

@app.get("/export", response_class=HTMLResponse)
async def export_dashboard(request: Request):
    vlogs = await app.mongodb["vlogs"].find().to_list(None)
    sentiments = await app.mongodb["sentiments"].find().to_list(None)
    gps = await app.mongodb["gps"].find().to_list(None)

    return templates.TemplateResponse(
        "export.html",
        {
            "request": request,
            "vlogs": vlogs,
            "sentiments": sentiments,
            "gps": gps,
        }
    )

# =====================================================
#   Debug route (test MongoDB connection)
# =====================================================
@app.get("/export-debug")
async def export_debug():
    vlogs_raw = await app.mongodb["vlogs"].find().to_list(5)
    sentiments_raw = await app.mongodb["sentiments"].find().to_list(5)
    gps_raw = await app.mongodb["gps"].find().to_list(5)

    def convert_id(docs):
        out = []
        for d in docs:
            d = dict(d)
            if "_id" in d:
                d["_id"] = str(d["_id"])
            out.append(d)
        return out

    return {
        "vlogs": convert_id(vlogs_raw),
        "sentiments": convert_id(sentiments_raw),
        "gps": convert_id(gps_raw),
    }

# =====================================================
#   Test Root
# =====================================================
@app.get("/")
async def root():
    return {"message": "EmoGo backend running", "export_page": "/export"}
