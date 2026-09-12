"""Build the public schedule snapshot from two read-only published CSV tabs."""

import csv
import io
import json
import os
from datetime import date
from pathlib import Path
from urllib.request import Request, urlopen

OUTPUT = Path(__file__).resolve().parents[1] / "data" / "schedule.json"


def read_rows(csv_text, expected_headers):
    reader = csv.DictReader(io.StringIO(csv_text.lstrip("\ufeff")))
    if reader.fieldnames != expected_headers:
        raise ValueError(f"CSV columns must be: {', '.join(expected_headers)}")
    return list(reader)


def valid_date(value):
    # Require the same sortable date format on both tabs.
    parsed = date.fromisoformat(value)
    if parsed.isoformat() != value:
        raise ValueError(f"Invalid date format: {value}")
    return value


def build_schedule(events_csv, bookings_csv):
    events = []
    for row in read_rows(events_csv, ["日付", "内容", "時間", "会場", "補足", "表示"]):
        if not any(row.values()) or row["表示"].strip() == "非公開":
            continue
        if row["表示"].strip() != "公開":
            raise ValueError("開催日程の表示は「公開」か「非公開」を選択してください")
        event_date = valid_date(row["日付"].strip())
        title = row["内容"].strip()
        if not title:
            raise ValueError(f"開催日程 {event_date} の内容が空欄です")
        events.append({"date": event_date, "title": title, "time": row["時間"].strip(),
                       "place": row["会場"].strip(), "note": row["補足"].strip()})

    bookings = []
    for row in read_rows(bookings_csv, ["日付", "時間", "状態", "表示"]):
        if not any(row.values()) or row["表示"].strip() == "非公開":
            continue
        if row["表示"].strip() != "公開":
            raise ValueError("予約空き枠の表示は「公開」か「非公開」を選択してください")
        slot_date = valid_date(row["日付"].strip())
        time, status = row["時間"].strip(), row["状態"].strip()
        if not time or status not in {"空きあり", "満席", "受付終了"}:
            raise ValueError(f"予約空き枠 {slot_date} の時間または状態を確認してください")
        bookings.append({"date": slot_date, "time": time, "status": status})

    events.sort(key=lambda row: row["date"])
    bookings.sort(key=lambda row: row["date"])
    return {"events": events, "bookings": bookings}


def download(url):
    if not url.startswith("https://docs.google.com/spreadsheets/"):
        raise ValueError("公開CSVのGoogleスプレッドシートURLを設定してください")
    request = Request(url, headers={"User-Agent": "BASIC-Schedule-Sync/1.0"})
    with urlopen(request, timeout=20) as response:
        return response.read().decode("utf-8-sig")


def main():
    event_url = os.environ["BASIC_EVENTS_CSV_URL"]
    booking_url = os.environ["BASIC_BOOKINGS_CSV_URL"]
    content = build_schedule(download(event_url), download(booking_url))
    # Both tabs must parse successfully before the public snapshot is replaced.
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    temporary = OUTPUT.with_suffix(".tmp")
    temporary.write_text(json.dumps(content, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(OUTPUT)


if __name__ == "__main__":
    main()
