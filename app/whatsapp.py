import os
import random
import asyncio
import httpx

async def send_whatsapp_message(text: str):

    api_url = os.getenv("WHATSAPP_API_URL")
    token = os.getenv("WHATSAPP_CLIENT_TOKEN")
    phone = os.getenv("WHATSAPP_PHONE")

    print("[WA] env ok?", {
        "api_url": bool(api_url),
        "token": bool(token),
        "phone": bool(phone),
        "phone_value": phone,
    })

    if not api_url or not token or not phone:
        print("[WA] abortando: env faltando ❌")
        return

    delay = random.uniform(4, 8)
    print(f"[WA] delayTyping: {delay:.2f}s")
    await asyncio.sleep(delay)

    # ⚠️ ajuste conforme sua API real
    url = f"{api_url.rstrip('/')}"
    headers = {
        "Content-Type": "application/json",
        "Client-Token": token,     # pode ser Authorization: Bearer ...
    }
    payload = {
        "phone": phone,            # pode precisar de +55..., ou só 55..., depende do provider
        "message": text,           # pode ser "text" em vez de "message"
    }

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.post(url, json=payload, headers=headers)
            r.raise_for_status()
    except Exception as e:
        print("[WA] ERRO ao enviar ❌", repr(e))




def format_order_text(order_obj: dict, mesa_id: str, order_id: str, customer_text: str = "") -> str:
    items = order_obj.get("items") or []
    transcript = (order_obj.get("transcript") or "").strip()

    mesa = f"Mesa {mesa_id}" if mesa_id and mesa_id != "—" else "Mesa —"

    lines = [
        f"🧾 *NOVO PEDIDO* — {mesa}",
        f"🆔 {order_id}",
        "",
        "*Itens:*",
    ]

    if items:
        for it in items:
            name = it.get("name") or it.get("item_id") or "Item"
            qty = int(it.get("quantity") or 1)
            lines.append(f"• {qty}x {name}")
    else:
        lines.append("• (nenhum item identificado)")

    if transcript:
        lines += ["", "*Transcrição:*", transcript]

    if customer_text.strip():
        lines += ["", "*Comanda editada:*", customer_text.strip()]

    return "\n".join(lines)
