#!/usr/bin/env python3
from pydantic import BaseModel, Field
from typing import Optional

class T(BaseModel):
    device_id: int
    to_facility_id: int
    from_facility_id: Optional[int] = Field(default=None)
    giver_name: Optional[str] = Field(default=None)
    transfer_reason: Optional[str] = Field(default=None)
    transfer_date: Optional[str] = Field(default=None)

# Test
t = T(device_id=1, to_facility_id=1)
print("Model works:", t.model_dump())

# Test validation
try:
    t2 = T(device_id=1, to_facility_id=1, from_facility_id=None, giver_name=None)
    print("Validation works:", t2.model_dump())
except Exception as e:
    print("Error:", e)