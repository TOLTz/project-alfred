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

# Rodar front
```
cd front
python -m http.server 5173
```


# Rodar script para qrCode
```
$env:BASE_FRONT_URL="url" q vai ser do front 
$env:MESA_START="1"
$env:MESA_END="30"
python scripts/generate_qrcode.py
```