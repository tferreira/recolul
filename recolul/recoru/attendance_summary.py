import re
from enum import Enum
from typing import TypeAlias

from bs4 import Tag


class SummaryItemTitle(str, Enum):
    PAID_LEAVE_TAKEN = "有休取得日数"
    PAID_LEAVE_REMAINING = "有休残り日数"


class SummaryItem:
    """Item of the attendance chart vacations summary"""

    def __init__(self, tag: Tag):
        self._tag = tag

    @property
    def title(self) -> str:
        return self._tag.attrs[""]

    @property
    def value(self) -> list[ChartRowEntry]:
        return self._value


AttendanceSummary: TypeAlias = list[SummaryItem]
