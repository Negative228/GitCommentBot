from pydantic import BaseModel, Field
from typing import Optional, List, Any, Dict
from datetime import datetime


# Базовые модели для общих полей
class SGitHubUser(BaseModel):
    login: str
    id: int
    node_id: str = Field(alias="node_id")
    avatar_url: str
    type: str
    site_admin: bool = False


class SGitHubRepository(BaseModel):
    id: int
    node_id: str = Field(alias="node_id")
    name: str
    full_name: str
    private: bool
    owner: SGitHubUser
    html_url: str
    description: Optional[str] = None
    fork: bool
    default_branch: str = "main"


class SGitHubOrganization(BaseModel):
    login: str
    id: int
    node_id: str = Field(alias="node_id")
    description: Optional[str] = None

class SGitHubEvent(BaseModel, extra=Extra.allow):
    action: Optional[str] = None
    sender: SGitHubUser
    repository: SGitHubRepository
    organization: Optional[SGitHubOrganization] = None
    installation: Optional[Dict[str, Any]] = None


