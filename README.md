# Bulk Phone Number Generator

Bulk Phone Number Generator is a Python-based tool for generating and validating large sets of realistic phone numbers for any country. It uses the [`phonenumbers`](https://github.com/daviddrysdale/python-phonenumbers) library to ensure numbers conform to real-world formats and exports them to CSV for easy use in testing, QA, and data workflows.

> Developer: **xorro**  
> URL: https://github.com/x-o-r-r-o/Bulk-Phone-Number-Generator

---

## Features

- ✅ **Country-aware validation** using `phonenumbers`
- ✅ **Multiple country input formats**:
  - ISO codes: `US`, `GB`, `PK`
  - Full names: `United States`, `Pakistan`
  - Calling codes: `+1`, `44`
- ✅ **Generation modes**
  - Pure random numbers
  - Serial numbers (sequential, prefix, or suffix)
  - Fixed prefix + random tail (e.g. `300` + `XXXXXXX` for Pakistan)
- ✅ **CSV export** with:
  - E.164 formatted number (e.g. `+923004736218`)
  - National number
  - Country ISO code
  - Country calling code
  - Generation timestamp
- ✅ **Two interfaces**
  - Interactive CLI (`phone_generator.py`)
  - Argument-based CLI (`phone_generator_cli.py`)
- ✅ **Configurable validation strictness** for local number lengths

---

## Project Structure

```text
.
├─ phone_core.py              # Shared core logic (generation, validation, CSV)
├─ phone_generator.py         # Interactive CLI
├─ phone_generator_cli.py     # Non-interactive CLI with arguments
└─ requirements.txt           # Python dependencies
```

## Requirements

- Python 3.8+ (recommended)
- Packages:
  - phonenumbers
  - pycountry

Install dependencies:
 ```text
pip install -r requirements.txt
```
or manually:
 ```text
pip install phonenumbers pycountry
```
## Usage

You can use either:
- The interactive generator (phone_generator.py)
- The non-interactive CLI (phone_generator_cli.py)

**1. Interactive Generator**
Run:
 ```text
python phone_generator.py
```
You will be prompted step by step.

**1.1. Country selection**

You can type:
- ISO code: US
- Name: United States
- Calling code: +1 or 1

Example:
 ```text
Enter country (ISO code, calling code, or full name): United States
Selected country: United States (region: US, calling code: +1)
Is this correct? (y/n): y
```

**1.2. Number count and local-part length**
 ```text
How many numbers to generate? 50
How many digits in the local part (without country code)? 10
```
> _The tool may warn if the local-part length doesn’t match common lengths for that region, but you can still proceed._

**1.3. Serial / prefix configuration**
You can choose between:
- No serial (pure random)
- Fixed prefix mode
- Classic serial prefix/suffix

**Prompt flow:**
 ```text
Use serial / prefix mode? (y/n): y
Use only first N digits of serial as fixed prefix and randomize the rest? (y/n): y
Start serial (integer, e.g. 3000000000): 3000000000
How many leading digits to keep as fixed prefix? (1-10): 3
```

This configuration:
- Uses 300 as a fixed prefix
- Fills remaining 7 digits randomly for a 10-digit local part
- Example generated local numbers: 3004736218, 3009123456, etc.

If you answer n to fixed prefix mode, you’ll see classic serial options:
 ```text
Serial placement (prefix/suffix): prefix
Start serial (integer >= 0): 1000
Serial increment (integer >= 1) [default 1]: 1
Use serial as main (sequential) generator (no random part)? (y/n): n
```

Behavior:
- Local part is a mix of serial + random digits.
- Placement controls whether the serial is at the start or end.

**1.4. Output and CSV**
After generation, you’ll see a summary and a CSV file will be created:
 ```text
---------------- Summary ----------------
Country: United States (US), calling code: +1
Requested: 50
Valid unique numbers saved: 50
CSV file: numbers_US1_20260101_120000.csv
Time taken: 0.42 seconds
----------------------------------------
```

## 2. Non-interactive CLI
Use phone_generator_cli.py when you want to script or automate generation.

Show help:
 ```text
python phone_generator_cli.py --help
```
Key arguments:
- --country – ISO code, full name, or calling code
- --count – how many valid numbers to generate
- --local-length – number of digits in the local part (without country code)
- Serial / prefix options:
  - --serial-enabled
  - --serial-placement (prefix / suffix)
  - --serial-start
  - --serial-step
  - --sequential-only
  - --fixed-prefix-len
 
- Other:
  - --strict-length – enforce typical length for the region
  - --filename-prefix – CSV filename prefix
  - --no-progress – hide progress output

 **2.1. Example: pure random numbers (United States)**
  ```text
python phone_generator_cli.py \
  --country United States \
  --count 100 \
  --local-length 10
```
Generates 100 valid United States numbers with 10-digit local parts, fully random.

**2.2. Example: fixed prefix for Pakistan (300 + random)**
Use --serial-enabled, --serial-start, and --fixed-prefix-len:
  ```text
python phone_generator_cli.py \
  --country Pakistan \
  --count 50 \
  --local-length 10 \
  --serial-enabled \
  --serial-start 3000000000 \
  --fixed-prefix-len 3
```
Behavior:
- Extracts first 3 digits of 3000000000 → 300
- Keeps 300 as fixed prefix
- Fills remaining 7 digits randomly
- Example local parts: 3004736218, 3009123456, etc.

**2.3. Example: classic serial prefix**
  ```text
python phone_generator_cli.py \
  --country US \
  --count 50 \
  --local-length 10 \
  --serial-enabled \
  --serial-placement prefix \
  --serial-start 1000 \
  --serial-step 1
```
Behavior:
- Serial runs: 1000, 1001, 1002, ...
- Each local part is: <serial><random_digits> (or similar, depending on length and mode).

**2.4. Example: sequential-only numbers**
  ```text
python phone_generator_cli.py \
  --country US \
  --count 20 \
  --local-length 10 \
  --serial-enabled \
  --serial-start 5550000000 \
  --serial-step 1 \
  --sequential-only
```
Behavior:
- Entire local part is the serial value (optionally zero-padded).
- No random digits are added.

**2.5. Strict length checking**
If you want to fail fast when the local-part length is unusual for that country:
  ```text
python phone_generator_cli.py \
  --country PK \
  --count 100 \
  --local-length 8 \
  --strict-length
```
If 8 is not a typical length for that region, the tool will exit with an error.

## CSV Output Format
Each generated CSV row has the following columns:
- e164_number – Full E.164 formatted number, e.g. +923004736218
- national_number – National number without country code, e.g. 3004736218
- country_iso – Region code, e.g. PK
- country_calling_code – Numeric calling code, e.g. 92
- generation_timestamp – ISO timestamp when generation started

Example:
  ```text
e164_number,national_number,country_iso,country_calling_code,generation_timestamp
+923004736218,3004736218,PK,92,2026-01-01T12:00:00
+923009123456,3009123456,PK,92,2026-01-01T12:00:00
...
```

## Implementation Overview
**Core module: phone_core.py**
Responsibilities:
- Resolve country from:
  - ISO alpha-2 code
  - Full country name
  - Calling code
- Configure serial behavior via SerialConfig
- Generate and validate phone numbers using phonenumbers
- Warn on unusual local-part lengths
- Export results to CSV

Key types and functions:
- SerialConfig
  - enabled
  - placement (prefix / suffix)
  - start
  - step
  - sequential_only
  - fixed_prefix_len
- resolve_country(identifier, interactive=False)
- warn_if_unrealistic_length(region, local_length, strict=False)
- generate_numbers(region, calling_code, count, local_length, serial_cfg, verbose=True)
- build_csv_filename(region, calling_code, country_display_name, prefix="numbers")
- save_to_csv(filename, rows)
**Interactive script: phone_generator.py**
- Guides the user through:
  - Country selection
  - Number count
  - Local-part length
  - Serial / fixed-prefix configuration
- Confirms overwriting existing CSV files
- Displays summary after completion
**CLI script: phone_generator_cli.py**
- Provides a scriptable interface with argparse
- Suitable for batch jobs, automation, and integration into other tooling

# E164 Export Tool

CLI tool to export a column named `e164_number` from a CSV file, ensure each number has a `+` prefix, and save the cleaned numbers to a text file.

Works on:

- Windows 10 / 11
- macOS
- Linux

The launch scripts will:

1. Check if a suitable Python 3 is installed (≥ 3.8 on macOS/Linux; any Python 3 on Windows).
2. If missing, attempt to install Python globally (system-wide).
3. Run the `export_e164.py` script.

---

## Folder Structure

Place the files like this:
  ```text
project_folder/ export_e164.py run_windows.bat run_macos.sh run_linux.sh
```

You can zip and distribute the `oasis_tool` folder.

---

## Requirements

- Internet connection (for first run on systems without Python or Homebrew/package manager metadata).
- Admin/sudo rights for:
  - Installing Python on Windows.
  - Installing Homebrew + Python on macOS.
  - Installing Python packages via system package manager on Linux.

---

## Usage Overview

Basic usage (all platforms):

```bash
# Windows
run_windows.bat path\to\file.csv

# macOS
./run_macos.sh /path/to/file.csv

# Linux
./run_linux.sh /path/to/file.csv
```
If you don’t provide file.csv as an argument, the script will prompt you for the CSV path.

By default, output is written as numbers.txt in the same folder as the input CSV, one number per line, each starting with +.

You can also specify an explicit output file via the -o/--output option, passed through to export_e164.py:

```text
# Windows
run_windows.bat path\to\file.csv -o path\to\output.txt

# macOS
./run_macos.sh /path/to/file.csv -o /path/to/output.txt

# Linux
./run_linux.sh /path/to/file.csv -o /path/to/output.txt
```

## Details Per Platform for export_e164.py
**Windows 10/11**
Entry point: run_windows.bat

Behavior:
1. Checks for python and then py -3.
2. If neither is available, downloads the official Python installer (currently 3.12.1, 64-bit) from python.org.
3. Installs Python silently for all users and adds it to PATH.
4. Re-checks for Python and finally runs:
```text
python export_e164.py ...
```
or
```text
py -3 export_e164.py ...
```
Run from project_folder directory:
```text
run_windows.bat path\to\file.csv
```
or Just:
```text
run_windows.bat
```
## macOS
Entry point: run_macos.sh

Behavior:
1. Checks for python3 with version ≥ 3.8.
2. If missing:
  - Installs Homebrew (if not already installed).
  - Uses Homebrew to install Python.
3. Runs:
```text
python3 export_e164.py ...
```
Setup:
```text
cd project_folder
chmod +x run_macos.sh
```
Run:
```text
./run_macos.sh /path/to/file.csv
```
and then enter the CSV path when prompted.

## Linux
Entry point: run_linux.sh
Behavior:
1. Checks for python3 with version ≥ 3.8.
2. If missing, attempts to install Python 3 via the detected package manager (requires sudo):
  - apt (Debian/Ubuntu)
  - dnf / yum (Fedora/RHEL/CentOS)
  - zypper (openSUSE)
  - pacman (Arch)
3. Run:
```text
python3 export_e164.py ...
```
Setup:
```text
cd project_folder
chmod +x run_linux.sh
```
Run:
```text
./run_linux.sh /path/to/file.csv
```
Or:
```text
./run_linux.sh
```
and then enter the CSV path when prompted.
**export_e164.py Behavior**

Core logic:

- Reads the CSV file using csv.DictReader.
- Looks for a column named e164_number.
  - If the column is missing, it raises an error.
- For each row:
  - Reads and strips the value in e164_number.
  - Skips empty values.
  - Ensures the number starts with +:
    - If it already has +, it's kept.
    - If not, + is prepended.
- Writes all processed numbers to a text file, one per line.

CLI options:
```text
python export_e164.py \[csv_path\] \[-o OUTPUT\]
```

- csv_path (optional positional):
  - Path to the input CSV.
  - If omitted, the script prompts: Enter path to CSV file:
- -o, \--output (optional):
  - Path to the output text file.
  - Default: numbers.txt in the same directory as the input CSV.

Examples (directly with Python, if you already have it):
```text
python3 export_e164.py contacts.csv

python3 export_e164.py contacts.csv -o cleaned_numbers.txt

python3 export_e164.py \# will prompt for CSV path
```

**CSV Requirements**

- File must contain a header row.
- Must include a column named exactly:
```text
e164_number
```

Example CSV:
```text
name,e164_number
Alice,1234567890
Bob,+19876543210
Charlie, 441234567890
```

Output (numbers.txt):

```text
+1234567890
+19876543210
+441234567890
```

**Notes / Limitations**

- Windows script uses a specific Python installer URL (currently 3.12.1,
  64-bit). Update this URL in run_windows.bat when you want to move to a
  newer Python release.
- macOS script assumes Homebrew is acceptable for installing Python.
- Linux script relies on common package managers and requires sudo for
  installing Python.
- All scripts are CLI-only; there is no GUI.

**Troubleshooting**

- CSV column not found\
  Error: Column \'e164_number\' not found in CSV header: \[\...\]\
  → Ensure your CSV has a header row with e164_number spelled exactly.
- Permission issues when installing Python
  - Windows: run the .bat from an elevated Command Prompt if needed.
  - macOS/Linux: ensure your user can run sudo and enter the password.
- Python still not found after install step
  - On Windows: verify that Python is on the PATH, or run py -3
    \--version.
  - On macOS/Linux: run python3 \--version to confirm installation, then
    re-run the launcher script.



## Error Handling & Notes
- If the requested number of valid numbers cannot be generated within a reasonable number of attempts, the generator stops early and reports how many it managed to generate.
- If serial or fixed-prefix configuration doesn’t fit into the chosen local-part length, the tool raises an error (or asks you to reconfigure in interactive mode).
- Country resolution may fail if the input is ambiguous or invalid; in that case the tool prints examples and exits (CLI) or asks again (interactive).
## Contributing
Contributions, suggestions, and bug reports are welcome.

1. Fork the repository.
2. Create a feature branch:
  ```text
git checkout -b feature/my-improvement
```
3. Commit your changes with clear messages.
4. Open a pull request describing:
   - What you changed
   - Why it’s useful
   - How to test it
  
## Credits
- Developer: **xorro**
- Repository: https://github.com/x-o-r-r-o/Bulk-Phone-Number-Generator
- Phone number validation powered by: [`phonenumbers`](https://github.com/daviddrysdale/python-phonenumbers)
- Country data powered by: [`pycountry`](https://pypi.org/project/pycountry/)
