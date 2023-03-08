import datetime
from pydantic import BaseModel, Field


class Location(BaseModel):
    locality: str
    country: str


class Circuit(BaseModel):
    location: Location = Field(None, alias="Location")


class RaceTime(BaseModel):
    date: datetime.datetime
    time: datetime.time


class Race(RaceTime, BaseModel):
    round: int
    raceName: str
    circuit: Circuit = Field(None, alias="Circuit")
    fp1: RaceTime = Field(None, alias="FirstPractice")
    fp2: RaceTime = Field(None, alias="SecondPractice")
    fp3: RaceTime = Field(None, alias="ThirdPractice")
    quali: RaceTime = Field(None, alias="Qualifying")
    sprint: RaceTime = Field(None, alias="Sprint")


class RaceTable(BaseModel):
    season: int
    races: list[Race] = Field(list[Race], alias="Races")


class ScheduleModel(BaseModel):
    raceTable: RaceTable = Field(RaceTable, alias="RaceTable")

    def __repr__(self) -> str:
        members = ", ".join(f"{key}={value}" for key, value in self.__dict__.items())
        return f"{type(self).__name__}({members})"
