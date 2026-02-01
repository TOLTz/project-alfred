from typing import Dict, Any, List

from app.ai.gemini_client import transcribe_and_parse_order
from dotenv import load_dotenv
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
    return result.model_dump()
