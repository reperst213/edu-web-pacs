"""뼈대 확인용 테스트. 모든 모듈이 import되고 공통 규칙이 계획서 18장과 맞는지 본다."""
import dataclasses
import importlib

import pytest

from services.errors import AppError, PermissionDenied, ValidationError
from services.types import ROLES, Actor, Status

MODULES = [
    "services.types", "services.errors", "services.auth", "services.permissions",
    "services.audit", "services.admin", "services.cases", "services.images",
    "services.notes", "services.reports", "services.processing", "services.review",
    "services.search", "repositories.base", "core.image_io", "core.roi",
    "core.features", "core.algorithms", "core.algorithms.color_constancy",
    "core.algorithms.hair_removal", "core.algorithms.segmentation", "storage.files",
]


@pytest.mark.parametrize("name", MODULES)
def test_module_imports(name):
    importlib.import_module(name)


def test_status_has_five_states():
    assert [s.value for s in Status] == [
        "RECEIVED", "ASSIGNED", "IN_REVIEW", "NEEDS_REWORK", "DONE"]


def test_roles():
    assert ROLES == ("registrar", "reviewer", "admin")


def test_actor_is_immutable():
    actor = Actor(uid="dev-reviewer", role="reviewer")
    with pytest.raises(dataclasses.FrozenInstanceError):
        actor.role = "admin"


def test_app_error_keeps_message_for_screen():
    err = PermissionDenied("배정된 검토자만 상태를 바꿀 수 있습니다.")
    assert isinstance(err, AppError)
    assert err.message == "배정된 검토자만 상태를 바꿀 수 있습니다."
    assert err.code == "permission_denied"


def test_error_codes_are_unique():
    import services.errors as errors
    codes = [c.code for c in vars(errors).values()
             if isinstance(c, type) and issubclass(c, AppError)]
    assert len(codes) == len(set(codes))


def test_validation_error_is_app_error():
    assert issubclass(ValidationError, AppError)
