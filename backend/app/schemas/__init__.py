"""
Schémas Pydantic pour l'API AGRIFRIKA Dashboard
"""

from .api_schemas import (
    APIResponse,
    APIResponseBase,
    HealthResponse,
    HealthStatus,
    SyncStatus,
    SyncStatusResponse,
    SyncExecutionResult,
    Dashboard2Data,
    TeamMemberAvailability,
    WeeklyPlanningItem,
    BasecampTask,
    CashFlowData,
    FacebookVideoMetrics,
    KPIMetrics,
    ErrorResponse,
    ErrorDetail,
    CredentialValidation,
    SystemInfo
)

__all__ = [
    "APIResponse",
    "APIResponseBase",
    "HealthResponse",
    "HealthStatus",
    "SyncStatus",
    "SyncStatusResponse",
    "SyncExecutionResult",
    "Dashboard2Data",
    "TeamMemberAvailability",
    "WeeklyPlanningItem",
    "BasecampTask",
    "CashFlowData",
    "FacebookVideoMetrics",
    "KPIMetrics",
    "ErrorResponse",
    "ErrorDetail",
    "CredentialValidation",
    "SystemInfo"
]