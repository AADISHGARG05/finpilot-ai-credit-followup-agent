from pydantic import BaseModel
class EmailResponse(BaseModel):
    subject: str
    body: str
    tone: str
    stage: str
    cta: str
    payment_reminder_level: str