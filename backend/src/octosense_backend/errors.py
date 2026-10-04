"""错误类型：所有命令边界与 HTTP API 共用统一错误信封。"""
from dataclasses import dataclass


@dataclass
class OctoSenseError(Exception):
    code: str = "INTERNAL_ERROR"
    detail: str = ""
    http_status: int = 400

    def to_dict(self) -> dict:
        return {"code": self.code, "detail": self.detail}

    def __str__(self) -> str:
        return f"{self.code}: {self.detail}"


# 业务错误（raise 时只需传 detail）
class TaskNotFound(OctoSenseError):
    code = "TASK_NOT_FOUND"
    http_status = 404
    def __init__(self, detail: str = "task not found"):
        super().__init__(self.code, detail, self.http_status)


class DraftMissingField(OctoSenseError):
    code = "DRAFT_MISSING_FIELD"
    http_status = 422
    def __init__(self, detail: str = "field missing"):
        super().__init__(self.code, detail, self.http_status)


class IdempotencyConflict(OctoSenseError):
    code = "IDEMPOTENCY_CONFLICT"
    http_status = 409
    def __init__(self, detail: str = "idempotency conflict"):
        super().__init__(self.code, detail, self.http_status)


class VersionConflict(OctoSenseError):
    code = "VERSION_CONFLICT"
    http_status = 409
    def __init__(self, detail: str = "version conflict"):
        super().__init__(self.code, detail, self.http_status)


class IllegalTransition(OctoSenseError):
    code = "ILLEGAL_TRANSITION"
    http_status = 422
    def __init__(self, detail: str = "illegal transition"):
        super().__init__(self.code, detail, self.http_status)


class PermissionDenied(OctoSenseError):
    code = "PERMISSION_DENIED"
    http_status = 403
    def __init__(self, detail: str = "permission denied"):
        super().__init__(self.code, detail, self.http_status)


class ConcurrentConflict(OctoSenseError):
    code = "CONCURRENT_CONFLICT"
    http_status = 409
    def __init__(self, detail: str = "concurrent conflict"):
        super().__init__(self.code, detail, self.http_status)


class IdentityRequired(OctoSenseError):
    code = "IDENTITY_REQUIRED"
    http_status = 401
    def __init__(self, detail: str = "identity required"):
        super().__init__(self.code, detail, self.http_status)


class ProjectNotFound(OctoSenseError):
    code = "PROJECT_NOT_FOUND"
    http_status = 404
    def __init__(self, detail: str = "project not found"):
        super().__init__(self.code, detail, self.http_status)


class NoAssignee(OctoSenseError):
    code = "NO_ASSIGNEE"
    http_status = 422
    def __init__(self, detail: str = "task has no assignee"):
        super().__init__(self.code, detail, self.http_status)


class AssetNotFound(OctoSenseError):
    code = "ASSET_NOT_FOUND"
    http_status = 404
    def __init__(self, detail: str = "asset not found"):
        super().__init__(self.code, detail, self.http_status)


class AssetArchived(OctoSenseError):
    code = "ASSET_ARCHIVED"
    http_status = 422
    def __init__(self, detail: str = "asset archived"):
        super().__init__(self.code, detail, self.http_status)


class InvalidProjectReference(OctoSenseError):
    code = "INVALID_PROJECT_REFERENCE"
    http_status = 422
    def __init__(self, detail: str = "cross-project reference rejected"):
        super().__init__(self.code, detail, self.http_status)


class EvidenceNotFound(OctoSenseError):
    code = "EVIDENCE_NOT_FOUND"
    http_status = 404
    def __init__(self, detail: str = "evidence not found"):
        super().__init__(self.code, detail, self.http_status)


class EvidenceTooLarge(OctoSenseError):
    code = "EVIDENCE_TOO_LARGE"
    http_status = 422
    def __init__(self, detail: str = "evidence too large"):
        super().__init__(self.code, detail, self.http_status)


class EvidenceQuarantined(OctoSenseError):
    code = "EVIDENCE_QUARANTINED"
    http_status = 422
    def __init__(self, detail: str = "evidence quarantined"):
        super().__init__(self.code, detail, self.http_status)


class InvalidKind(OctoSenseError):
    code = "INVALID_KIND"
    http_status = 422
    def __init__(self, detail: str = "invalid kind"):
        super().__init__(self.code, detail, self.http_status)

class InvalidVersion(OctoSenseError):
    code = "INVALID_VERSION"
    http_status = 422
    def __init__(self, detail: str = "expected_version must be a strict positive integer"):
        super().__init__(self.code, detail, self.http_status)


class SkillMismatch(OctoSenseError):
    code = "SKILL_MISMATCH"
    http_status = 403
    def __init__(self, detail: str = "skill does not match task category"):
        super().__init__(self.code, detail, self.http_status)


class ServiceRelationMissing(OctoSenseError):
    code = "SERVICE_RELATION_MISSING"
    http_status = 422
    def __init__(self, detail: str = "asset has no effective service relation to the task space"):
        super().__init__(self.code, detail, self.http_status)


class SpaceRequired(OctoSenseError):
    code = "SPACE_REQUIRED"
    http_status = 422
    def __init__(self, detail: str = "confirmed service space required"):
        super().__init__(self.code, detail, self.http_status)


class EvidenceIntegrity(OctoSenseError):
    code = "EVIDENCE_INTEGRITY"
    http_status = 422
    def __init__(self, detail: str = "evidence file missing or corrupted"):
        super().__init__(self.code, detail, self.http_status)


class AppointmentExpired(OctoSenseError):
    code = "APPOINTMENT_EXPIRED"
    http_status = 410
    def __init__(self, detail: str = "appointment proposal expired"):
        super().__init__(self.code, detail, self.http_status)


class AppointmentWindowInvalid(OctoSenseError):
    code = "APPOINTMENT_WINDOW_INVALID"
    http_status = 422
    def __init__(self, detail: str = "appointment window violates product defaults"):
        super().__init__(self.code, detail, self.http_status)


class InvalidRoleFilter(OctoSenseError):
    code = "INVALID_ROLE_FILTER"
    http_status = 403
    def __init__(self, detail: str = "role filter is not one of the caller's own roles"):
        super().__init__(self.code, detail, self.http_status)
