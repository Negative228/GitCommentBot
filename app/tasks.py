from celery import Celery
import os, json, time
from datetime import datetime
from schemas import *

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
        repo_full_name = payload.repository.full_name
        sender = payload.sender.login
        ref = payload.ref
        
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
        
        # Если это не удаление ветки, анализируем коммиты
        if not payload.deleted and payload.commits:
            print(f"\n📝 Коммитов в пуше: {len(payload.commits)}")
            
            # Считаем общую статистику по файлам
            # TO DO: Вынести в другое место
            total_added = 0
            total_removed = 0
            total_modified = 0
            
            for commit in payload.commits:
                total_added += len(commit.added)
                total_removed += len(commit.removed)
                total_modified += len(commit.modified)
            
            print(f"\n Затронутые файлы:")
            print(f"   - Добавлено: {total_added}")
            print(f"   - Удалено: {total_removed}")
            print(f"   - Изменено: {total_modified}")
            
            # Здесь позже будет логика:
            # 1. Если пуш в main/master -> обновить RAG базу (переиндексировать измененные файлы)
            # 2. Если пуш в feature-ветку -> проверить на наличие секретов/уязвимостей
            
        elif payload.deleted:
            print("Ветка удалена, коммиты отсутствуют.")
            
        else:
            print("Dummy-пуш")

        print(f"{'='*60}\n")
        
        print("Имитируем бурную деятельность (3 секунды)...")
        time.sleep(3)
        
        print("Push успешно обработан!")
        
        return {
            "status": "success",
            "repo": repo_full_name,
            "branch": ref,
            "commits_count": len(payload.commits),
            "processed_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        print(f"Ошибка при обработке Push: {e}")
        raise

@celery_app.task(bind=True, max_retries=1, default_retry_delay=30, pydantic=True, rate_limit='1/m') #rate_limit='10/m' #pydantic=True
def process_pull_request(self, payload: SPullRequestWebhook):
    try:
        action = payload.action
        pr_number = payload.number
        pr_title = payload.pull_request.title
        pr_url = payload.pull_request.url
        repo_full_name = payload.repository.full_name
        user = payload.sender.login
        
        print(f"\n{'='*60}")
        print(f"Обработка PR #{pr_number}: {pr_title}")
        print(f"Автор: {user}")
        print(f"Репозиторий: {repo_full_name}")
        print(f"Действие: {action}")
        print(f"URL: {pr_url}")
        print(f"{'='*60}\n")
        
        print("Имитируем бурную деятельность (5 секунд)...")
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