import json


def build_payload(result):
    return {
        "stats": {
            "compromised": result.compromised_count,
            "matched": result.matched_count,
            "no_matches": result.no_matches_count,
            },
        "compromised": result.compromised,
        "matched": result.matched,
        "no_matches": result.no_matches,
        }


def export_to_json(result, path):
    payload = build_payload(result)

    with open(path, "w", encoding="utf-8") as json_file:
        json.dump(payload, json_file, ensure_ascii=False, indent=2, default=str)
