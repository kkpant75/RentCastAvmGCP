# RentCast API to CSV Converter - Documentation

## Table of Contents
1. [Overview](#overview)
2. [System Requirements](#system-requirements)
3. [Installation Guide](#installation-guide)
4. [Configuration](#configuration)
5. [Operation Manual](#operation-manual)
6. [Solution Architecture](#solution-architecture)
7. [CSV Output Structure](#csv-output-structure)
8. [Troubleshooting](#troubleshooting)
9. [API Reference](#api-reference)
10. [Best Practices](#best-practices)

---

## Overview

### Purpose
This Python application connects to the RentCast API to fetch property valuation data and exports it to CSV format for analysis. The tool is designed for real estate professionals, investors, and analysts who need to evaluate property values with comparable market data.

### Key Features
- Automated API data retrieval from RentCast
- Flat CSV structure with subject property and comparable properties
- Environment-based API key management (.env file)
- Command-line interface for easy automation
- Comprehensive error handling and validation
- Timestamped output files

### Use Cases
- Property valuation analysis
- Comparative market analysis (CMA)
- Real estate investment research
- Portfolio evaluation
- Market trend analysis

---

## System Requirements

### Software Requirements
- **Python**: Version 3.7 or higher
- **Operating System**: Windows, macOS, or Linux
- **Internet Connection**: Required for API calls

### Python Dependencies
```
requests>=2.31.0
python-dotenv>=1.0.0
```

### Hardware Requirements
- Minimum 2GB RAM
- 100MB free disk space
- Network connectivity

---

## Installation Guide

### Step 1: Install Python
Ensure Python 3.7+ is installed on your system.

**Check Python version:**
```bash
python --version
# or
python3 --version
```

**Download Python:**
- Visit: https://www.python.org/downloads/
- Download and install the latest version

### Step 2: Download the Script
Save the `rentcast_to_csv.py` file to your desired directory.

### Step 3: Install Required Packages

**Option A: Using pip (Recommended)**
```bash
pip install requests python-dotenv
```

**Option B: Using pip3**
```bash
pip3 install requests python-dotenv
```

**Option C: Using requirements.txt**

Create a file named `requirements.txt`:
```
requests>=2.31.0
python-dotenv>=1.0.0
```

Install:
```bash
pip install -r requirements.txt
```

### Step 4: Verify Installation
```bash
python rentcast_to_csv.py --help
```

If successful, you'll see the help menu.

---

## Configuration

### Step 1: Obtain RentCast API Key

1. Visit: https://app.rentcast.io
2. Sign up for an account
3. Navigate to API settings
4. Copy your API key

### Step 2: Create .env File

Create a file named `.env` in the same directory as `rentcast_to_csv.py`:

```env
# RentCast API Configuration
RENTCAST_API_KEY=your_actual_api_key_here
```

**Important Security Notes:**
- Never commit `.env` file to version control
- Add `.env` to your `.gitignore` file
- Keep your API key confidential

### Step 3: Create .gitignore (Optional but Recommended)

If using Git, create a `.gitignore` file:
```
.env
*.csv
__pycache__/
*.pyc
```

---

## Operation Manual

### Basic Usage

#### Syntax
```bash
python rentcast_to_csv.py --address "PROPERTY_ADDRESS" [OPTIONS]
```

### Command-Line Arguments

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `--address` | Yes | None | Property address to evaluate |
| `--comp-count` | No | 5 | Number of comparable properties (1-25) |
| `--output` | No | Auto-generated | Custom output filename |
| `--api-key` | No | From .env | Override API key from .env |

### Usage Examples

#### Example 1: Basic Usage
```bash
python rentcast_to_csv.py --address "5500 Grand Lake Dr, San Antonio, TX, 78244"
```
**Output:** `rentcast_20241130_143045.csv` (auto-generated with timestamp)

#### Example 2: Custom Comparable Count
```bash
python rentcast_to_csv.py --address "123 Main St, Austin, TX, 78701" --comp-count 10
```
**Result:** Fetches 10 comparable properties

#### Example 3: Custom Output Filename
```bash
python rentcast_to_csv.py --address "456 Oak Ave, Dallas, TX, 75201" --output "dallas_property.csv"
```
**Output:** `dallas_property.csv`

#### Example 4: Override API Key
```bash
python rentcast_to_csv.py --api-key "sk_different_key" --address "789 Elm St, Houston, TX, 77001"
```
**Use Case:** Testing with different API accounts

#### Example 5: Maximum Comparables
```bash
python rentcast_to_csv.py --address "321 Pine St, Fort Worth, TX, 76102" --comp-count 25
```
**Result:** Fetches maximum 25 comparables

### Running the Script

#### On Windows
```cmd
python rentcast_to_csv.py --address "5500 Grand Lake Dr, San Antonio, TX, 78244"
```

#### On macOS/Linux
```bash
python3 rentcast_to_csv.py --address "5500 Grand Lake Dr, San Antonio, TX, 78244"
```

#### Make Script Executable (macOS/Linux)
```bash
chmod +x rentcast_to_csv.py
./