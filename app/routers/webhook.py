import sys
sys.path.append("..")

import hmac, hashlib, os, json
from tasks import process_pull_request, process_push
from schemas import *
from database import SessionDep
from repository import EventsRepository

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

async def parse_webhook_payload(event_id:str, event_type: str, payload_dict: dict, session: SessionDep) -> SGitHubEvent:
    """
    Парсит payload в соответствующую Pydantic-модель на основе типа события.
    Возвращает базовый SGitHubEvent для неизвестных типов.
    """
    try:
        if event_type == "pull_request":
            payload = SPullRequestWebhook(**payload_dict)
        elif event_type == "push":
            payload = SPushWebhook(**payload_dict)
        elif event_type == "issues":
            payload = SIssuesWebhook(**payload_dict)
        elif event_type == "issue_comment":
            payload = SIssueCommentWebhook(**payload_dict)
        else:
            payload = SGitHubEvent(**payload_dict)
        
        await EventsRepository.add_one(event_id=event_id, event_type=event_type, data=payload, session=session)

        return payload
    except Exception as e:
        print(f"Ошибка валидации payload: {e}")
        raise HTTPException(status_code=422, detail=f"Invalid payload structure: {str(e)}")

def process_event(payload: SGitHubEvent, x_github_event: str = Header(None)):
    if x_github_event == "pull_request":
        task = process_pull_request.delay(payload.model_dump())
        print(f"Задача отправлена в очередь. Task ID: {task.id}")
        
        return {
            "status": "accepted",
            "task_id": task.id,
            "event_type": "pull",
            "message": "PR processing started"
        }
    
    elif x_github_event == "push":
        task = process_push.delay(payload.model_dump())
        print(f"Задача отправлена в очередь. Task ID: {task.id}")
        return {
            "status": "accepted",
            "task_id": task.id,
            "event_type": "push",
            "message": "Push processing started"
        }
    
    elif x_github_event == "issues":
        print(f"Issue #{payload.issue.number}: {payload.issue.title}")
        return {"status": "received", "event_type": "issues"}
    
    elif x_github_event == "issue_comment":
        print(f"Комментарий к Issue #{payload.issue.number}")
        return {"status": "received", "event_type": "issue_comment"}
    
    else:
        print(f"Событие {x_github_event} не обрабатывается")
        return {"status": "ignored", "reason": "event type not supported", "event_type": x_github_event}

@router.post("/github")
async def receive_webhook(  request: Request,
                            session: SessionDep, 
                            x_hub_signature_256: str = Header(None),
                            x_github_event: str = Header(None), 
                            x_github_delivery: str = Header(None) ):

    payload_body = await request.body()
    
    if not verify_signature(payload_body, x_hub_signature_256):
        raise HTTPException(status_code=403, detail="Invalid signature")
    
    try:
        payload = json.loads(payload_body)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON")
    
    validated_payload = await parse_webhook_payload(x_github_delivery, x_github_event, payload, session)

    # Временная печать информации
    print(f"\n{'='*60}")
    print(f"Получено событие: {x_github_event}")
    print(f"Action: {validated_payload.action}")
    print(f"User: {validated_payload.sender.login}")
    print(f"Repo: {validated_payload.repository.full_name}")
    if validated_payload.organization:
        print(f"Org: {validated_payload.organization.login}")
    
    print(f"{'='*60}\n")

    return process_event(validated_payload, x_github_event)

@router.get("/ok")
async def ok():
    return {"status": "ok"}