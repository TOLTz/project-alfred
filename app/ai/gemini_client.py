import os
from typing import List, Dict, Any

from google import genai
from google.genai import types

from app.ai.schemas import AudioOrderResult


def _get_client() -> genai.Client:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY não encontrado. Verifique seu .env.")
    return genai.Client(api_key=api_key)


def _build_prompt(menu: List[Dict[str, Any]]) -> str:
    return f"""
Você é um sistema de pedidos de restaurante.

Tarefas:
1) Transcrever o áudio em pt-BR (raw_transcript) com máxima fidelidade.
2) Gerar uma versão limpa (clean_transcript), removendo muletas: "ah", "hum", "é..." e frases como
   "eu quero", "pra mim", "por favor".
3) Interpretar o pedido e mapear para itens do cardápio canônico abaixo.
4) Se algo não casar com o cardápio, colocar em 'unmatched' (lista de strings).
5) Retornar SOMENTE JSON válido seguindo o schema.

Cardápio canônico (use como fonte de verdade para item_id e name; aliases ajudam a reconhecer variações):
{menu}

Regras:
- "queijo quente", "pão com queijo", "queixo quente" devem virar o MESMO item se existir no cardápio.
- Quantidades: detectar "um/uma", "dois/duas", "3", etc. Se não houver, quantity=1.
- Observações: "sem X", "com X", "bem passado", "com gelo" → notes.
- intent:
  - "order" se houver pedido de comida/bebida
  - "call_waiter" se pedir garçom/ajuda/atendimento
  - "unknown" se não der para entender
"""


def transcribe_and_parse_order(
    audio_bytes: bytes,
    mime_type: str,
    menu: List[Dict[str, Any]],
    model: str = "gemini-3-flash-preview",
) -> AudioOrderResult:
    """
    mime_type exemplos: audio/wav, audio/mp3, audio/ogg, audio/flac, audio/aac
    """
    client = _get_client()
    prompt = _build_prompt(menu)

    resp = client.models.generate_content(
        model=model,
        contents=[
            types.Part.from_bytes(data=audio_bytes, mime_type=mime_type),
            prompt,
        ],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=AudioOrderResult,
        ),
    )

    return AudioOrderResult.model_validate_json(resp.text)
