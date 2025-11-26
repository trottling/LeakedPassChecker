import random
from pathlib import Path

from faker import Faker
from openpyxl import Workbook


BASE_DIR = Path(__file__).resolve().parent
EXAMPLES_DIR = BASE_DIR / "examples"


fake = Faker("ru_RU")


def ensure_examples_dir() -> None:
    EXAMPLES_DIR.mkdir(parents=True, exist_ok=True)


def generate_entrances_xlsx(path: Path, employees: list[dict], days: int = 3) -> None:
    wb = Workbook()
    ws = wb.active
    ws.title = "Проходная"

    # header rows to match load_entrances()
    ws.append([])
    ws.append([])
    ws.append([])
    ws.append([])
    ws.append([])
    ws.append([])
    ws.append(["дата", "отдел", "фио", "таб. №", "события", ""])
    ws.append(["", "", "", "", "", ""])

    for _ in range(days):
        date = fake.date_this_year()
        for emp in employees:
            events_in = [f"{fake.time()[:5]} ({random.randint(1, 5)})"]
            events_out = [f"{fake.time()[:5]} ({random.randint(1, 5)})"]

            ws.append(
                [
                    date.strftime("%Y-%m-%d"),
                    emp["department"],
                    emp["fio"],
                    emp["tab_number"],
                    " / ".join(events_in),
                    " / ".join(events_out),
                ]
            )

    wb.save(path)


def generate_logins_xlsx(path: Path, employees: list[dict], rows_per_employee: int = 3) -> None:
    wb = Workbook()
    ws = wb.active
    ws.title = "Логины"

    # rows before header (1..10)
    for _ in range(10):
        ws.append([])

    headers = [
        "user name",
        "client host name",
        "logon time",
        "event type text",
        "failure reason",
        "message",
        "user display name",
        "user distinguish name",
    ]
    ws.append(headers)

    for emp in employees:
        for _ in range(rows_per_employee):
            user_name = emp["login"]
            host = f"PC-{fake.random_uppercase_letter()}{random.randint(100, 999)}"
            logon_time = fake.date_time_this_year().strftime("%Y-%m-%d %H:%M:%S")
            event_type = random.choice(["Logon", "Logoff"])
            failure_reason = ""
            message = random.choice(
                [
                    "User logon successful",
                    "User initiated logoff",
                    "Kerberos authentication ticket granted",
                ]
            )
            user_display_name = emp["fio"]
            user_dn = f"CN={emp['fio']},OU=Users,DC=example,DC=local"

            ws.append(
                [
                    user_name,
                    host,
                    logon_time,
                    event_type,
                    failure_reason,
                    message,
                    user_display_name,
                    user_dn,
                ]
            )

    wb.save(path)


def generate_fired_list(path: Path, employees: list[dict], count: int = 5) -> None:
    fired = random.sample(employees, k=min(count, len(employees)))
    with path.open("w", encoding="utf-8") as f:
        for emp in fired:
            f.write(emp["fio"] + "\n")


def generate_exceptions_list(path: Path) -> None:
    patterns = [
        "*админ*",
        "*сервис*",
        "svc_*",
        "*test*",
        "*vpn*",
        "*service*",
    ]
    with path.open("w", encoding="utf-8") as f:
        for p in patterns:
            f.write(p + "\n")


def generate_employees(count: int = 30) -> list[dict]:
    employees: list[dict] = []
    for i in range(count):
        fio = fake.name()
        department = f"{random.randint(1000, 9999)}"
        tab_number = f"{random.randint(1000, 9999)}-{random.randint(1000, 9999)}"
        login = fake.user_name()
        employees.append(
            {
                "fio": fio,
                "department": department,
                "tab_number": tab_number,
                "login": login,
            }
        )
    return employees


def main() -> None:
    ensure_examples_dir()

    employees = generate_employees(10000)

    entrances_path = EXAMPLES_DIR / "entrance_test.xlsx"
    logins_path = EXAMPLES_DIR / "logins_test.xlsx"
    fired_path = EXAMPLES_DIR / "fired_test.txt"
    exceptions_path = EXAMPLES_DIR / "exceptions_test.txt"

    generate_entrances_xlsx(entrances_path, employees)
    generate_logins_xlsx(logins_path, employees)
    generate_fired_list(fired_path, employees)
    generate_exceptions_list(exceptions_path)


if __name__ == "__main__":
    main()


