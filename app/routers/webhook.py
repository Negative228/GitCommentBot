import sys
sys.path.append("..")

import hmac, hashlib, os, json
from tasks import process_pull_request

GITHUB_WEBHOOK_SECRET = os.getenv('GITHUB_WEBHOOK_SECRET')

from fastapi import APIRouter, Request, HTTPException, Header

router = APIRouter(prefix="/webhook", tags=["Вебхук"])

def verify_signature(payload_body: bytes, signature: str) -> bool:
    if not signature:
        return False
    
    # GitHub шлет подпись в формате sha256=...
    if signature.startswith("sha256="):
        signature = signature[7:]
    
    expected = hmac.new(
        GITHUB_WEBHOOK_SECRET.encode("utf-8"),
        payload_body,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(expected, signature)


@router.post("/github")
async def receive_webhook(  request: Request,
                            x_hub_signature_256: str = Header(None),
                            x_github_event: str = Header(None), ):
    payload_body = await request.body()
    
    if not verify_signature(payload_body, x_hub_signature_256):
        raise HTTPException(status_code=403, detail="Invalid signature")
    
    try:
        payload = json.loads(payload_body)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON")
    
    action = payload.get("action")
    print(f"\n Получено событие: {x_github_event} | Action: {action}")
    
    # TEST TEST TEST
    if True: #x_github_event == "pull_request":
        task = process_pull_request.delay(payload)
        print(f"Задача отправлена в очередь. Task ID: {task.id}")
        return {"status": "received"}
    
    print(f"Событие {x_github_event} не обрабатывается")
    return {"status": "ignored", "detail": "event type not supported"}

@router.get("/ok")
async def ok():
    return {"status": "ok"}