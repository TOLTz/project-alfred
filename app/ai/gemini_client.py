import os
from dotenv import load_dotenv

from google import genai

load_dotenv()


def _get_api_key() -> str:
    key = os.getenv("GEMINI_API_KEY", "").strip()
    if key:
        return key
    key_test = os.getenv("GEMINI_API_KEY_TEST", "").strip()
    if key_test:
        return key_test
    raise RuntimeError("GEMINI_API_KEY não encontrado. Verifique seu .env.")


def _get_model() -> str:
    return os.getenv("GEMINI_MODEL", "gemini-3-flash-preview")


def _get_client() -> genai.Client:
    return genai.Client(api_key=_get_api_key())


def transcribe_and_parse_order(audio_bytes: bytes, mime_type: str, menu: list):
    client = _get_client()
    model = _get_model()

    prompt = f"""
Você é um atendente de restaurante.
1) Transcreva o áudio do cliente.
2) Normalize o pedido usando o cardápio e aliases.
3) Retorne um JSON com:
- transcript (string)
- items: lista de {{ item_id, name, quantity, notes(optional) }}

Cardápio (JSON):
{menu}

Regras:
- Use aliases para mapear itens iguais.
- quantity default = 1.
- notes só se houver observação.
Retorne SOMENTE JSON válido. Sem texto extra, sem markdown.
""".strip()

    resp = client.models.generate_content(
        model=model,
        contents=[
            {"role": "user", "parts": [{"text": prompt}]},
            {"role": "user", "parts": [{"inline_data": {"mime_type": mime_type, "data": audio_bytes}}]},
        ],
    )

    import json

    raw = (resp.text or "").strip()

    if not raw:
        raise RuntimeError("Gemini retornou resposta vazia (resp.text vazio).")

    # remove possíveis cercas de markdown ```json ... ```
    if raw.startswith("```"):
        raw = raw.strip("`").strip()
        if raw.lower().startswith("json"):
            raw = raw[4:].strip()

    # tenta parse direto
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # tenta extrair o primeiro bloco JSON dentro do texto
        start = raw.find("{")
        end = raw.rfind("}")
        if start != -1 and end != -1 and end > start:
            candidate = raw[start:end + 1]
            return json.loads(candidate)

        # se não deu, joga erro com preview pra debug
        preview = raw[:400]
        raise RuntimeError(f"Resposta do Gemini não é JSON válido. Preview: {preview}")
