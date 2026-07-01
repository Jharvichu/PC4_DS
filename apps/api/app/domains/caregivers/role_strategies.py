"""Caregiver role strategies (LSP: all roles substitutable behind CaregiverRoleStrategy)."""

from abc import ABC, abstractmethod

from app.domains.caregivers.models import Caregiver, CaregiverRoleType


class CaregiverRoleStrategy(ABC):
    """Extension point: whether a caregiver of this role can take a given species."""

    @abstractmethod
    def can_accept_species(self, caregiver: Caregiver, species: str) -> bool:
        pass


class SolidarioRoleStrategy(CaregiverRoleStrategy):
    """Solidarios accept any species by default."""

    def can_accept_species(self, caregiver: Caregiver, species: str) -> bool:
        if not caregiver.accepted_species:
            return True
        return species in caregiver.accepted_species.split(",")


class ProfesionalRoleStrategy(CaregiverRoleStrategy):
    """Profesionales only accept species they explicitly listed."""

    def can_accept_species(self, caregiver: Caregiver, species: str) -> bool:
        if not caregiver.accepted_species:
            return False
        return species in caregiver.accepted_species.split(",")


class EspecializadoRoleStrategy(CaregiverRoleStrategy):
    """Especializados only accept their declared specialization."""

    def can_accept_species(self, caregiver: Caregiver, species: str) -> bool:
        return caregiver.specialization == species


_STRATEGIES: dict[str, CaregiverRoleStrategy] = {
    CaregiverRoleType.SOLIDARIO: SolidarioRoleStrategy(),
    CaregiverRoleType.PROFESIONAL: ProfesionalRoleStrategy(),
    CaregiverRoleType.ESPECIALIZADO: EspecializadoRoleStrategy(),
}


def get_role_strategy(role_type: str) -> CaregiverRoleStrategy:
    """Factory: resolve the strategy for a role_type string (OCP: register new roles here only)."""
    return _STRATEGIES[role_type]
