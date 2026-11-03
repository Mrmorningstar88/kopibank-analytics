"""Собирает отчёт по воронке.

  python run_report.py --days 90                 # данные из API
  python run_report.py --csv samples/demo.csv    # данные из выгрузки CSV
"""

import argparse
import csv
import datetime as dt
import pathlib

from kopibank.funnel import render_markdown


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--csv", help="CSV-выгрузка заявок вместо API")
    p.add_argument("--days", type=int, default=90, help="период для API, дней назад")
    p.add_argument("--out", default="report/funnel.md")
    args = p.parse_args()

    if args.csv:
        with open(args.csv, newline="", encoding="utf-8") as f:
            apps = list(csv.DictReader(f))
    else:
        from kopibank.client import fetch_applications
        today = dt.date.today()
        apps = fetch_applications(
            date_from=(today - dt.timedelta(days=args.days)).isoformat(),
            date_to=today.isoformat(),
        )

    out = pathlib.Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render_markdown(apps), encoding="utf-8")
    print(f"Отчёт: {out} ({len(apps)} заявок)")


if __name__ == "__main__":
    main()
