#!/usr/bin/env python3
# Developer: xorro
# URL: https://github.com/x-o-r-r-o/Bulk-Phone-Number-Generator
"""
Shared core logic for phone number generation & validation.

Requirements:

    pip install phonenumbers pycountry
"""

import csv
import random
from datetime import datetime
from typing import Optional, Tuple, Dict

import phonenumbers
from phonenumbers import NumberParseException, PhoneNumber
import pycountry


# ------------------------- Country Resolution -------------------------


def normalize_country_input(s: str) -> str:
    return s.strip()


def is_probably_calling_code(s: str) -> bool:
    s = s.strip()
    if s.startswith("+"):
        s = s[1:]
    return s.isdigit()


def resolve_country_from_name_or_iso(identifier: str) -> Optional[Tuple[str, int, str]]:
    """
    Resolve a country given ISO alpha-2 code or country name.

    Returns:
        (region_code, calling_code, display_name) or None
    """
    ident = identifier.strip()
    # Try ISO alpha-2 first
    if len(ident) == 2:
        country = pycountry.countries.get(alpha_2=ident.upper())
        if country:
            region = country.alpha_2.upper()
            calling_code = phonenumbers.country_code_for_region(region)
            if calling_code == 0:
                return None
            return region, calling_code, country.name

    # Try by name (case-insensitive, fuzzy)
    try:
        matches = pycountry.countries.search_fuzzy(ident)
        if not matches:
            return None
        country = matches[0]
        region = country.alpha_2.upper()
        calling_code = phonenumbers.country_code_for_region(region)
        if calling_code == 0:
            return None
        return region, calling_code, country.name
    except LookupError:
        return None


def resolve_country_from_calling_code(
    code_str: str,
    *,
    interactive: bool = False,
) -> Optional[Tuple[str, int, str]]:
    """
    Resolve a country from a calling code like '+44' or '44'.

    If multiple regions share the code:
      - interactive=True: prompt user to choose.
      - interactive=False: pick the first region.
    """
    s = code_str.strip()
    if s.startswith("+"):
        s = s[1:]
    if not s.isdigit():
        return None

    calling_code = int(s)
    regions = phonenumbers.region_codes_for_country_code(calling_code)
    if not regions:
        return None

    if len(regions) == 1 or not interactive:
        region = regions[0]
        country = pycountry.countries.get(alpha_2=region)
        display_name = country.name if country else region
        return region, calling_code, display_name

    # Interactive selection
    print(f"Calling code +{calling_code} is shared by multiple regions:")
    options = []
    for r in regions:
        country = pycountry.countries.get(alpha_2=r)
        name = country.name if country else r
        options.append((r, name))

    for idx, (_, name) in enumerate(options, start=1):
        print(f"  {idx}. {name}")

    while True:
        choice = input(f"Select region (1-{len(options)}) [default 1]: ").strip()
        if choice == "":
            idx = 1
        elif choice.isdigit():
            idx = int(choice)
        else:
            print("Please enter a number.")
            continue

        if 1 <= idx <= len(options):
            region, name = options[idx - 1]
            return region, calling_code, name
        else:
            print("Invalid choice, try again.")


def resolve_country(identifier: str, *, interactive: bool = False) -> Optional[Tuple[str, int, str]]:
    """
    Resolve any of:
        - ISO 2-letter code (US, GB, PK, etc.)
        - Full country name ("United States")
        - Calling code ("+1", "44")

    Returns:
        (region_code, calling_code, display_name) or None
    """
    identifier = normalize_country_input(identifier)
    if not identifier:
        return None

    if is_probably_calling_code(identifier):
        result = resolve_country_from_calling_code(identifier, interactive=interactive)
        if result:
            return result

    result = resolve_country_from_name_or_iso(identifier)
    return result


# ------------------------- Serial Mode Logic -------------------------


class SerialConfig:
    def __init__(
        self,
        enabled: bool = False,
        placement: str = "suffix",
        start: int = 0,
        step: int = 1,
        sequential_only: bool = False,
        fixed_prefix_len: Optional[int] = None,
    ):
        """
        fixed_prefix_len:
            - If not None: use the first N digits of `start` as a fixed prefix,
              and fill the remaining local-part digits randomly.
              In this mode, placement is effectively 'prefix' and serial does not increment.
        """
        self.enabled = enabled
        self.placement = placement  # "prefix" or "suffix"
        self.start = start
        self.step = step
        self.sequential_only = sequential_only
        self.fixed_prefix_len = fixed_prefix_len
        self._current = start

    def next_serial_str(self) -> str:
        val = self._current
        self._current += self.step
        return str(val)


# ------------------------- Generation & Validation -------------------------


def warn_if_unrealistic_length(region: str,
                               local_length: int,
                               *,
                               strict: bool = False) -> None:
    """
    Use metadata to see possible national number lengths.
    If unrealistic, print warning and optionally raise ValueError if strict=True.
    """
    meta = phonenumbers.PhoneMetadata.metadata_for_region(region, None)
    possible_lengths = None
    if meta and meta.general_desc:
        if meta.general_desc.possible_length:
            possible_lengths = list(meta.general_desc.possible_length)

    if not possible_lengths:
        return

    if local_length not in possible_lengths:
        msg = (
            f"WARNING: Requested local-part length ({local_length}) does not "
            f"match common lengths for region {region}: {sorted(possible_lengths)}"
        )
        if strict:
            raise ValueError(msg)
        else:
            print(msg)


