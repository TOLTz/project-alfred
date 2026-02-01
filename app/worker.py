from redis import Redis
from rq import Queue, Worker

# conexão Redis
redis_conn = Redis(host="localhost", port=6379)

# fila usada pela API
audio_queue = Queue("audio-orders", connection=redis_conn)

if __name__ == "__main__":
    print("Worker RQ iniciado (modo compatível com Windows)")
    worker = Worker(
        [audio_queue],
        connection=redis_conn,
        disable_job_desc_logging=True
    )
    worker.work()
