from typing import List
from pydantic import BaseModel


class DashboardSummary(BaseModel):
    total_farms: int
    total_fields: int
    active_crops: int
    crops_ready_for_harvest: int
    critical_crop_alerts: int
    total_harvest_quantity: float
    total_sales: int
    total_revenue: float
    total_treatment_cost: float


class FarmRevenue(BaseModel):
    farm_id: int
    farm_name: str
    total_revenue: float


class CropProduction(BaseModel):
    crop_name: str
    total_quantity: float


class DashboardReports(BaseModel):
    farm_wise_revenue: List[FarmRevenue]
    crop_wise_production: List[CropProduction]
