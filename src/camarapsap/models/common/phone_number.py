"""Phone number model."""

from pydantic import BaseModel, Field, field_validator
import re


class PhoneNumber(BaseModel):
    """A public identifier addressing a telephone subscription.
    
    In mobile networks it corresponds to the MSISDN (Mobile Station International 
    Subscriber Directory Number). In order to be globally unique it has to be 
    formatted in international format, according to E.164 standard, prefixed with '+'.
    """
    
    phone_number: str = Field(
        ...,
        pattern=r'^\+[1-9][0-9]{4,14}$',
        examples=["+123456789"],
        description="Phone number in E.164 format"
    )
    
    @field_validator('phone_number')
    @classmethod
    def validate_phone_number(cls, v: str) -> str:
        if not re.match(r'^\+[1-9][0-9]{4,14}$', v):
            raise ValueError('Phone number must be in E.164 format with + prefix')
        return v
