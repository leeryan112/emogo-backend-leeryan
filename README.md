[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/e7FBMwSa)
[![Open in Visual Studio Code](https://classroom.github.com/assets/open-in-vscode-2e0aaae1b6195c2367325f4f02e2d04e9abb55f0b24a779b69b11b9e10269abc.svg)](https://classroom.github.com/online_ide?assignment_repo_id=21925326&assignment_repo_type=AssignmentRepo)

# EmoGo Backend (FastAPI + MongoDB on Render)

This repo contains my EmoGo backend, deployed on a public server using **FastAPI** and **MongoDB Atlas (Motor, async driver)**.

The backend provides three POST endpoints for data collection from the EmoGo frontend (vlogs, sentiments, GPS) and one HTML dashboard page for exporting / viewing all collected data.

---

## 🔗 Live Backend URLs

- Base URL (Render):

  **`https://emogo-backend-leeryan.onrender.com`**

- Interactive API docs (Swagger UI):

  **`https://emogo-backend-leeryan.onrender.com/docs`**

- 📥 **Data export / download HTML page (required by assignment):**

  👉 **`https://emogo-backend-leeryan.onrender.com/export`**

  TAs & Tren can open this URL in a browser to see all three types of data (vlogs, sentiments, GPS) in one HTML dashboard page and download them if needed.

---

## 📡 API Endpoints

### 1. Upload Vlog

- **Method:** `POST`
- **Path:** `/vlogs`
- **Request body (JSON):**

  ```json
  {
    "user_id": "string",
    "video_url": "string",
    "timestamp": 1733200000
  }
  ```

- **Description:**  
  Stores vlog metadata into the `vlogs` collection.

---

### 2. Upload Sentiment

- **Method:** `POST`
- **Path:** `/sentiments`
- **Request body (JSON):**

  ```json
  {
    "user_id": "string",
    "text": "string",
    "timestamp": 1733200100
  }
  ```

- **Description:**  
  Stores a sentiment record (text diary / mood) into the `sentiments` collection.

---

### 3. Upload GPS

- **Method:** `POST`
- **Path:** `/gps`
- **Request body (JSON):**

  ```json
  {
    "user_id": "string",
    "lat": 25.033,
    "lng": 121.565,
    "timestamp": 1733200200
  }
  ```

- **Description:**  
  Stores GPS coordinates into the `gps` collection.

---

## 💾 MongoDB Setup

- **MongoDB:** Atlas cluster
- **Driver:** [`motor`](https://motor.readthedocs.io/) (async MongoDB driver for Python)
- **Database name:** `emogo`
- **Collections:**
  - `vlogs`
  - `sentiments`
  - `gps`

The connection string is provided to the backend via the environment variable:

- `MONGODB_URI`

Example (not hard-coded in the repo):

```text
mongodb+srv://<username>:<password>@ntuprogram.3ocjemu.mongodb.net/
```

---

## 🚀 Deployment on Render

This backend is deployed as a **Render Web Service**.

- **Runtime:** Python 3
- **Build command:**

  ```bash
  pip install -r requirements.txt
  ```

- **Start command:**

  ```bash
  uvicorn main:app --host 0.0.0.0 --port $PORT
  ```

The service reads `MONGODB_URI` from Render's Environment Variables and connects to the Atlas cluster on startup.