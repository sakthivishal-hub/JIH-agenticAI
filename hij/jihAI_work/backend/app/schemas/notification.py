from pydantic import BaseModel


class NotificationPreferencesRequest(BaseModel):
    notify_email: bool | None = None
    notify_whatsapp: bool | None = None
    whatsapp_number: str | None = None


class NotificationPreferencesResponse(BaseModel):
    notify_email: bool
    notify_whatsapp: bool
    whatsapp_number: str | None = None

    class Config:
        from_attributes = True
