import hmac, hashlib, os

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
    
    print(f"\n{'='*50}")
    print(f"Event: {x_github_event}")
    print(f"Action: {payload.get('action')}")
    print(f"User: {payload.get('sender', {}).get('login')}")
    print(f"Repo: {payload.get('repository', {}).get('full_name')}")
    print(f"{'='*50}\n")
    
    return {"status": "received"}

@router.get("/ok")
async def ok():
    return {"status": "ok"}