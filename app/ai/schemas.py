from typing import List, Optional
from pydantic import BaseModel, Field


class OrderItem(BaseModel):
    item_id: str = Field(
        description="ID canônico do item (ex: QUEIJO_QUENTE)"
    )
    name: str = Field(
        description="Nome canônico do item (ex: Queijo quente)"
    )
    quantity: int = Field(
        default=1,
        description="Quantidade inferida do pedido"
    )
    notes: Optional[str] = Field(
        default=None,
        description="Observações do pedido (ex: sem cebola)"
    )
    confidence: float = Field(
        description="Confiança do match do item (0 a 1)"
    )


class AudioOrderResult(BaseModel):
    raw_transcript: str = Field(
        description="Transcrição literal do áudio"
    )
    clean_transcript: str = Field(
        description="Transcrição limpa, sem muletas"
    )
    intent: str = Field(
        description="order | call_waiter | unknown"
    )
    items: List[OrderItem] = Field(
        default_factory=list
    )
    unmatched: List[str] = Field(
        default_factory=list,
        description="Trechos não reconhecidos no cardápio"
    )
    overall_confidence: float = Field(
        description="Confiança geral do entendimento (0 a 1)"
    )