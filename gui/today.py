from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QPlainTextEdit, QVBoxLayout, QWidget

from recolul.errors import NoClockInError
from recolul.recoru.attendance_chart import AttendanceChart
from recolul.time import (
    get_leave_time,
    get_row_work_time,
    until_today,
)


class Today(QWidget):
    def __init__(self, full_attendance_chart: AttendanceChart, parent: QWidget | None = None):
        super().__init__(parent)
        self._full_attendance_chart = full_attendance_chart
        self._attendance_chart = until_today(full_attendance_chart)

        self._text_edit = QPlainTextEdit()
        self._text_edit.setReadOnly(True)

        label = QLabel("Today", self)

        self._layout = QVBoxLayout(self)
        self._layout.addWidget(label, alignment=Qt.AlignmentFlag.AlignHCenter)
        self._layout.addWidget(self._text_edit)

        self.update_text()

    def update_text(self):
        try:
            last_day = self._attendance_chart[-1]
            text = f"Clock-in: {max(entry.clock_in_time for entry in last_day.entries)}\n"
            text += f"Working hours: {get_row_work_time(last_day)}\n\n"

            leave_times = get_leave_time(self._full_attendance_chart)
            if len(leave_times) == 1:
                break_msg = "(break time included)" if leave_times[0].includes_break else "(break time not included)"
                text += f"Leave after {leave_times[0].min_time} {break_msg}"
            else:
                text += (
                    f"Leave between {leave_times[0].min_time} and {leave_times[0].max_time} (break time not included), or "
                    f"after {leave_times[1].min_time} (break time included)"
                )

            for lt in leave_times:
                if not lt.wfh_cutoff_time:
                    continue
                break_msg = "(break time included)" if lt.wfh_cutoff_includes_break else "(break time not included)"
                print(f"Warning! Reaching maximum monthly WFH hours at {lt.wfh_cutoff_time} {break_msg}.")
                break
        except NoClockInError:
            text = "You have already clocked out"

        self._text_edit.setPlainText(text)
