"""Report repository interfaces (DIP)."""

from abc import ABC, abstractmethod
from typing import List, Optional

from app.domains.reports.models import Report, ReportStatus
from app.domains.reports.schemas import ReportCreate


class IReportRepository(ABC):
    """Interface for report persistence and CRUD (ISP: only CRUD concerns)."""

    @abstractmethod
    async def get_by_id(self, report_id: str) -> Optional[Report]:
        pass

    @abstractmethod
    async def create(self, owner_id: str, report: ReportCreate) -> Report:
        pass

    @abstractmethod
    async def update_status(self, report_id: str, status: ReportStatus) -> Optional[Report]:
        pass

    @abstractmethod
    async def get_by_owner(self, owner_id: str) -> List[Report]:
        pass


class IReportSearchRepository(ABC):
    """Interface for report search/query concerns (ISP: segregated from CRUD)."""

    @abstractmethod
    async def get_active_in_bounding_box(
        self, min_lat: float, max_lat: float, min_lon: float, max_lon: float
    ) -> List[Report]:
        """Cheap pre-filter by bounding box; caller refines with Haversine."""
        pass

    @abstractmethod
    async def get_active(self) -> List[Report]:
        pass
