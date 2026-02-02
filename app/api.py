import os
import time
import uuid
import json
from dotenv import load_dotenv

from fastapi import FastAPI, UploadFile, File, Body, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

from redis import Redis
from rq import Queue
from rq.job import Job

from app.jobs import process_audio_job
from app.db import init_db, SessionLocal, Order
from app.menu_seed import ensure_menu_seeded
from app.menu_repo import get_menu_as_list



load_dotenv()

app = FastAPI()

CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://127.0.0.1:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in CORS_ORIGINS if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()
ensure_menu_seeded()



REDIS_URL = os.getenv("REDIS_URL")
if REDIS_URL:
    redis_conn = Redis.from_url(REDIS_URL)
else:
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
    redis_conn = Redis(host=REDIS_HOST, port=REDIS_PORT)

audio_queue = Queue("audio-orders", connection=redis_conn)


@app.post("/audio")
async def receive_audio(file: UploadFile = File(...)):
    audio_bytes = await file.read()

    menu = get_menu_as_list()


    job = audio_queue.enqueue(
        process_audio_job,
        audio_bytes,
        file.content_type,
        menu,
        job_timeout=180,
    )

    return {"job_id": job.id, "status": "queued"}


@app.get("/jobs/{job_id}")
def get_job(job_id: str):
    job = Job.fetch(job_id, connection=redis_conn)

    if job.is_finished:
        return {"job_id": job.id, "status": "finished", "result": job.result}

    if job.is_failed:
        return {"job_id": job.id, "status": "failed"}

    return {"job_id": job.id, "status": job.get_status()}


@app.get("/events/{job_id}")
def job_events(job_id: str):
    def event_stream():
        while True:
            job = Job.fetch(job_id, connection=redis_conn)

            if job.is_finished:
                yield f"data: {json.dumps(job.result, ensure_ascii=False)}\n\n"
                break

            if job.is_failed:
                yield 'data: {"status":"failed"}\n\n'
                break

            time.sleep(1)

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@app.post("/orders/confirm")
def confirm_order(payload: dict = Body(...)):
    job_id = payload.get("job_id")
    order_obj = payload.get("order")

    if not job_id or not order_obj:
        raise HTTPException(status_code=400, detail="job_id e order são obrigatórios")

    order_id = str(uuid.uuid4())

    db = SessionLocal()
    try:
        row = Order(
            id=order_id,
            created_at=time.time(),
            status="pending",
            job_id=job_id,
            order_json=json.dumps(order_obj, ensure_ascii=False),
        )
        db.add(row)
        db.commit()
        return {"order_id": order_id, "status": "pending"}
    finally:
        db.close()


@app.get("/orders")
def list_orders():
    db = SessionLocal()
    try:
        rows = db.query(Order).order_by(Order.created_at.desc()).all()
        return [
            {
                "id": r.id,
                "created_at": r.created_at,
                "status": r.status,
                "job_id": r.job_id,
                "order": json.loads(r.order_json),
            }
            for r in rows
        ]
    finally:
        db.close()


@app.post("/orders/{order_id}/delivered")
def mark_order_delivered(order_id: str):
    db = SessionLocal()
    try:
        row = db.query(Order).filter(Order.id == order_id).first()
        if not row:
            raise HTTPException(status_code=404, detail="order_id não encontrado")

        row.status = "delivered"
        db.commit()
        return {"order_id": row.id, "status": row.status}
    finally:
        db.close()
