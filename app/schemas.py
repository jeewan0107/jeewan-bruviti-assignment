from typing import Literal
from pydantic import BaseModel, Field, ConfigDict, field_validator, model_validator

ProductCategory = Literal[
    "washing_machine", "refrigerator", "dishwasher", "oven_or_cooktop",
    "air_conditioner", "water_heater", "microwave"
]
FaultCategory = Literal[
    "no_power", "not_heating", "not_cooling", "water_leak",
    "drainage_or_blockage", "noise_or_vibration", "door_seal_or_latch",
    "control_panel_or_display", "electrical_or_control_board",
    "motor_or_drive", "installation_or_setup", "other"
]
WarrantyStatus = Literal["in_warranty", "extended", "out_of_warranty", "unknown"]
CustomerSentiment = Literal["negative", "neutral", "positive"]


class Part(BaseModel):
    model_config = ConfigDict(extra="ignore")
    sku: str
    description: str
    price: float | None = Field(default=None, ge=0)
    lead_time_days: int | None = Field(default=None, ge=0)


class DecisionRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")
    case_id: str
    product_category: ProductCategory
    product_age_months: int | None = Field(default=None, ge=0)
    purchase_price: float | None = Field(default=None, ge=0)
    replacement_price: float | None = Field(default=None, ge=0)
    warranty_status: WarrantyStatus
    fault_category: FaultCategory
    parts: list[Part] = Field(default_factory=list)
    labour_hours: float | None = Field(default=None, ge=0)
    labour_rate_per_hour: float = Field(ge=0)
    technician_travel_minutes: int | None = Field(default=None, ge=0)
    prior_repairs_12m: int = Field(ge=0)
    customer_sentiment: CustomerSentiment
    symptom_text: str

    @field_validator("case_id")
    @classmethod
    def case_id_not_blank(cls, value):
        if not value.strip():
            raise ValueError("case_id must not be blank")
        return value


class DecisionResponse(BaseModel):
    case_id: str
    decision: Literal["repair", "replace", "escalate"]
    estimated_repair_cost: float | None
    confidence: float = Field(ge=0, le=1)
    reason: str
