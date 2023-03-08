from datetime import datetime
from models import ScheduleModel


def get_date(date: str) -> datetime:
    year, month, day = [*map(lambda s: int(s), date.split("-"))]
    return datetime(year, month, day)


def get_time(time: str) -> datetime.time:
    return datetime.strptime(time, "%H:%M:%S%z").astimezone().time()


def get_schedule(schedule: dict) -> ScheduleModel:
    for race in schedule["MRData"]["RaceTable"]["Races"]:
        race["date"] = get_date(race["date"])
        race["time"] = get_time(race["time"])
        if "FirstPractice" in race:
            race["FirstPractice"]["date"] = get_date(race["FirstPractice"]["date"])
            race["FirstPractice"]["time"] = get_time(race["FirstPractice"]["time"])
        if "SecondPractice" in race:
            race["SecondPractice"]["date"] = get_date(race["SecondPractice"]["date"])
            race["SecondPractice"]["time"] = get_time(race["SecondPractice"]["time"])
        if "ThirdPractice" in race:
            race["ThirdPractice"]["date"] = get_date(race["ThirdPractice"]["date"])
            race["ThirdPractice"]["time"] = get_time(race["ThirdPractice"]["time"])
        if "Sprint" in race:
            race["Sprint"]["date"] = get_date(race["Sprint"]["date"])
            race["Sprint"]["time"] = get_time(race["Sprint"]["time"])
        if "Qualifying" in race:
            race["Qualifying"]["date"] = get_date(race["Qualifying"]["date"])
            race["Qualifying"]["time"] = get_time(race["Qualifying"]["time"])
    schedule = ScheduleModel(**schedule["MRData"])
    return schedule
