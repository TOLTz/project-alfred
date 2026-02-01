# Rodar o redis
```
docker run -d --name redis-audio -p 6379:6379 redis:7
```

# Se já existir

```
docker start redis-audio
```

# Subir Api
```
uvicorn app.api:app --reload
```

# Subir Worker
```
rq worker audio-orders --url redis://localhost:6379 --worker-class rq.worker.SimpleWorker
```