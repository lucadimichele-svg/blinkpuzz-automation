"""Posting cadence for @blinkpuzz only (Europe/Berlin).

Option B: 4 Reels/day 2026-11-10 through 2026-11-16, then 2/day.
On launch day, extra posts are shifted into the afternoon so nothing is backdated.
The original YYYY-MM-DD.mp4 remains the 19:30 slot, preserving existing Buffer posts.
"""
from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

TZ = ZoneInfo("Europe/Berlin")
BOOST_START = date(2026, 11, 10)
BOOST_END = BOOST_START + timedelta(days=6)

# Each slot identifier is stable and unique within the day.
# "base" retains the original daily post and its legacy Challenge ID.
LAUNCH = (("B1", "16:30"), ("B2", "18:00"),
          ("base", "19:30"), ("B3", "21:30"))
BOOST = (("B1", "10:00"), ("B2", "14:00"),
         ("base", "19:30"), ("B3", "21:30"))
ONGOING = (("N1", "12:00"), ("base", "19:30"))


def slots_for(day: date):
    if day == BOOST_START:
        return LAUNCH
    if BOOST_START < day <= BOOST_END:
        return BOOST
    return ONGOING


def filename_stem(day: date, slot: str) -> str:
    return day.isoformat() + ("" if slot == "base" else "-" + slot)


def challenge_id(day: date, slot: str) -> str:
    return "BP" + day.strftime("%Y%m%d") + ("" if slot == "base" else slot)


def planned_at(day: date, clock: str) -> datetime:
    hour, minute = map(int, clock.split(":"))
    return datetime.combine(day, time(hour, minute), tzinfo=TZ)


def planned_items(start: date, days=7):
    for offset in range(days):
        day = start + timedelta(days=offset)
        for slot, clock in slots_for(day):
            yield day, slot, clock, planned_at(day, clock)
