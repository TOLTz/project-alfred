import time
import uuid
import json

from fastapi.responses import StreamingResponse
from fastapi import Body, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, UploadFile, File

from app.db import init_db, SessionLocal, Order
from app.jobs import process_audio_job

from dotenv import load_dotenv

from redis import Redis

from rq import Queue
from rq.job import Job


load_dotenv()

app = FastAPI()
init_db()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



redis_conn = Redis(host="localhost", port=6379)
audio_queue = Queue("audio-orders", connection=redis_conn)


@app.post("/audio")
async def receive_audio(file: UploadFile = File(...)):
    audio_bytes = await file.read()

    menu = [
        {
            "item_id": "QUEIJO_QUENTE",
            "name": "Queijo quente",
            "aliases": ["pao com queijo", "pão com queijo", "queixo quente", "queijo quenti", "pão com quero"],
        },
        {
            "item_id": "COCA_ZERO_LATA",
            "name": "Coca-Cola Zero (lata)",
            "aliases": ["coca zero", "coca cola zero", "coca 0", "coca zero lata"],
        },
        {
            "item_id": "COXINHA_FRANGO",
            "name": "Coxinha de Frango",
            "aliases": ["coxinha", "coxina", "coxinha de frango com catupiry", "salgado de frango"],
        },
        {
            "item_id": "PAO_DE_QUEIJO_UN",
            "name": "Pão de Queijo",
            "aliases": ["pao de queijo", "pãozinho de queijo", "pao de keijo", "pdq"],
        },
        {
            "item_id": "SUCO_LARANJA_500",
            "name": "Suco de Laranja (500ml)",
            "aliases": ["suco de laranja", "suco natural", "laranja natural", "suco de laranxa"],
        },
        {
            "item_id": "HAMBURGUER_ARTESANAL",
            "name": "Hambúrguer Artesanal",
            "aliases": ["burguer", "hamburgue", "X-burguer", "cheeseburguer", "lanche"],
        },
        {
            "item_id": "BATATA_FRITA_M",
            "name": "Batata Frita (Média)",
            "aliases": ["batata", "fritas", "porção de batata", "batata frita media"],
        },
        {
            "item_id": "MISTO_QUENTE",
            "name": "Misto Quente",
            "aliases": ["misto", "pão com presunto e queijo", "misto quente caprichado"],
        },
        {
            "item_id": "ESFIHA_CARNE",
            "name": "Esfiha de Carne",
            "aliases": ["esfiha", "esfirra", "esfirra de carne", "salgado de carne"],
        },
        {
            "item_id": "CAFE_EXPRESSO",
            "name": "Café Expresso",
            "aliases": ["cafe", "cafézinho", "expresso", "cafezinho", "café preto"],
        },
        {
            "item_id": "AGUA_MINERAL_S_GAS",
            "name": "Água Mineral Sem Gás",
            "aliases": ["agua", "água", "agua sem gas", "garrafa de agua"],
        },
        {
            "item_id": "AGUA_MINERAL_C_GAS",
            "name": "Água Mineral Com Gás",
            "aliases": ["agua com gas", "água com gás", "agua gaseificada"],
        },
        {
            "item_id": "BOLO_CENOURA_FATIA",
            "name": "Bolo de Cenoura (fatia)",
            "aliases": ["bolo de cenoura", "bolo com cobertura de chocolate", "fatia de bolo"],
        },
        {
            "item_id": "CERVEJA_LATA",
            "name": "Cerveja (lata)",
            "aliases": ["cerveja", "breja", "gelada", "latinha"],
        },
        {
            "item_id": "BRIGADEIRO_UN",
            "name": "Brigadeiro Gourmet",
            "aliases": ["doce", "brigadeiro", "neguinho", "docinho"],
        },
        {
            "item_id": "ACAI_TIGELA_500",
            "name": "Açaí na Tigela (500ml)",
            "aliases": ["acai", "açaí", "assai", "tigela de açaí"],
        },
        {
            "item_id": "SANDUICHE_NATURAL",
            "name": "Sanduíche Natural de Frango",
            "aliases": ["sanduiche leve", "lanche natural", "sanduiche de frango"],
        },
        {
            "item_id": "CAPUCCINO_G",
            "name": "Capuccino Grande",
            "aliases": ["capuccino", "capuchino", "café com leite e chocolate"],
        },
        {
            "item_id": "PAO_NA_CHAPA",
            "name": "Pão na Chapa",
            "aliases": ["pao com manteiga", "pão na chapa", "paozinho na chapa"],
        },
        {
            "item_id": "SUCO_DETOX",
            "name": "Suco Detox (Verde)",
            "aliases": ["suco verde", "detox", "suco de couve"],
        },
        {
            "item_id": "TORTA_FRANGO_FATIA",
            "name": "Torta de Frango",
            "aliases": ["fatia de torta", "torta salgada", "torta de frango"],
        },
        {
            "item_id": "CROISSANT_MANTEIGA",
            "name": "Croissant de Manteiga",
            "aliases": ["croassant", "croisat", "pão folhado"],
        },
    ]

    job = audio_queue.enqueue(
        process_audio_job,
        audio_bytes,
        file.content_type,
        menu,
        job_timeout=120,
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
    """
    Espera:
    {
      "job_id": "...",
      "order": { ...json retornado pela IA... }
    }
    """
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
