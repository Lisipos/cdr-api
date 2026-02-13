from pydantic import BaseModel
from typing import Optional

class CDRRequest(BaseModel):
    date_ini: str
    date_end: str
    time_ini: Optional[str] = ""
    time_end: Optional[str] = ""
    device_id: Optional[int] = None
    start: Optional[int] = 0
    limit: Optional[int] = 200