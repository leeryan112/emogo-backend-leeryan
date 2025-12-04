from fastapi import (
    FastAPI,
    Request,
    UploadFile,
    File,
    Form,
    HTTPException,
)
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from pathlib import Path
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
#   Data Models（sentiments / gps 還是用 JSON）
# =====================================================
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
#   上傳目錄設定（本地 uploads/ 資料夾）
# =====================================================
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# =====================================================
#   POST /vlogs 影片上傳（multipart/form-data）
# =====================================================
@app.post("/vlogs")
async def upload_vlog(
    user_id: str = Form(...),
    timestamp: float = Form(...),
    file: UploadFile = File(...),
):
    # 產生比較不會撞名的檔名
    safe_name = f"{int(datetime.utcnow().timestamp())}_{file.filename}"
    file_path = UPLOAD_DIR / safe_name

    # 寫檔到 uploads/
    with file_path.open("wb") as f:
        f.write(await file.read())

    video_url = f"/video/{safe_name}"

    record = {
        "user_id": user_id,
        "video_url": video_url,
        "timestamp": float(timestamp),
        "server_received_at": datetime.utcnow(),
    }
    await app.mongodb["vlogs"].insert_one(record)
    return {"status": "ok", "stored": record}

# =====================================================
#   提供影片檔案（GET /video/{filename}）
# =====================================================
@app.get("/video/{filename}")
async def get_video(filename: str):
    file_path = UPLOAD_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    # 讓瀏覽器可以串流播放
    return FileResponse(str(file_path))

# =====================================================
#   其它 POST endpoints (JSON)
# =====================================================
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
#   Root
# =====================================================
@app.get("/")
async def root():
    return {"message": "EmoGo backend running", "export_page": "/export"}
