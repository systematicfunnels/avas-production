from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, field_validator
import re


# ---- Auth Schemas ----

class UserRegister(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    organization: Optional[str] = None

    @field_validator("password")
    @classmethod
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    organization: Optional[str]
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ---- Asset Schemas ----

class AssetCreate(BaseModel):
    name: str
    asset_type: str
    location_name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    description: Optional[str] = None
    metadata: dict = {}


class AssetResponse(BaseModel):
    id: str
    name: str
    asset_type: str
    location_name: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    description: Optional[str]
    risk_score: float
    created_at: datetime

    model_config = {"from_attributes": True}


# ---- Inspection Schemas ----

class InspectionCreate(BaseModel):
    title: str
    asset_id: Optional[str] = None


class DefectResponse(BaseModel):
    id: str
    defect_type: str
    severity: str
    confidence: float
    bbox: Optional[dict]
    description: Optional[str]
    recommendation: Optional[str]

    model_config = {"from_attributes": True}


class InspectionResponse(BaseModel):
    id: str
    title: str
    status: str
    image_count: int
    risk_score: Optional[float]
    defect_count: int
    processing_duration_ms: Optional[int]
    error_message: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime]
    defects: List[DefectResponse] = []

    model_config = {"from_attributes": True}


class InspectionListResponse(BaseModel):
    id: str
    title: str
    status: str
    image_count: int
    risk_score: Optional[float]
    defect_count: int
    created_at: datetime

    model_config = {"from_attributes": True}


# ---- Analytics Schemas ----

class DashboardStats(BaseModel):
    total_inspections: int
    total_assets: int
    total_defects: int
    critical_defects: int
    avg_risk_score: float
    inspections_this_month: int


class RiskSummary(BaseModel):
    asset_id: str
    asset_name: str
    risk_score: float
    defect_count: int
    last_inspection: Optional[datetime]


# ---- Pagination ----

class PaginatedResponse(BaseModel):
    items: list
    total: int
    page: int
    page_size: int
    pages: int
