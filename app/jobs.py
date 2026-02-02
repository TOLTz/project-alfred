from dotenv import load_dotenv
load_dotenv()

from typing import Dict, Any, List
from app.ai.gemini_client import transcribe_and_parse_order


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

    # Se gemini_client já retorna dict, retorna direto
    return result
