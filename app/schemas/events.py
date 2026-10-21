from pydantic import BaseModel, Field
from typing import Optional, List, Any, Dict
from datetime import datetime
from entities import SGitHubUser, SGitHubRepository, SGitHubOrganization, SGitHubEvent
"""
class SGitHubEvent(BaseModel, extra=Extra.allow):
    action: Optional[str] = None
    sender: SGitHubUser
    repository: SGitHubRepository
    organization: Optional[SGitHubOrganization] = None
    installation: Optional[Dict[str, Any]] = None
"""

class PullRequestInfo(SGitHubEvent):
    """Информация о Pull Request"""
    url: str
    id: int
    node_id: str = Field(alias="node_id")
    number: int
    state: str
    title: str
    body: Optional[str] = None
    user: SGitHubUser
    html_url: str
    created_at: str
    updated_at: str
    closed_at: Optional[str] = None
    merged_at: Optional[str] = None
    merge_commit_sha: Optional[str] = None
    assignee: Optional[SGitHubUser] = None
    assignees: List[SGitHubUser] = []
    requested_reviewers: List[SGitHubUser] = []
    head: Dict[str, Any]  # Упрощенно, можно детализировать
    base: Dict[str, Any]  # Упрощенно, можно детализировать
    draft: bool = False
    merged: bool = False
    mergeable: Optional[bool] = None
    commits: int = 0
    additions: int = 0
    deletions: int = 0
    changed_files: int = 0


class PushCommit(BaseModel):
    """Информация о коммите при push"""
    id: str
    tree_id: str
    distinct: bool
    message: str
    timestamp: str
    url: str
    author: Dict[str, str]
    committer: Dict[str, str]
    added: List[str] = []
    removed: List[str] = []
    modified: List[str] = []


class IssueInfo(BaseModel):
    """Информация об Issue"""
    url: str
    id: int
    node_id: str = Field(alias="node_id")
    number: int
    title: str
    body: Optional[str] = None
    user: SGitHubUser
    state: str
    html_url: str
    created_at: str
    updated_at: str
    closed_at: Optional[str] = None
    labels: List[Dict[str, Any]] = []
    assignee: Optional[SGitHubUser] = None
    assignees: List[SGitHubUser] = []


class CommentInfo(BaseModel):
    """Информация о комментарии"""
    url: str
    id: int
    node_id: str = Field(alias="node_id")
    body: str
    user: SGitHubUser
    created_at: str
    updated_at: str
    html_url: str
    issue_url: str


# Схемы для конкретных событий
class PullRequestWebhook(BaseModel):
    """Webhook для pull_request события"""
    action: str
    number: int
    pull_request: PullRequestInfo
    repository: SGitHubRepository
    sender: SGitHubUser
    organization: Optional[SGitHubOrganization] = None
    installation: Optional[Dict[str, Any]] = None


class PushWebhook(BaseModel):
    """Webhook для push события"""
    ref: str
    before: str
    after: str
    created: bool
    deleted: bool
    forced: bool
    base_ref: Optional[str] = None
    compare: str
    commits: List[PushCommit]
    head_commit: Optional[PushCommit] = None
    repository: SGitHubRepository
    pusher: Dict[str, str]
    sender: SGitHubUser
    organization: Optional[SGitHubOrganization] = None


class IssuesWebhook(BaseModel):
    """Webhook для issues события"""
    action: str
    issue: IssueInfo
    repository: SGitHubRepository
    sender: SGitHubUser
    organization: Optional[SGitHubOrganization] = None


class IssueCommentWebhook(BaseModel):
    """Webhook для issue_comment события"""
    action: str
    issue: IssueInfo
    comment: CommentInfo
    repository: SGitHubRepository
    sender: SGitHubUser
    organization: Optional[SGitHubOrganization] = None



# Union тип для всех поддерживаемых событий
GitHubWebhookPayload = (
    PullRequestWebhook | 
    PushWebhook | 
    IssuesWebhook | 
    IssueCommentWebhook | 
    GenericWebhook
)