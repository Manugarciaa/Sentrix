"""
Pydantic schemas for user settings
Esquemas Pydantic para configuraciones de usuario
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, Literal
from datetime import datetime


class UserSettingsBase(BaseModel):
    """Base schema for user settings"""

    # General
    language: str = Field(default="es", description="User interface language")
    timezone: str = Field(default="America/Argentina/Buenos_Aires", description="User timezone")
    date_format: str = Field(default="DD/MM/YYYY", description="Date format preference")

    # Email Notifications
    email_notifications: bool = Field(default=True, description="Enable email notifications")
    email_new_analysis: bool = Field(default=True, description="Notify on new analysis completion")
    email_validation_complete: bool = Field(default=False, description="Notify on validation completion")
    email_reports: bool = Field(default=True, description="Notify on report generation")

    # In-app Notifications
    in_app_notifications: bool = Field(default=True, description="Enable in-app notifications")

    # Analysis Defaults
    default_confidence_threshold: float = Field(
        default=0.7,
        ge=0.5,
        le=0.95,
        description="Default confidence threshold for analysis"
    )
    default_include_gps: bool = Field(default=True, description="Include GPS by default")
    auto_validate_high_confidence: bool = Field(
        default=False,
        description="Auto-validate detections with >90% confidence"
    )

    # Privacy
    profile_visibility: Literal["public", "private"] = Field(
        default="private",
        description="Profile visibility setting"
    )
    share_analytics: bool = Field(default=False, description="Share anonymous usage data")

    @field_validator("language")
    def validate_language(cls, v):
        allowed = ["es", "en", "pt"]
        if v not in allowed:
            raise ValueError(f"Language must be one of {allowed}")
        return v

    @field_validator("date_format")
    def validate_date_format(cls, v):
        allowed = ["DD/MM/YYYY", "MM/DD/YYYY", "YYYY-MM-DD"]
        if v not in allowed:
            raise ValueError(f"Date format must be one of {allowed}")
        return v


class UserSettingsCreate(UserSettingsBase):
    """Schema for creating user settings"""
    pass


class UserSettingsUpdate(BaseModel):
    """Schema for updating user settings (all fields optional)"""

    language: Optional[str] = None
    timezone: Optional[str] = None
    date_format: Optional[str] = None
    email_notifications: Optional[bool] = None
    email_new_analysis: Optional[bool] = None
    email_validation_complete: Optional[bool] = None
    email_reports: Optional[bool] = None
    in_app_notifications: Optional[bool] = None
    default_confidence_threshold: Optional[float] = Field(None, ge=0.5, le=0.95)
    default_include_gps: Optional[bool] = None
    auto_validate_high_confidence: Optional[bool] = None
    profile_visibility: Optional[Literal["public", "private"]] = None
    share_analytics: Optional[bool] = None


class UserSettingsResponse(UserSettingsBase):
    """Schema for user settings response"""

    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserSettingsInDB(UserSettingsResponse):
    """Schema for user settings in database"""
    pass


# Default settings constant
DEFAULT_USER_SETTINGS = {
    "language": "es",
    "timezone": "America/Argentina/Buenos_Aires",
    "date_format": "DD/MM/YYYY",
    "email_notifications": True,
    "email_new_analysis": True,
    "email_validation_complete": False,
    "email_reports": True,
    "in_app_notifications": True,
    "default_confidence_threshold": 0.7,
    "default_include_gps": True,
    "auto_validate_high_confidence": False,
    "profile_visibility": "private",
    "share_analytics": False
}
