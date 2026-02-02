import os
from dotenv import load_dotenv

from redis import Redis
from rq import Queue
from rq.worker import SimpleWorker

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL")
if REDIS_URL:
    redis_conn = Redis.from_url(REDIS_URL)
else:
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
    redis_conn = Redis(host=REDIS_HOST, port=REDIS_PORT)

audio_queue = Queue("audio-orders", connection=redis_conn)

if __name__ == "__main__":
    worker = SimpleWorker([audio_queue], connection=redis_conn)
    worker.work()
