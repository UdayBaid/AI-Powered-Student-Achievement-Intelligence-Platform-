from datetime import datetime

from pydantic import BaseModel, Field

FEATURE_COLUMNS = [
    "school", "sex", "age", "address", "famsize", "Pstatus",
    "Medu", "Fedu", "Mjob", "Fjob", "reason", "guardian",
    "traveltime", "studytime", "failures", "schoolsup",
    "famsup", "paid", "activities", "nursery", "higher",
    "internet", "romantic", "famrel", "freetime", "goout",
    "Dalc", "Walc", "health", "absences",
]


class StudentInput(BaseModel):
    school: str = Field(description="GP or MS")
    sex: str = Field(description="F or M")
    age: int = Field(ge=15, le=22)
    address: str
    famsize: str
    Pstatus: str
    Medu: int = Field(ge=0, le=4)
    Fedu: int = Field(ge=0, le=4)
    Mjob: str
    Fjob: str
    reason: str
    guardian: str
    traveltime: int = Field(ge=1, le=4)
    studytime: int = Field(ge=1, le=4)
    failures: int = Field(ge=0, le=4)
    schoolsup: str
    famsup: str
    paid: str
    activities: str
    nursery: str
    higher: str
    internet: str
    romantic: str
    famrel: int = Field(ge=1, le=5)
    freetime: int = Field(ge=1, le=5)
    goout: int = Field(ge=1, le=5)
    Dalc: int = Field(ge=1, le=5)
    Walc: int = Field(ge=1, le=5)
    health: int = Field(ge=1, le=5)
    absences: int = Field(ge=0)


class PredictionHistoryItem(BaseModel):
    id: int
    student_data: dict[str, object]
    result: dict[str, object]
    created_at: datetime

    model_config = {"from_attributes": True}
