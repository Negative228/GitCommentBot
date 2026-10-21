from celery import Celery
import os, json
from datetime import datetime

celery_app = Celery(
    "gitcommentbot",
    broker=os.getenv("REDIS_URL", "redis://redis:6379/0"),
    backend=os.getenv("REDIS_URL", "redis://redis:6379/0"),
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  
    task_soft_time_limit=240,  
    worker_prefetch_multiplier=1,  #по 1 задаче за раз, больше не нужно
)


@celery_app.task(bind=True, max_retries=1, default_retry_delay=30) #rate_limit='10/m' #pydantic=True
def process_pull_request(self, payload: dict):
    try:
        action = payload.get("action")
        pr_number = payload.get("number")
        pr_title = payload.get("pull_request", {}).get("title")
        pr_url = payload.get("pull_request", {}).get("url")
        repo_full_name = payload.get("repository", {}).get("full_name")
        user = payload.get("sender", {}).get("login")
        
        print(f"\n{'='*60}")
        print(f"Обработка PR #{pr_number}: {pr_title}")
        print(f"Автор: {user}")
        print(f"Репозиторий: {repo_full_name}")
        print(f"Действие: {action}")
        print(f"URL: {pr_url}")
        print(f"{'='*60}\n")
        
        print("Имитируем бурную деятельность (5 секунд)...")
        import time
        time.sleep(5)
        
        print("PR обработан успешно!")
        
        return {
            "status": "success",
            "pr_number": pr_number,
            "processed_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        print(f"Ошибка при обработке PR: {e}")
        raise