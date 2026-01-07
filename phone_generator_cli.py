#!/usr/bin/env python3
# Developer: xorro
# URL: https://github.com/x-o-r-r-o/Bulk-Phone-Number-Generator
"""
CLI Mobile Phone Number Generator & Validator (non-interactive).

Requirements:

    pip install phonenumbers pycountry

Example usages:

1) Pure random:

    python phone_generator_cli.py \
      --country PK \
      --count 50 \
      --local-length 10

2) Fixed prefix (e.g. Pakistan '300' + random 7 digits):

    python phone_generator_cli.py \
      --country Pakistan \
      --count 50 \
      --local-length 10 \
      --serial-enabled \
      --serial-start 3000000000 \
      --fixed-prefix-len 3

3) Classic serial prefix/suffix:

    python phone_generator_cli.py \
      --country US \
      --count 20 \
      --local-length 10 \
      --serial-enabled \
      --serial-placement prefix \
      --serial-start 1000 \
      --serial-step 1
"""

import argparse
import sys
import time
from typing import Optional, List

from phone_core import (
    resolve_country,
    SerialConfig,
    warn_if_unrealistic_length,
    generate_numbers,
    build_csv_filename,
    save_to_csv,
)


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate random/serial mobile phone numbers for a country, "
                    "validate with phonenumbers, and save to a timestamped CSV."
    )

    parser.add_argument(
        "--country",
        required=True,
        help="Country identifier: ISO code (US), full name (United States), or calling code (+1 / 1).",
    )
    parser.add_argument(
        "--count",
        type=int,
        required=True,
        help="How many valid numbers to generate.",
    )
    parser.add_argument(
        "--local-length",
        type=int,
        required=True,
        help="Number of digits in the local part (without country code).",
    )

    # Serial / prefix options
    parser.add_argument(
        "--serial-enabled",
        action="store_true",
        help="Enable serial / prefix mode.",
    )
    parser.add_argument(
        "--serial-placement",
        choices=["prefix", "suffix"],
        default="suffix",
        help="Where to place the serial relative to random digits (default: suffix). "
             "Ignored if --fixed-prefix-len is used.",
    )
    parser.add_argument(
        "--serial-start",
        type=int,
        default=0,
        help="Starting serial value (integer >= 0). Also used as base for fixed-prefix mode.",
    )
    parser.add_argument(
        "--serial-step",
        type=int,
        default=1,
        help="Serial increment (integer >= 1). Ignored if --fixed-prefix-len is used.",
    )
    parser.add_argument(
        "--sequential-only",
        action="store_true",
        help="Use serial as the main generator (no random part). Ignored if --fixed-prefix-len is used.",
    )
    parser.add_argument(
        "--fixed-prefix-len",
        type=int,
        default=None,
        help=(
            "Use the first N digits of serial-start as a fixed prefix and fill "
            "the remaining digits randomly. Example: --serial-start 3000000000 "
            "--fixed-prefix-len 3 --local-length 10 -> 300XXXXXXX."
        ),
    )

    parser.add_argument(
        "--strict-length",
        action="store_true",
        help="Exit with error if local-length not in known possible lengths for region.",
    )
    parser.add_argument(
        "--filename-prefix",
        default="numbers",
        help="Custom prefix for the CSV filename (default: numbers).",
    )
    parser.add_argument(
        "--no-progress",
        action="store_true",
        help="Suppress progress output.",
    )

    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> None:
    args = parse_args(argv)

    if args.count <= 0:
        print("ERROR: --count must be a positive integer.")
        sys.exit(1)
    if args.local_length <= 0:
        print("ERROR: --local-length must be a positive integer.")
        sys.exit(1)
    if args.serial_step <= 0:
        print("ERROR: --serial-step must be >= 1.")
        sys.exit(1)
    if args.serial_start < 0:
        print("ERROR: --serial-start must be >= 0.")
        sys.exit(1)

    resolved = resolve_country(args.country, interactive=False)
    if not resolved:
        print(
            "ERROR: Could not resolve country from input. Try:\n"
            "  - 'US' or 'GB'\n"
            "  - 'United States' or 'Pakistan'\n"
            "  - '+1' or '44'\n"
        )
        sys.exit(1)

    region, calling_code, display_name = resolved
    print(
        f"Resolved country: {display_name} "
        f"(region: {region}, calling code: +{calling_code})"
    )

    try:
        warn_if_unrealistic_length(region, args.local_length, strict=args.strict_length)
    except ValueError as e:
        print(str(e))
        print("Strict length mode enabled; exiting.")
        sys.exit(1)

    # Build SerialConfig according to whether fixed-prefix mode is used
    serial_cfg = SerialConfig(
        enabled=args.serial_enabled,
        placement=args.serial_placement,
        start=args.serial_start,
        step=args.serial_step,
        sequential_only=args.sequential_only,
        fixed_prefix_len=args.fixed_prefix_len,
    )

    if serial_cfg.enabled:
        serial_str = str(args.serial_start)

        if args.fixed_prefix_len is not None:
            # Fixed prefix mode checks
            if args.fixed_prefix_len <= 0:
                print("ERROR: --fixed-prefix-len must be > 0.")
                sys.exit(1)
            if args.fixed_prefix_len > len(serial_str):
                print(
                    f"ERROR: --fixed-prefix-len ({args.fixed_prefix_len}) "
                    f"cannot exceed length of serial-start ({len(serial_str)})."
                )
                sys.exit(1)
            if args.fixed_prefix_len > args.local_length:
                print(
                    f"ERROR: fixed prefix length {args.fixed_prefix_len} "
                    f"exceeds local-part length {args.local_length}."
                )
                sys.exit(1)
        else:
            # Original serial length check
            if len(serial_str) > args.local_length:
                print(
                    f"ERROR: Serial start '{serial_str}' has {len(serial_str)} digits "
                    f"which exceeds the requested local-part length {args.local_length}."
                )
                sys.exit(1)

    start_time = time.time()
    rows = generate_numbers(
        region=region,
        calling_code=calling_code,
        count=args.count,
        local_length=args.local_length,
        serial_cfg=serial_cfg,
        verbose=not args.no_progress,
    )
    elapsed = time.time() - start_time

    if not rows:
        print("No valid numbers generated. Exiting.")
        sys.exit(1)

    filename = build_csv_filename(
        region=region,
        calling_code=calling_code,
        country_display_name=display_name,
        prefix=args.filename_prefix,
    )
    save_to_csv(filename, rows)

    print("\n---------------- Summary ----------------")
    print(f"Country: {display_name} ({region}), calling code: +{calling_code}")
    print(f"Requested: {args.count}")
    print(f"Valid unique numbers saved: {len(rows)}")
    print(f"CSV file: {filename}")
    print(f"Time taken: {elapsed:.2f} seconds")
    print("----------------------------------------")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted by user. Exiting.")
        sys.exit(1)