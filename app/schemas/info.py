from pydantic import BaseModel, Field
from typing import Optional, List, Any, Dict

from .entities import SGitHubUser, SGitHubInfo


class SGitHubNodeInfo(SGitHubInfo):
    """Info-объект, у которого есть GraphQL node_id (PR / Issue / Comment)."""
    node_id: str = Field(alias="node_id")


class SGitHubContentInfo(SGitHubNodeInfo):
    """Info-объект с пользовательским содержимым и таймстемпами."""
    body: Optional[str] = None
    user: SGitHubUser
    html_url: str
    created_at: str
    updated_at: str


class SGitHubIssueLikeInfo(SGitHubContentInfo):
    """Общая часть для PR и Issue (то, что GitHub моделирует одинаково)."""
    number: int
    state: str
    title: str
    closed_at: Optional[str] = None
    assignee: Optional[SGitHubUser] = None
    assignees: List[SGitHubUser] = []


# --- Конкретные типы -----------------------------------------------------

class SPullRequestInfo(SGitHubIssueLikeInfo):
    merged_at: Optional[str] = None
    merge_commit_sha: Optional[str] = None
    requested_reviewers: List[SGitHubUser] = []
    head: Dict[str, Any]
    base: Dict[str, Any]
    draft: bool = False
    merged: bool = False
    mergeable: Optional[bool] = None
    commits: int = 0
    additions: int = 0
    deletions: int = 0
    changed_files: int = 0


class SIssueInfo(SGitHubIssueLikeInfo):
    labels: List[Dict[str, Any]] = []


class SCommentInfo(SGitHubContentInfo):
    body: str         
    issue_url: str


class SPushCommitInfo(SGitHubInfo):
    id: str
    tree_id: str
    distinct: bool
    message: str
    timestamp: str
    author: Dict[str, str]
    committer: Dict[str, str]
    added: List[str] = []
    removed: List[str] = []
    modified: List[str] = []