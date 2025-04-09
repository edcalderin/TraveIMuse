from pydantic import BaseModel, Field


class Trip(BaseModel):
    start: str = Field(description="Start location of trip")
    end: str = Field(description="End location of trip")
    waypoint: list[str] = Field(description="List of waypoints")
    transit: str = Field(description="Mode of transportation")
