from __future__ import annotations

import argparse
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Iterable, List, Sequence

from faker import Faker
from openpyxl import Workbook

LOGINS_HEADER = (
    "User Name",
    "Client Host Name",
    "Logon Time",
    "Event Type Text",
    "Failure Reason",
    "Message",
    "User Display Name",
    "User Distinguish Name",
)

ENTRANCE_HEADER = ("ФИО", "Дата", "Время входа", "Время выхода", "Статус")


def _build_full_name(faker: Faker) -> str:
    """Генерирует ФИО, чтобы оно лучше подходило под ожидаемый формат."""
    if faker.random.random() < 0.5:
        last = faker.last_name_male()
        first = faker.first_name_male()
        middle = faker.middle_name_male()
    else:
        last = faker.last_name_female()
        first = faker.first_name_female()
        middle = faker.middle_name_female()
    return f"{last} {first} {middle}"


def _unique_names(faker: Faker, count: int, used: set[str]) -> List[str]:
    names: List[str] = []
    while len(names) < count:
        name = _build_full_name(faker)
        if name not in used:
            used.add(name)
            names.append(name)
    return names


def _generate_logins(
    faker: Faker, names: Sequence[str], base_date: datetime
) -> tuple[list[tuple], list[str]]:
    logins: list[tuple] = []
    hosts: list[str] = []

    for name in names:
        logon_time = faker.date_time_between(
            start_date=base_date,
            end_date=base_date + timedelta(days=1),
        )
        host = faker.hostname()
        hosts.append(host)

        logins.append(
            (
                faker.user_name(),
                host,
                logon_time.strftime("%d/%m/%Y %I:%M:%S %p"),
                "Success",
                "-",
                "Login successful",
                name,
                f"CN={name}",
            )
        )

    return logins, hosts


def _generate_entrances(
    faker: Faker, names: Sequence[str], base_date: datetime
) -> list[tuple]:
    entrances: list[tuple] = []
    for name in names:
        enter_time = faker.date_time_between(
            start_date=base_date + timedelta(hours=6),
            end_date=base_date + timedelta(hours=11),
        )
        exit_time = enter_time + timedelta(hours=random.randint(7, 10), minutes=random.randint(0, 59))
        entrances.append(
            (
                name,
                enter_time.strftime("%Y-%m-%d"),
                enter_time.strftime("%H:%M"),
                exit_time.strftime("%H:%M"),
                "Вход",
            )
        )
    return entrances


def _write_workbook(rows: Iterable[tuple], header: Sequence[str], path: Path, title: str) -> None:
    wb = Workbook()
    ws = wb.active
    ws.title = title
    ws.append(tuple(header))
    for row in rows:
        ws.append(tuple(row))
    wb.save(path)


def _write_text_file(lines: Iterable[str], path: Path) -> None:
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _build_exception_patterns(names: Sequence[str], hosts: Sequence[str], faker: Faker) -> list[str]:
    patterns: set[str] = set()

    sampled_names = random.sample(names, k=min(len(names), 4)) if names else []
    for name in sampled_names:
        last = name.split()[0]
        patterns.add(f"{last} *")
        patterns.add(f"*{last[:3]}*")

    if hosts:
        sample_host = random.choice(hosts)
        patterns.add(f"{sample_host.split('.')[0]}-*")

    patterns.add(faker.bothify(text="prod-??-**"))
    return list(patterns)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Генерация тестовых таблиц с Faker")
    parser.add_argument(
        "--output-dir",
        default=Path("generated"),
        type=Path,
        help="Папка, куда сохранять файлы",
    )
    parser.add_argument("--login-count", type=int, default=25, help="Количество записей логинов")
    parser.add_argument(
        "--entrance-count", type=int, default=20, help="Количество записей в журнале проходной"
    )
    parser.add_argument(
        "--seed", type=int, default=42, help="Зёрно генератора для воспроизводимости"
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    random.seed(args.seed)
    faker = Faker("ru_RU")
    faker.seed_instance(args.seed)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    base_date = datetime.combine(datetime.now().date(), datetime.min.time())

    shared_count = min(args.login_count, args.entrance_count) // 2
    used_names: set[str] = set()

    shared_names = _unique_names(faker, shared_count, used_names)
    login_names = shared_names + _unique_names(faker, args.login_count - shared_count, used_names)
    entrance_names = shared_names + _unique_names(
        faker, args.entrance_count - shared_count, used_names
    )

    logins, hosts = _generate_logins(faker, login_names, base_date)
    entrances = _generate_entrances(faker, entrance_names, base_date)

    _write_workbook(
        logins,
        LOGINS_HEADER,
        args.output_dir / "logins_generated.xlsx",
        title="Logins",
    )
    _write_workbook(
        entrances,
        ENTRANCE_HEADER,
        args.output_dir / "entrance_generated.xlsx",
        title="Entrance",
    )

    _write_text_file(
        _build_exception_patterns(login_names, hosts, faker),
        args.output_dir / "exceptions_generated.txt",
    )

    fired_candidates = random.sample(login_names, k=min(len(login_names), 3))
    _write_text_file(fired_candidates, args.output_dir / "fired_generated.txt")

    print(f"Создано: {args.output_dir.resolve()}")
    print(" - logins_generated.xlsx")
    print(" - entrance_generated.xlsx")
    print(" - exceptions_generated.txt")
    print(" - fired_generated.txt")


if __name__ == "__main__":
    main()