def build_local_part(local_length: int,
                     serial_cfg: SerialConfig) -> str:
    """
    Build a candidate local part (digits only) based on serial config.

    Supports:
      - Plain random digits (serial disabled)
      - Serial prefix/suffix with optional sequential-only
      - Fixed prefix mode: use first N digits of start as prefix, random rest
    """
    if not serial_cfg.enabled:
        # Pure random digits
        return "".join(random.choices("0123456789", k=local_length))

    # ----- Fixed prefix mode -----
    if serial_cfg.fixed_prefix_len is not None:
        base_serial_str = str(serial_cfg.start)
        prefix_len = serial_cfg.fixed_prefix_len

        if prefix_len <= 0 or prefix_len > len(base_serial_str):
            raise ValueError(
                f"Invalid fixed_prefix_len={prefix_len} for start={base_serial_str}"
            )

        prefix = base_serial_str[:prefix_len]
        if prefix_len > local_length:
            raise ValueError(
                f"Fixed prefix '{prefix}' length {prefix_len} exceeds local length {local_length}"
            )

        remaining_len = local_length - prefix_len
        random_part = "".join(random.choices("0123456789", k=remaining_len))
        # In fixed-prefix mode, placement is effectively forced to 'prefix'
        return prefix + random_part

    # ----- Original serial behavior -----
    serial_str = serial_cfg.next_serial_str()
    serial_len = len(serial_str)
    if serial_len > local_length:
        raise ValueError(
            f"Serial '{serial_str}' length {serial_len} exceeds local length {local_length}"
        )

    if serial_cfg.sequential_only:
        # Entire local part is serial, but must fit exactly or be padded.
        if serial_len < local_length:
            serial_str = serial_str.zfill(local_length)
        return serial_str

    # Mixed serial + random digits
    remaining_len = local_length - serial_len
    random_part = "".join(random.choices("0123456789", k=remaining_len))
    if serial_cfg.placement == "prefix":
        return serial_str + random_part
    else:
        return random_part + serial_str


def generate_numbers(region: str,
                     calling_code: int,
                     count: int,
                     local_length: int,
                     serial_cfg: SerialConfig,
                     *,
                     verbose: bool = True) -> Dict[str, Dict[str, str]]:
    """
    Generate and validate numbers.

    Returns:
        dict mapping e164_number -> row_data
    """
    valid_numbers: Dict[str, Dict[str, str]] = {}
    attempts = 0
    max_attempts = count * 10
    start_time = datetime.now().isoformat(timespec="seconds")

    if verbose:
        print("\nStarting generation...")
        print(f"Target valid numbers: {count}")
        print(f"Max attempts: {max_attempts}\n")

    while len(valid_numbers) < count and attempts < max_attempts:
        attempts += 1
        try:
            local_part = build_local_part(local_length, serial_cfg)
        except ValueError as e:
            print(f"ERROR during generation: {e}")
            print("Serial/fixed-prefix overflowed the allotted local-part length.")
            break

        full_number_str = f"+{calling_code}{local_part}"

        try:
            parsed: PhoneNumber = phonenumbers.parse(full_number_str, region)
            if not phonenumbers.is_possible_number(parsed):
                continue
            if not phonenumbers.is_valid_number(parsed):
                continue
        except NumberParseException:
            continue

        e164 = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
        national_number = str(parsed.national_number)

        if e164 in valid_numbers:
            continue

        row = {
            "e164_number": e164,
            "national_number": national_number,
            "country_iso": region,
            "country_calling_code": str(calling_code),
            "generation_timestamp": start_time,
        }
        valid_numbers[e164] = row

        if verbose and (len(valid_numbers) % max(1, count // 10) == 0 or len(valid_numbers) == count):
            print(
                f"Progress: {len(valid_numbers)}/{count} valid "
                f"(attempts: {attempts})"
            )

    if verbose:
        if len(valid_numbers) < count:
            print(
                f"\nReached attempt limit ({attempts} attempts). "
                f"Generated {len(valid_numbers)} valid numbers out of requested {count}."
            )
        else:
            print(f"\nCompleted generation: {len(valid_numbers)} valid numbers.")

    return valid_numbers


# ------------------------- CSV Output -------------------------


def sanitize_country_for_filename(name_or_iso: str) -> str:
    return "".join(ch for ch in name_or_iso if ch.isalnum())


def build_csv_filename(region: str,
                       calling_code: int,
                       country_display_name: str,
                       *,
                       prefix: str = "numbers") -> str:
    country_part = region.upper() if len(region) == 2 else sanitize_country_for_filename(
        country_display_name.replace(" ", "")
    )
    code_part = str(calling_code)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{country_part}{code_part}_{ts}.csv"


def save_to_csv(filename: str, rows: Dict[str, Dict[str, str]]) -> None:
    fieldnames = [
        "e164_number",
        "national_number",
        "country_iso",
        "country_calling_code",
        "generation_timestamp",
    ]
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows.values():
            writer.writerow(row)