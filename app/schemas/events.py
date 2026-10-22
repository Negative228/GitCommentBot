from pydantic import BaseModel, Field
from typing import Optional, List, Any, Dict
from datetime import datetime
from .entities import SGitHubUser, SGitHubRepository, SGitHubOrganization, SGitHubEvent
from .info import SPullRequestInfo, SPushCommitInfo, SIssueInfo, SCommentInfo

class SPushWebhook(SGitHubEvent):
    ref: str
    before: str
    after: str
    created: bool
    deleted: bool
    forced: bool
    base_ref: Optional[str] = None
    compare: str
    commits: List[SPushCommitInfo]
    head_commit: Optional[SPushCommitInfo] = None
    pusher: Dict[str, str]

class SPullRequestWebhook(SGitHubEvent):
    number: int
    pull_request: SPullRequestInfo


class SIssuesWebhook(SGitHubEvent):
    issue: SIssueInfo

class SIssueCommentWebhook(SGitHubEvent):
    issue: SIssueInfo
    comment: SCommentInfo