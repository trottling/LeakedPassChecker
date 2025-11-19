import csv
import json


def flatten_result(result):
    rows = []

    def collect(category, entries):
        for entry in entries:
            rows.append({
                "category": category,
                "user": entry.get("user"),
                "logins_rows": entry.get("logins_rows", []),
                "entrance_rows": entry.get("entrance_rows", []),
                "logins_rows_count": len(entry.get("logins_rows") or []),
                "entrance_rows_count": len(entry.get("entrance_rows") or []),
                })

    collect("compromised", result.compromised)
    collect("matched", result.matched)
    collect("no_matches", result.no_matches)
    return rows


def export_to_csv(result, path):
    rows = flatten_result(result)

    fieldnames = [
        "category",
        "user",
        "logins_rows_count",
        "entrance_rows_count",
        "logins_rows",
        "entrance_rows",
        ]

    with open(path, "w", encoding="utf-8", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({
                "category": row["category"],
                "user": row["user"],
                "logins_rows_count": row["logins_rows_count"],
                "entrance_rows_count": row["entrance_rows_count"],
                "logins_rows": json.dumps(row["logins_rows"], ensure_ascii=False, default=str),
                "entrance_rows": json.dumps(row["entrance_rows"], ensure_ascii=False, default=str),
                })
