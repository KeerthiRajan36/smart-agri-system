"""Import every model so Base.metadata is aware of all tables."""
from app.models.user import User
from app.models.farm import Farm
from app.models.field import Field
from app.models.crop import Crop
from app.models.irrigation import Irrigation
from app.models.treatment import CropTreatment
from app.models.health import CropHealth
from app.models.alert import Alert
from app.models.harvest import Harvest
from app.models.sale import Sale

__all__ = [
    "User", "Farm", "Field", "Crop", "Irrigation",
    "CropTreatment", "CropHealth", "Alert", "Harvest", "Sale",
]
