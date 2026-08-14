import enum


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    FARM_MANAGER = "farm_manager"
    FARMER = "farmer"
    FIELD_WORKER = "field_worker"


class FarmStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    UNDER_MAINTENANCE = "under_maintenance"


class FieldStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    UNDER_MAINTENANCE = "under_maintenance"


class CropStatus(str, enum.Enum):
    PLANNED = "planned"
    GROWING = "growing"
    READY_FOR_HARVEST = "ready_for_harvest"
    HARVESTED = "harvested"
    FAILED = "failed"


class IrrigationStatus(str, enum.Enum):
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ProductType(str, enum.Enum):
    FERTILIZER = "fertilizer"
    PESTICIDE = "pesticide"
    HERBICIDE = "herbicide"
    OTHER = "other"


class HealthStatus(str, enum.Enum):
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"


class SeverityLevel(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    PARTIAL = "partial"
    PAID = "paid"
