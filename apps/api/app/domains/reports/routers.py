"""Report domain routes."""

from typing import List

from fastapi import APIRouter, BackgroundTasks, Depends, status

from app.core.dependencies import get_report_service, get_current_user
from app.domains.reports.schemas import ReportCreate, ReportStatusUpdate, ReportResponse, ReportPublicResponse
from app.domains.reports.services import ReportService
from app.domains.users.schemas import UserResponse

router = APIRouter(prefix="/reports", tags=["reports"])


@router.post("/", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
async def create_report(
    report_data: ReportCreate,
    background_tasks: BackgroundTasks,
    current_user: UserResponse = Depends(get_current_user),
    service: ReportService = Depends(get_report_service),
):
    """Report a lost pet. Alerts within the radius (RF 1.4) are dispatched in the
    background so the response isn't held up waiting on the notification fan-out."""
    report = await service.create_report(current_user.id, report_data)
    background_tasks.add_task(service.dispatch_new_report_alert, report.id, report_data)
    return report


@router.get("/active", response_model=List[ReportPublicResponse])
async def get_active_reports(
    service: ReportService = Depends(get_report_service),
):
    """Public feed of active lost-pet reports (anonymized, RNF 1.2)."""
    return await service.get_active_public_reports()


@router.get("/me", response_model=List[ReportResponse])
async def get_my_reports(
    current_user: UserResponse = Depends(get_current_user),
    service: ReportService = Depends(get_report_service),
):
    """Get all reports created by the current user (owner view, full details)."""
    return await service.get_my_reports(current_user.id)


@router.get("/{report_id}", response_model=ReportPublicResponse)
async def get_report_public(
    report_id: str,
    service: ReportService = Depends(get_report_service),
):
    """Public/anonymized view of a report for citizens (RNF 1.2)."""
    return await service.get_report_public(report_id)


@router.get("/{report_id}/owner-view", response_model=ReportResponse)
async def get_report_owner_view(
    report_id: str,
    current_user: UserResponse = Depends(get_current_user),
    service: ReportService = Depends(get_report_service),
):
    """Full report details (owner-facing only)."""
    return await service.get_report(report_id, current_user.id)


@router.put("/{report_id}/status", response_model=ReportResponse)
async def update_report_status(
    report_id: str,
    data: ReportStatusUpdate,
    current_user: UserResponse = Depends(get_current_user),
    service: ReportService = Depends(get_report_service),
):
    """Update report status (e.g. mark as ENCONTRADO)."""
    return await service.update_status(report_id, current_user.id, data.status)
