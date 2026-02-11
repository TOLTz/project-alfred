from dotenv import load_dotenv
from typing import Dict, Any, List

from app.ai.gemini_client import transcribe_and_parse_order

load_dotenv()


def process_audio_job(
    audio_bytes: bytes,
    mime_type: str,
    menu: List[Dict[str, Any]],
) -> Dict[str, Any]:
    result = transcribe_and_parse_order(
        audio_bytes=audio_bytes,
        mime_type=mime_type,
        menu=menu,
    )

    # Garante estrutura
    items = result.get("items") or []

    # 1️⃣ Junta observações que vierem dentro dos itens (notes)
    notes_lines = []
    for it in items:
        note = (it.get("notes") or "").strip()
        name = (it.get("name") or it.get("item_id") or "Item").strip()
        if note:
            notes_lines.append(f"- {name}: {note}")

    # 2️⃣ Normaliza observations (pode vir string, lista ou vazio)
    obs = result.get("observations")

    if isinstance(obs, list):
        obs_text = "\n".join(
            [str(x).strip() for x in obs if str(x).strip()]
        )
    elif isinstance(obs, str):
        obs_text = obs.strip()
    else:
        obs_text = ""

    # 3️⃣ Se não veio observation explícita, usa as notes dos itens
    if not obs_text and notes_lines:
        obs_text = "\n".join(notes_lines)

    # 4️⃣ Garante SEMPRE string (front agradece)
    result["observations"] = obs_text

    return result
