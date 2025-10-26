from datetime import UTC, date, datetime
from typing import Any, List, Optional

from pydantic import UUID4, BaseModel, Field


class BaseEncoder(BaseModel):

    class Config:
        json_encoders = {
            date: lambda v: v.strftime("%Y-%m-%d"),
            datetime: lambda v: v.astimezone(UTC)
            .replace(microsecond=0)
            .isoformat()
            .replace("+00:00", "Z"),
            UUID4: lambda v: str(v),
        }


class Cycle(BaseEncoder):
    archived_at: Optional[datetime] = None
    backlog_issues: Optional[int] = None
    cancelled_issues: Optional[int] = None
    completed_estimates: Optional[float] = None
    completed_issues: Optional[int] = None
    created_at: Optional[datetime] = None
    created_by: Optional[UUID4] = None
    deleted_at: Optional[datetime] = None
    description: Optional[str] = None
    end_date: Optional[date] = Field(
        default=None, description="The end date of the cycle of format YYYY-MM-DD"
    )
    external_id: Optional[str] = Field(default=None, max_length=255)
    external_source: Optional[str] = Field(default=None, max_length=255)
    id: Optional[UUID4] = None
    logo_props: Optional[Any] = None
    name: Optional[str] = Field(default=None, max_length=255)
    owned_by: Optional[UUID4] = None
    progress_snapshot: Optional[Any] = None
    project_id: Optional[UUID4] = None
    sort_order: Optional[float] = None
    start_date: Optional[date] = Field(
        default=None, description="The start date of the cycle of format YYYY-MM-DD"
    )
    started_estimates: Optional[float] = None
    started_issues: Optional[int] = None
    timezone: Optional[Any] = None
    total_estimates: Optional[float] = None
    total_issues: Optional[int] = None
    unstarted_issues: Optional[int] = None
    updated_at: Optional[datetime] = None
    updated_by: Optional[UUID4] = None
    version: Optional[int] = Field(default=None, ge=-2147483648, le=2147483647)
    view_props: Optional[Any] = None
    workspace: Optional[UUID4] = None


class CycleCreate(Cycle):
    name: str = Field(..., max_length=255)


class Module(BaseEncoder):
    archived_at: Optional[datetime] = None
    backlog_issues: Optional[int] = None
    cancelled_issues: Optional[int] = None
    completed_issues: Optional[int] = None
    created_at: Optional[datetime] = None
    created_by: Optional[UUID4] = None
    deleted_at: Optional[datetime] = None
    description: Optional[str] = None
    description_html: Optional[Any] = None
    description_text: Optional[Any] = None
    external_id: Optional[str] = Field(default=None, max_length=255)
    external_source: Optional[str] = Field(default=None, max_length=255)
    id: Optional[UUID4] = None
    lead: Optional[UUID4] = None
    logo_props: Optional[Any] = None
    members: Optional[List[UUID4]] = None
    name: Optional[str] = Field(default=None, max_length=255)
    project: Optional[UUID4] = None
    sort_order: Optional[float] = 0
    start_date: Optional[date] = None
    started_issues: Optional[int] = None
    status: Optional[Any] = None
    target_date: Optional[date] = None
    total_issues: Optional[int] = None
    unstarted_issues: Optional[int] = None
    updated_at: Optional[datetime] = None
    updated_by: Optional[UUID4] = None
    view_props: Optional[Any] = None
    workspace: Optional[UUID4] = None


class ModuleCreate(Module):
    name: str = Field(..., max_length=255)


class Issue(BaseEncoder):
    name: Optional[str] = Field(default=None, max_length=255)
    description_html: Optional[str] = None
    description_binary: Optional[str] = None
    archived_at: Optional[date] = None
    assignees: Optional[List[UUID4]] = None
    completed_at: Optional[datetime] = None
    estimate_point: Optional[UUID4] = None
    external_id: Optional[str] = Field(default=None, max_length=255)
    external_source: Optional[str] = Field(default=None, max_length=255)
    is_draft: Optional[bool] = None
    labels: Optional[List[UUID4]] = None
    parent: Optional[UUID4] = None
    point: Optional[int] = Field(default=None, ge=0, le=12)
    priority: Optional[Any] = None
    sequence_id: Optional[int] = Field(default=None, ge=-2147483648, le=2147483647)
    sort_order: Optional[float] = None
    start_date: Optional[date] = None
    state: Optional[UUID4] = None
    target_date: Optional[date] = None
    type: Optional[UUID4] = None
    type_id: Optional[UUID4] = None
    created_at: Optional[datetime] = None
    id: Optional[UUID4] = None
    project: Optional[UUID4] = None
    updated_at: Optional[datetime] = None
    updated_by: Optional[UUID4] = None
    workspace: Optional[UUID4] = None


class IssueCreate(Issue):
    name: str = Field(..., max_length=255)
    description_html: str = Field(...)


class State(BaseEncoder):
    color: Optional[str] = Field(default=None, max_length=255)
    created_at: Optional[datetime] = None
    created_by: Optional[UUID4] = None
    default: Optional[bool] = None
    deleted_at: Optional[datetime] = None
    description: Optional[str] = None
    external_id: Optional[str] = Field(default=None, max_length=255)
    external_source: Optional[str] = Field(default=None, max_length=255)
    group: Optional[Any] = None
    id: Optional[UUID4] = None
    is_triage: Optional[bool] = None
    name: Optional[str] = Field(default=None, max_length=255)
    project: Optional[UUID4] = None
    sequence: Optional[float] = None
    slug: Optional[str] = Field(
        default=None, max_length=100, pattern=r"^[-a-zA-Z0-9_]+$"
    )
    updated_at: Optional[datetime] = None
    updated_by: Optional[UUID4] = None
    workspace: Optional[UUID4] = None


class StateCreate(State):
    color: str = Field(..., max_length=255)
    name: str = Field(..., max_length=255)


class Label(BaseEncoder):
    color: Optional[str] = Field(default=None, max_length=255)
    created_at: Optional[datetime] = None
    created_by: Optional[UUID4] = None
    deleted_at: Optional[datetime] = None
    description: Optional[str] = None
    external_id: Optional[str] = Field(default=None, max_length=255)
    external_source: Optional[str] = Field(default=None, max_length=255)
    id: Optional[UUID4] = None
    name: Optional[str] = Field(default=None, max_length=255)
    parent: Optional[UUID4] = None
    project: Optional[UUID4] = None
    sort_order: Optional[float] = None
    updated_at: Optional[datetime] = None
    updated_by: Optional[UUID4] = None
    workspace: Optional[UUID4] = None


class LabelCreate(Label):
    color: str = Field(..., max_length=255)
    name: str = Field(..., max_length=255)
