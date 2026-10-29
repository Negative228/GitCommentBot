from celery import Celery
import os, json, time, httpx
from datetime import datetime
from schemas import *
from typing import Optional

GITHUB_WEBHOOK_SECRET = os.getenv('GITHUB_WEBHOOK_SECRET')
GITHUB_API   = "https://api.github.com"

def _gh_headers(accept: str = "application/vnd.github.v3+json") -> dict:
    h = {
        "Accept": accept,
        "User-Agent": "GitCommentBot/1.0",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if GITHUB_TOKEN:
        h["Authorization"] = f"Bearer {GITHUB_TOKEN}"
    return h


def fetch_compare_diff(repo_full_name: str, before: str, after: str) -> Optional[str]:
    """Unified diff между двумя SHA через Compare API."""
    if not before or set(before) == {"0"}:
        return None
    url = f"{GITHUB_API}/repos/{repo_full_name}/compare/{before}...{after}"
    with httpx.Client(timeout=60, follow_redirects=True) as client:
        resp = client.get(url, headers=_gh_headers("application/vnd.github.v3.diff"))
    if resp.status_code == 404:
        return None
    resp.raise_for_status()
    return resp.text


def fetch_pr_diff(repo_full_name: str, pr_number: int) -> Optional[str]:
    """Unified diff конкретного PR через Pulls API."""
    url = f"{GITHUB_API}/repos/{repo_full_name}/pulls/{pr_number}"
    with httpx.Client(timeout=60, follow_redirects=True) as client:
        resp = client.get(url, headers=_gh_headers("application/vnd.github.v3.diff"))
    if resp.status_code == 404:
        return None
    resp.raise_for_status()
    return resp.text


"""
def save_diff(repo_full_name: str, identifier: str, diff: str) -> str:
    
    safe_repo = repo_full_name.replace("/", "_")
    os.makedirs(DIFF_DIR, exist_ok=True)
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%S")
    path = os.path.join(DIFF_DIR, f"{safe_repo}_{identifier}_{ts}.diff")
    with open(path, "w", encoding="utf-8") as f:
        f.write(diff)
    return path
"""
################################################################################

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

@celery_app.task(bind=True, max_retries=1, default_retry_delay=30, pydantic=True, rate_limit='1/m') #rate_limit='10/m' #pydantic=True
def process_push(self, payload: SPushWebhook):
    try:
        repo_full_name =    payload.repository.full_name
        sender =            payload.sender.login
        ref =               payload.ref
        
        if payload.deleted:
            push_type = "Удаление ветки"
        elif payload.created:
            push_type = "Создание новой ветки"
        else:
            push_type = "Обычный пуш"

        print(f"\n{'='*60}")
        print(f"{push_type} в репозиторий: {repo_full_name}")
        print(f"Ветка: {ref}")
        print(f"Pusher: {payload.pusher.get('name', sender)} ({payload.pusher.get('email', 'N/A')})")
        print(f"Compare URL: {payload.compare}")
        
        diff_text: Optional[str] = None
        diff_path: Optional[str] = None

        if payload.deleted:
            print("Ветка удалена, коммиты отсутствуют.")
        elif not payload.commits:
            print("Dummy-пуш")
        else:
            # ... существующая статистика по файлам ...
            print("\nСкачиваем diff...")
            diff_text = fetch_compare_diff(repo_full_name, payload.before, payload.after)
            if diff_text:
                #diff_path = save_diff(repo_full_name, payload.after[:12], diff_text)
                print(f"Diff: {len(diff_text)}")
            else:
                print("Diff пуст (например, создание ветки или нет изменений)")

        print(f"{'='*60}\n")
        
        print("Имитируем бурную деятельность (3 секунды)...")
        time.sleep(3)
        
        print("Push успешно обработан!")
        
        return {
            "status":        "success",
            "repo":          repo_full_name,
            "branch":        ref,
            "commits_count": len(payload.commits),
            "diff_size":     len(diff_text) if diff_text else 0,
            "processed_at":  datetime.utcnow().isoformat(),
        }
        
    except Exception as e:
        print(f"Ошибка при обработке Push: {e}")
        raise

@celery_app.task(bind=True, max_retries=1, default_retry_delay=30, pydantic=True, rate_limit='1/m') #rate_limit='10/m' #pydantic=True
def process_pull_request(self, payload: SPullRequestWebhook):
    try:
        action =            payload.action
        pr_number =         payload.number
        pr_title =          payload.pull_request.title
        pr_url =            payload.pull_request.url
        repo_full_name =    payload.repository.full_name
        user =              payload.sender.login
        
        print(f"\n{'='*60}")
        print(f"Обработка PR #{pr_number}: {pr_title}")
        print(f"Автор: {user}")
        print(f"Репозиторий: {repo_full_name}")
        print(f"Действие: {action}")
        print(f"URL: {pr_url}")
        print(f"{'='*60}\n")
        
        diff_text: Optional[str] = None
        diff_path: Optional[str] = None

        # Diff актуален только для «живых» действий
        if action in {"opened", "synchronize", "reopened", "ready_for_review", "edited"}:
            print("⬇️ Скачиваем diff PR...")
            diff_text = fetch_pr_diff(repo_full_name, pr_number)
            if diff_text:
                #diff_path = save_diff(repo_full_name, f"pr{pr_number}", diff_text)
                print(f"✅ Diff: {len(diff_text)}")
            else:
                print("⚠️ Diff пуст")
        else:
            print(f"Действие '{action}' — diff не запрашиваем")
        
        print("Имитируем бурную деятельность (5 секунд)...")
        time.sleep(5)
        
        print("PR обработан успешно!")
        
        return {
            "status":      "success",
            "pr_number":   pr_number,
            "diff_size":   len(diff_text) if diff_text else 0,
            "processed_at": datetime.utcnow().isoformat(),
        }
        
    except Exception as e:
        print(f"Ошибка при обработке PR: {e}")
        raise