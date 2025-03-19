# Tapestry - Log Analysis Tool

## Overview

Tapestry is a **command-line tool** designed to process and analyze different types of log files using a universal rule-based system. Users can specify queries using **grep, awk, regex, etc.** in a rules file to extract meaningful insights from logs. The tool organizes results into a dedicated output directory (`Tapestry_Results`).

## Features

- **Menu-based CLI**: Intuitive navigation through different analysis options.
- **Rule-based log processing**: Users define analysis rules in a text file (`rules.txt`).
- **Multiple log type support**:
  - XGFW Event Logs
  - IIS Logs
  - General Firewall Logs (Experimental)
  - General SSLVPN Logs (Experimental)
- **Multiple analysis modes**:
  - Generate Summary Reports
  - Run All Matching Rules
- **Automatic results organization**: Output files are stored in `Tapestry_Results`.
- **Field-aware rule execution**: Automatically maps log fields to rule placeholders.
- **Log extraction support**: Converts XGFW `.db` files into CSV format using `xgfw_unpacker.py`.

---

## Installation

### Prerequisites

- **Python 3.x**
- **Required utilities**: `grep`, `awk`, and other shell utilities (for Linux/macOS). Windows users may need Git Bash or WSL.

### Running the Tool

Clone or download the repository and navigate to its directory:

```sh
python tapestry.py
```

---

## Usage

### Main Menu

Upon running, Tapestry presents the following menu:

```
1. Log Analysis
2. Log Extraction
3. Manual
4. Exit
```

### Log Extraction

Select **2. Log Extraction** to extract logs. Currently, only **XGFW Event Logs** are supported. Provide the directory containing `.db` files, and the tool will convert them into CSV format using `xgfw_unpacker.py`. The output is saved in a `converted` directory.

### Log Analysis

Select **1. Log Analysis** to proceed with log processing.

#### Log Type Selection

Choose the type of log files to analyze:

```
1. XGFW Event Logs
2. IIS
3. General FW (Experimental)
4. General SSLVPN (Experimental)
```

#### Analysis Choice

Select how to analyze the logs:

```
1. Generate Summary Report
2. Run Rules File
3. Identifier Search (WIP)
```

#### Specifying Log Directory

After selecting the log type and analysis choice, the tool will prompt:

```
Enter the target directory containing log files:
```

Provide the full path to the directory containing logs. For XGFW Event Logs, ensure the directory contains `tapestry_logs.csv`.

#### Field Mapping for Rules

For XGFW Event Logs, the tool automatically maps log fields to rule placeholders (e.g., `${field_name}`) by analyzing the log file's header.

### Output Location

All results are saved inside:

```
Tapestry_Results/
```

This directory is created automatically inside the current working directory.

---

## Adding Rules

Tapestry applies log analysis rules based on `rules.txt`. Each rule follows this format:

```
XXXXXX|command
```

### Rule Breakdown

- `XXXXXX` → 6-digit rule identifier:
  - `XX----` → (Unused for now)
  - `--X---` → Log Type Selection (1-4)
  - `---X--` → Analysis Choice (1-3)
  - `----X-` → Date Variable (0-1) *(Not implemented yet)*
  - `-----X` → Identifier Variable (0-1) *(Not implemented yet)*
- `command` → The actual command to be executed. Use `${field_name}` placeholders for field-aware execution.

### Example Rules

#### **Basic grep rule for error messages in XGFW logs:**

```
103100|grep "ERROR" {log_file} > error_results.txt
```

#### **Extracting specific fields using awk in IIS logs:**

```
112200|awk '{print $1, $7}' {log_file} > requested_urls.txt
```

#### **General Firewall Rule to filter critical warnings:**

```
203001|grep -E "(WARN|CRITICAL)" {log_file} > warnings.txt
```

### Comments in Rules

Lines starting with `//` are ignored:

```
// This is a comment, ignored by the tool
103100|grep "ERROR" {log_file} > error_results.txt
```

---

## Debugging & Development

### Debug Mode

During execution, the tool displays the **rule generation values** and **field placements** for debugging:

```
DEBUG: Rule Code Generation Values
Log Type: 3, Analysis Choice: 1

Field Placements:
{'field1': 1, 'field2': 2, ...}
```

### Locating Results

After processing logs, results can be found in:

```
Tapestry_Results/
```

---

## Future Enhancements

- Implement **identifier-based filtering**.
- Add **date-based log filtering**.
- Support **custom output directories**.
- Improve **Windows compatibility**.

