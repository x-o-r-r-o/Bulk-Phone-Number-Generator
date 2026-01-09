#!/usr/bin/env python3
import csv
import argparse
from pathlib import Path

COLUMN_NAME = "e164_number"

def process_file(input_csv: Path, output_txt: Path):
    numbers = []

    with input_csv.open(mode="r", newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)

        if COLUMN_NAME not in reader.fieldnames:
            raise ValueError(
                f"Column '{COLUMN_NAME}' not found in CSV header: {reader.fieldnames}"
            )

        for row in reader:
            raw = (row.get(COLUMN_NAME) or "").strip()
            if not raw:
                continue

            if not raw.startswith("+"):
                raw = "+" + raw

            numbers.append(raw)

    with output_txt.open(mode="w", encoding="utf-8") as txtfile:
        for num in numbers:
            txtfile.write(num + "\n")

    print(f"Exported {len(numbers)} numbers from '{input_csv}' to '{output_txt}'.")


def main():
    parser = argparse.ArgumentParser(
        description="Export e164_number column from CSV, add '+' prefix, and save to a text file."
    )
    parser.add_argument(
        "csv_path",
        nargs="?",
        help="Path to input CSV file (if omitted, you will be prompted).",
    )
    parser.add_argument(
        "-o", "--output",
        help="Path to output text file (default: same folder as CSV, 'numbers.txt').",
    )

    args = parser.parse_args()

    if not args.csv_path:
        args.csv_path = input("Enter path to CSV file: ").strip()

    input_csv = Path(args.csv_path).expanduser().resolve()

    if not input_csv.is_file():
        raise FileNotFoundError(f"CSV file not found: {input_csv}")

    if args.output:
        output_txt = Path(args.output).expanduser().resolve()
    else:
        output_txt = input_csv.with_name("numbers.txt")

    process_file(input_csv, output_txt)


if __name__ == "__main__":
    main()