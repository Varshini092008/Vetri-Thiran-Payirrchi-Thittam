from pydantic import BaseModel, Field


class HomeRequest(BaseModel):
    budget: float = Field(gt=0)

    rooms: list[str] = Field(
        min_length=1
    )

    style: str = "Modern"

    quantities: dict[str, int] = Field(
        default_factory=dict
    )

    priorities: str = ""


class PartyRequest(BaseModel):
    budget: float = Field(gt=0)

    guests: int = Field(gt=0)

    event_type: str = "Birthday"

    venue: str = "Home"

    preferences: str = ""