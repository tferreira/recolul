import argparse
import sys
from datetime import datetime
from getpass import getpass

from recolul import plotting, time
from recolul.config import Config
from recolul.duration import Duration
from recolul.recoru.attendance_chart import AttendanceChart
from recolul.recoru.recoru_session import RecoruSession
from recolul.time import get_work_time


def balance(exclude_last_day: bool) -> None:
    attendance_chart = _get_attendance_chart()
    month = attendance_chart[:-1] if exclude_last_day else attendance_chart
    overtime_balance, total_workplace_times = time.get_overtime_balance(month)
    print(f"Monthly overtime balance: {overtime_balance}")
    print(f"Total time per workplace:")
    for workplace, total_work_time in total_workplace_times.items():
        print(f"  {workplace}: {total_work_time}")

    if exclude_last_day:
        return

    last_day = attendance_chart[-1]
    print(f"\nLast day {last_day.day.text}")
    print(f"  Clock-in: {last_day.clock_in_time}")
    print(f"  Working hours: {get_work_time(last_day)}")


def when_to_leave() -> None:
    attendance_chart = _get_attendance_chart()
    leave_time, includes_break = time.get_leave_time(attendance_chart)
    current_time = Duration.now()
    if leave_time <= current_time:
        print("Leave today as early as you like.")
        return

    break_msg = "(includes a 1-hour break)" if includes_break else "(break time not included)"
    print(f"Leave today at {leave_time} to avoid overtime {break_msg}.")


def update_config() -> None:
    """Needs to match Config.load"""
    recoru_contract_id = input("recoru.contractId: ")
    recoru_auth_id = input("recoru.authId: ")
    recoru_password = getpass("recoru.password: ")
    config = Config(
        recoru_contract_id=recoru_contract_id,
        recoru_auth_id=recoru_auth_id,
        recoru_password=recoru_password
    )
    config.save()


def graph(exclude_last_day: bool) -> None:
    attendance_chart = _get_attendance_chart()
    if exclude_last_day and len(attendance_chart) > 1:
        attendance_chart = attendance_chart[:-1]
    days, history, _ = time.get_overtime_history(attendance_chart)
    plotting.plot_overtime_balance_history(days, history)


def main() -> None:
    parser = argparse.ArgumentParser(prog="recolul")
    subparsers = parser.add_subparsers(dest="command", required=True)

    balance_parser = subparsers.add_parser("balance", help="Calculate overtime balance")
    balance_parser.add_argument(
        "--exclude-last-day",
        action="store_true",
        help="Exclude last/current day from the calculation"
    )

    subparsers.add_parser("when", help="Calculate at which time to leave to avoid overtime this month")

    subparsers.add_parser("config", help="Init or update config")

    graph_parser = subparsers.add_parser("graph", help="Display a graph of overtime balance over the month")
    graph_parser.add_argument(
        "--exclude-last-day",
        action="store_true",
        help="Exclude last/current day from the graph"
    )

    args = parser.parse_args(sys.argv[1:])
    match args.command:
        case "balance":
            balance(exclude_last_day=args.exclude_last_day)
        case "when":
            when_to_leave()
        case "config":
            update_config()
        case "graph":
            graph(exclude_last_day=args.exclude_last_day)


def _get_attendance_chart() -> AttendanceChart:
    config = Config.from_env() or Config.load()
    if not config:
        raise RuntimeError(f"No config found")

    with RecoruSession(
        contract_id=config.recoru_contract_id,
        auth_id=config.recoru_auth_id,
        password=config.recoru_password
    ) as recoru_session:
        attendance_chart = recoru_session.get_attendance_chart()

    # Exclude rows which date is in the future
    current_day_of_month = datetime.now().day
    return [
        row for row in attendance_chart
        if row.day_of_month <= current_day_of_month
    ]


if __name__ == "__main__":
    main()
