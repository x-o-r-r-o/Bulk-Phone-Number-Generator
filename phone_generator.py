#!/usr/bin/env python3
# Developer: xorro
# URL: https://github.com/x-o-r-r-o/Bulk-Phone-Number-Generator
"""
Interactive mobile phone number generator with validation and CSV export.

Requirements:

    pip install phonenumbers pycountry

This script uses the shared core module: phone_core.py
"""

import sys
import time
from typing import Optional

from phone_core import (
    resolve_country,
    SerialConfig,
    warn_if_unrealistic_length,
    generate_numbers,
    build_csv_filename,
    save_to_csv,
)


# ------------------------- Input Helpers -------------------------


def input_int(prompt: str, min_value: Optional[int] = None,
              max_value: Optional[int] = None) -> int:
    while True:
        val = input(prompt).strip()
        if not val:
            print("Input cannot be empty.")
            continue
        if not val.isdigit():
            print("Please enter a valid integer.")
            continue
        num = int(val)
        if min_value is not None and num < min_value:
            print(f"Value must be >= {min_value}.")
            continue
        if max_value is not None and num > max_value:
            print(f"Value must be <= {max_value}.")
            continue
        return num


def input_yes_no(prompt: str, default: Optional[bool] = None) -> bool:
    while True:
        val = input(prompt).strip().lower()
        if val == "" and default is not None:
            return default
        if val in ("y", "yes"):
            return True
        if val in ("n", "no"):
            return False
        print("Please answer with 'y' or 'n'.")


def input_choice(prompt: str, choices: list, case_insensitive: bool = True) -> str:
    normalized_choices = [c.lower() for c in choices] if case_insensitive else choices
    while True:
        val = input(prompt).strip()
        if case_insensitive:
            vnorm = val.lower()
            if vnorm in normalized_choices:
                return choices[normalized_choices.index(vnorm)]
        else:
            if val in choices:
                return val
        print(f"Invalid choice. Allowed: {', '.join(choices)}")


# ------------------------- Serial Config (interactive) -------------------------


def configure_serial(local_length: int) -> SerialConfig:
    use_serial = input_yes_no("Use serial / prefix mode? (y/n): ", default=False)
    if not use_serial:
        return SerialConfig(enabled=False)

    # Ask if user wants fixed-prefix mode
    use_fixed_prefix = input_yes_no(
        "Use only first N digits of serial as fixed prefix and randomize the rest? (y/n): ",
        default=False
    )

    if use_fixed_prefix:
        start_serial = input_int("Start serial (integer, e.g. 3000000000): ", min_value=0)
        max_prefix_len = len(str(start_serial))
        fixed_prefix_len = input_int(
            f"How many leading digits to keep as fixed prefix? (1-{max_prefix_len}): ",
            min_value=1,
            max_value=max_prefix_len
        )
        if fixed_prefix_len > local_length:
            print(
                f"ERROR: fixed prefix length {fixed_prefix_len} exceeds "
                f"local-part length {local_length}."
            )
            return configure_serial(local_length)

        # In fixed-prefix mode, placement is effectively 'prefix', step and sequential_only unused
        return SerialConfig(
            enabled=True,
            placement="prefix",
            start=start_serial,
            step=1,
            sequential_only=False,
            fixed_prefix_len=fixed_prefix_len,
        )

    # Original serial behavior
    placement = input_choice(
        "Serial placement (prefix/suffix): ",
        ["prefix", "suffix"]
    )
    start_serial = input_int("Start serial (integer >= 0): ", min_value=0)
    step = input_int("Serial increment (integer >= 1) [default 1]: ", min_value=1)
    sequential_only = input_yes_no(
        "Use serial as main (sequential) generator (no random part)? (y/n): ",
        default=False
    )

    serial_cfg = SerialConfig(
        enabled=True,
        placement=placement,
        start=start_serial,
        step=step,
        sequential_only=sequential_only,
        fixed_prefix_len=None,
    )

    serial_str = str(start_serial)
    if len(serial_str) > local_length:
        print(
            f"ERROR: Serial '{serial_str}' has {len(serial_str)} digits which "
            f"exceeds the requested local-part length {local_length}."
        )
        print("Please reduce serial start value or increase local-part length.")
        return configure_serial(local_length)

    return serial_cfg


# ------------------------- File Overwrite Helper -------------------------


def confirm_overwrite(filename: str) -> bool:
    try:
        with open(filename, "r"):
            pass
    except FileNotFoundError:
        return True  # no file, safe to create

    print(f"\nFile '{filename}' already exists.")
    return input_yes_no("Overwrite? (y/n): ", default=False)


# ------------------------- Main -------------------------


def main() -> None:
    print("--------------------------------------------------")
    print(" Mobile Phone Number Generator & Validator")
    print("--------------------------------------------------")
    print("Before running, install dependencies:")
    print("    pip install phonenumbers pycountry")
    print("--------------------------------------------------\n")

    # Country resolution (interactive)
    while True:
        country_input = input(
            "Enter country (ISO code, calling code, or full name): "
        ).strip()
        resolved = resolve_country(country_input, interactive=True)
        if not resolved:
            print(
                "Could not resolve country. Examples of valid inputs:\n"
                "  - 'US' or 'GB'\n"
                "  - 'United States' or 'Pakistan'\n"
                "  - '+1' or '44'\n"
            )
            continue

        region, calling_code, display_name = resolved
        print(
            f"Selected country: {display_name} "
            f"(region: {region}, calling code: +{calling_code})"
        )
        confirm = input_yes_no("Is this correct? (y/n): ", default=True)
        if confirm:
            break

    n = input_int("How many numbers to generate? ", min_value=1)
    local_length = input_int(
        "How many digits in the local part (without country code)? ",
        min_value=1,
    )

    # Warn but let user decide
    try:
        warn_if_unrealistic_length(region, local_length, strict=False)
    except Exception:
        pass

    serial_cfg = configure_serial(local_length)

    start = time.time()
    rows = generate_numbers(region, calling_code, n, local_length, serial_cfg, verbose=True)
    elapsed = time.time() - start

    if not rows:
        print("\nNo valid numbers generated. Nothing to save.")
        return

    filename = build_csv_filename(region, calling_code, display_name, prefix="numbers")
    if not confirm_overwrite(filename):
        print("User declined overwrite. Aborting save.")
        return

    save_to_csv(filename, rows)

    print("\n---------------- Summary ----------------")
    print(f"Country: {display_name} ({region}), calling code: +{calling_code}")
    print(f"Requested: {n}")
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