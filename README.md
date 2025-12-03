# RentCast AVM Processor - Technical Documentation

## Table of Contents
1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Security Implementation](#security-implementation)
4. [GCP Bucket Structure](#gcp-bucket-structure)
5. [Processing Workflow](#processing-workflow)
6. [Configuration](#configuration)
7. [Data Retention Policies](#data-retention-policies)
8. [Logging and Monitoring](#logging-and-monitoring)
9. [Error Handling](#error-handling)
10. [Deployment Guide](#deployment-guide)
11. [API Integration](#api-integration)
12. [Troubleshooting](#troubleshooting)

---

## Overview

### Purpose
The RentCast AVM Processor is an automated Python application designed to process property addresses in bulk and retrieve Automated Valuation Model (AVM) data from the RentCast API. The system processes addresses in batches, stores results in JSON format, and maintains comprehensive audit logs.

### Key Features
- **Batch Processing**: Processes addresses in batches of 100
- **Secure API Key Management**: Retrieves API credentials from GCP Secret Manager
- **Automated Cleanup**: Removes old logs (7 days) and processed files (100 days)
- **Comprehensive Logging**: Detailed activity logs stored in GCP
- **Error Resilience**: Continues processing even if individual addresses fail
- **Cloud-Native**: Fully integrated with Google Cloud Platform services

### Technology Stack
- **Language**: Python 3.8+
- **Cloud Platform**: Google Cloud Platform (GCP)
- **Storage**: Google Cloud Storage
- **Security**: GCP Secret Manager
- **API**: RentCast AVM API v1

---

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    GCP Secret Manager                        │
│                  (RentCast API Key)                         │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ Secure Retrieval
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              RentCast AVM Processor                         │
│  ┌────────────────────────────────────────────────────┐    │
│  │  1. Cleanup old logs (>7 days)                     │    │
│  │  2. Cleanup processed files (>100 days)            │    │
│  │  3. Read addresses from input file                 │    │
│  │  4. Process in batches of 100                      │    │
│  │  5. Call RentCast API for each address             │    │
│  │  6. Save batch results to JSON                     │    │
│  │  7. Move input to processed folder                 │    │
│  │  8. Upload logs to GCP                             │    │
│  └────────────────────────────────────────────────────┘    │
└───────┬──────────────────────────────────────┬──────────────┘
        │                                      │
        │                                      │
        ▼                                      ▼
┌──────────────────┐                  ┌──────────────────┐
│  GCP Storage     │                  │  RentCast API    │
│  Bucket:         │                  │  External Service│
│  rent-cast-avm   │                  └──────────────────┘
└──────────────────┘
```

### Component Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                 RentCastAVMProcessor Class                   │
├─────────────────────────────────────────────────────────────┤
│  Components:                                                 │
│  ├─ Secret Manager Client (API Key Retrieval)              │
│  ├─ Storage Client (GCP Bucket Operations)                 │
│  ├─ Logger (In-Memory StringIO Buffer)                     │
│  ├─ HTTP Client (RentCast API Communication)               │
│  └─ Batch Processor (Address Processing Logic)             │
├─────────────────────────────────────────────────────────────┤
│  Methods:                                                    │
│  ├─ get_api_key_from_secret_manager()                      │
│  ├─ setup_logging()                                         │
│  ├─ upload_log_to_gcp()                                     │
│  ├─ cleanup_old_logs()                                      │
│  ├─ cleanup_old_processed_files()                          │
│  ├─ read_addresses_from_gcp()                              │
│  ├─ call_rentcast_api()                                     │
│  ├─ process_batch()                                         │
│  ├─ save_batch_to_gcp()                                     │
│  ├─ move_input_file_to_processed()                         │
│  └─ process_all_addresses()                                │
└─────────────────────────────────────────────────────────────┘
```

---

## Security Implementation

### GCP Secret Manager Integration

The application implements enterprise-grade security by storing the RentCast API key in GCP Secret Manager instead of hardcoding credentials.

#### Benefits
- **Zero Credential Exposure**: No API keys in code or configuration files
- **Centralized Management**: Single source of truth for secrets
- **Audit Trail**: All secret access is logged by GCP
- **Rotation Ready**: Easy API key rotation without code changes
- **Access Control**: IAM-based permission management

#### Implementation Details

**Secret Name**: `rentcast-api-key`  
**Secret Version**: `latest` (automatically uses the most recent version)  
**Project ID**: Retrieved from environment or explicitly configured

#### Code Implementation

```python
from google.cloud import secretmanager

def get_api_key_from_secret_manager(self, project_id, secret_id="rentcast-api-key"):
    """
    Retrieve RentCast API key from GCP Secret Manager
    
    Args:
        project_id: GCP Project ID
        secret_id: Secret identifier (default: rentcast-api-key)
    
    Returns:
        str: API key value
    """
    try:
        client = secretmanager.SecretManagerServiceClient()
        name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
        response = client.access_secret_version(request={"name": name})
        return response.payload.data.decode("UTF-8")
    except Exception as e:
        self.logger.error(f"Failed to retrieve API key: {e}")
        raise
```

#### Required IAM Permissions

The service account running this application requires:
- `secretmanager.versions.access` - To read secret values
- `secretmanager.secrets.get` - To retrieve secret metadata

**Recommended IAM Role**: `roles/secretmanager.secretAccessor`

#### Setup Instructions

1. **Create the secret in GCP Console**:
   ```bash
   gcloud secrets create rentcast-api-key \
       --replication-policy="automatic"
   ```

2. **Add the API key value**:
   ```bash
   echo -n "your-rentcast-api-key-here" | \
       gcloud secrets versions add rentcast-api-key --data-file=-
   ```

3. **Grant access to service account**:
   ```bash
   gcloud secrets add-iam-policy-binding rentcast-api-key \
       --member="serviceAccount:your-service-account@project.iam.gserviceaccount.com" \
       --role="roles/secretmanager.secretAccessor"
   ```

#### Security Best Practices

1. **Least Privilege**: Grant secret access only to required service accounts
2. **Secret Rotation**: Rotate API keys periodically (recommended: 90 days)
3. **Audit Logging**: Enable Cloud Audit Logs for secret access monitoring
4. **Environment Isolation**: Use separate secrets for dev/staging/production
5. **Version Management**: Keep multiple versions for zero-downtime rotation

---

## GCP Bucket Structure

### Bucket Name
`rent-cast-avm`

### Folder Hierarchy

```
rent-cast-avm/
│
├── AVM/
│   ├── avmfile.txt                          # Input file with addresses
│   │
│   └── processed/
│       ├── avmfile_20241203_143022.txt      # Processed files with timestamp
│       ├── avmfile_20241202_091544.txt
│       └── avmfile_20241201_105633.txt
│
├── JSON/
│   ├── rentcast_avm_241203_batch001.json    # Output JSON files
│   ├── rentcast_avm_241203_batch002.json
│   ├── rentcast_avm_241203_batch003.json
│   └── ...
│
└── Logs/
    ├── rentcast_avm_20241203_143022.log     # Processing logs
    ├── rentcast_avm_20241202_091544.log
    └── ...
```

### Folder Descriptions

#### `/AVM/` (Base Input Folder)
- **Purpose**: Contains the input file with addresses to process
- **File Format**: Plain text, newline-separated addresses
- **File Name**: `avmfile.txt`
- **Access Pattern**: Read-once per processing run

#### `/AVM/processed/` (Processed Files Archive)
- **Purpose**: Archive of successfully processed input files
- **Naming Convention**: `avmfile_YYYYMMDD_HHMMSS.txt`
- **Retention**: Automatically deleted after 100 days
- **Access Pattern**: Write-once, read rarely (audit purposes)

#### `/JSON/` (Output Results)
- **Purpose**: Stores AVM valuation results in JSON format
- **Naming Convention**: `rentcast_avm_YYMMDD_batchNNN.json`
- **File Contents**: Array of API responses (up to 100 records per file)
- **Retention**: No automatic cleanup (business data)
- **Access Pattern**: Write-once, read frequently

#### `/Logs/` (Application Logs)
- **Purpose**: Detailed processing logs for monitoring and debugging
- **Naming Convention**: `rentcast_avm_YYYYMMDD_HHMMSS.log`
- **Retention**: Automatically deleted after 7 days
- **Access Pattern**: Write-once, read for troubleshooting

### Storage Classes

| Folder | Storage Class | Reason |
|--------|---------------|--------|
| `/AVM/` | Standard | Frequent access required |
| `/AVM/processed/` | Nearline | Infrequent access, long retention |
| `/JSON/` | Standard | Frequent access for reporting |
| `/Logs/` | Standard | Short retention, debugging needs |

---

## Processing Workflow

### Complete Process Flow

```
START
  │
  ├─► 1. Initialize Application
  │      ├─ Retrieve API key from Secret Manager
  │      ├─ Setup logging with StringIO buffer
  │      └─ Initialize GCP Storage client
  │
  ├─► 2. Cleanup Phase
  │      ├─ Delete logs older than 7 days
  │      └─ Delete processed files older than 100 days
  │
  ├─► 3. Read Input
  │      ├─ Download AVM/avmfile.txt from GCP
  │      ├─ Parse newline-separated addresses
  │      └─ Validate address count > 0
  │
  ├─► 4. Batch Processing Loop
  │      │
  │      └─► For each batch (100 addresses):
  │            │
  │            ├─► For each address in batch:
  │            │     ├─ URL encode address
  │            │     ├─ Call RentCast API
  │            │     ├─ Handle success/error
  │            │     └─ Log result
  │            │
  │            ├─ Aggregate batch results
  │            ├─ Generate JSON filename
  │            └─ Upload to JSON/ folder
  │
  ├─► 5. Archive Input File
  │      ├─ Generate timestamped filename
  │      ├─ Copy to AVM/processed/
  │      └─ Delete original AVM/avmfile.txt
  │
  ├─► 6. Finalize Logging
  │      ├─ Generate processing summary
  │      ├─ Upload log buffer to Logs/ folder
  │      └─ Close log buffer
  │
END
```

### Detailed Step-by-Step Process

#### Step 1: Initialization
```python
# Retrieve API key securely from Secret Manager
api_key = processor.get_api_key_from_secret_manager(project_id="your-gcp-project")

# Setup in-memory logging
processor.setup_logging()

# Initialize GCP Storage client
storage_client = storage.Client()
```

#### Step 2: Automated Cleanup
- **Log Cleanup**: Removes all files in `Logs/` older than 7 days
- **Processed File Cleanup**: Removes all files in `AVM/processed/` older than 100 days
- **Purpose**: Maintain storage costs and comply with data retention policies

#### Step 3: Read Input Addresses
```python
# Read from GCP bucket
addresses = processor.read_addresses_from_gcp()

# Expected format in avmfile.txt:
# 123 Main St, New York, NY 10001
# 456 Oak Ave, Los Angeles, CA 90001
# 789 Pine Rd, Chicago, IL 60601
```

#### Step 4: Batch Processing
**Batch Size**: 100 addresses per batch  
**Processing Method**: Sequential (one address at a time within batch)

**For each address**:
1. URL encode the address
2. Construct API URL with encoded address and comp count
3. Make HTTP GET request with API key in header
4. Handle response:
   - **Success (200)**: Store full API response
   - **Error (4xx/5xx)**: Store error details
   - **Exception**: Store exception message
5. Log individual result

**For each batch**:
1. Collect all individual results
2. Generate JSON filename: `rentcast_avm_YYMMDD_batchNNN.json`
3. Convert results to JSON format
4. Upload to `JSON/` folder in GCP

#### Step 5: Archive Input File
- Copy `AVM/avmfile.txt` to `AVM/processed/avmfile_YYYYMMDD_HHMMSS.txt`
- Delete original `AVM/avmfile.txt`
- Purpose: Prevent reprocessing and maintain audit trail

#### Step 6: Finalize Logging
- Generate processing summary with statistics
- Upload complete log from StringIO buffer to `Logs/` folder
- Close buffer and cleanup resources

---

## Configuration

### Application Configuration

```python
# GCP Configuration
GCP_PROJECT_ID = "your-gcp-project-id"
GCP_BUCKET_NAME = "rent-cast-avm"

# Secret Manager Configuration
SECRET_NAME = "rentcast-api-key"

# Folder Structure
BASE_FOLDER = "AVM"
INPUT_FILE = f"{BASE_FOLDER}/avmfile.txt"
PROCESSED_FOLDER = f"{BASE_FOLDER}/processed"
OUTPUT_FOLDER = "JSON"
LOG_FOLDER = "Logs"

# Processing Configuration
BATCH_SIZE = 100
COMP_COUNT = 5  # Number of comparable properties

# Retention Policies
LOG_RETENTION_DAYS = 7
PROCESSED_FILE_RETENTION_DAYS = 100

# API Configuration
RENTCAST_API_URL = "https://api.rentcast.io/v1/avm/value"
API_TIMEOUT_SECONDS = 30
```

### Environment Variables

```bash
# Required
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
GCP_PROJECT_ID=your-gcp-project-id

# Optional
LOG_LEVEL=INFO
BATCH_SIZE=100
```

### Service Account Permissions

The GCP service account requires the following permissions:

```yaml
# Storage Permissions
- storage.objects.create      # Upload files
- storage.objects.delete      # Delete old files
- storage.objects.get         # Read input files
- storage.objects.list        # List files for cleanup

# Secret Manager Permissions
- secretmanager.versions.access   # Read API key
- secretmanager.secrets.get       # Get secret metadata

# Recommended Roles
roles:
  - roles/storage.objectAdmin              # For bucket operations
  - roles/secretmanager.secretAccessor     # For API key retrieval
```

---

## Data Retention Policies

### Log Files - 7 Days Retention

**Policy**: Automatically delete log files older than 7 days

**Rationale**:
- Logs are primarily used for immediate troubleshooting
- Reduces storage costs for verbose logs
- Compliance with short-term operational data policies

**Implementation**:
- Runs at the start of each processing job
- Checks `time_created` metadata of each blob
- Deletes files where `creation_date < (current_date - 7 days)`

**Code Reference**:
```python
def cleanup_old_logs(self, days=7):
    cutoff_date = datetime.now() - timedelta(days=days)
    blobs = bucket.list_blobs(prefix=f"{self.log_folder}/")
    
    for blob in blobs:
        if blob.time_created.replace(tzinfo=None) < cutoff_date:
            blob.delete()
```

### Processed Files - 100 Days Retention

**Policy**: Automatically delete processed input files older than 100 days

**Rationale**:
- Maintains audit trail for regulatory compliance (typical 90-day requirement)
- Allows reprocessing if needed within reasonable timeframe
- Prevents indefinite accumulation of historical input files

**Implementation**:
- Runs at the start of each processing job
- Checks `time_created` metadata of each blob
- Deletes files where `creation_date < (current_date - 100 days)`

**Code Reference**:
```python
def cleanup_old_processed_files(self, days=100):
    cutoff_date = datetime.now() - timedelta(days=days)
    blobs = bucket.list_blobs(prefix="AVM/processed/")
    
    for blob in blobs:
        if blob.time_created.replace(tzinfo=None) < cutoff_date:
            blob.delete()
```

### JSON Output Files - No Automatic Deletion

**Policy**: JSON result files are **NOT** automatically deleted

**Rationale**:
- Contains business-critical valuation data
- Used for reporting, analytics, and business decisions
- Subject to separate business data retention policies
- May be required for legal/regulatory purposes

**Manual Cleanup**: Should be managed by business requirements and data governance policies

---

## Logging and Monitoring

### Log Levels

| Level | Usage | Example |
|-------|-------|---------|
| **INFO** | Normal operations | "Processing address 5/100" |
| **WARNING** | Recoverable errors | "API returned 429 rate limit" |
| **ERROR** | Failed operations | "Failed to upload batch results" |
| **DEBUG** | Detailed debugging | "API response body: {...}" |

### Log Format

```
YYYY-MM-DD HH:MM:SS - RentCastAVMProcessor - LEVEL - Message
```

**Example**:
```
2024-12-03 14:30:22 - RentCastAVMProcessor - INFO - Starting RentCast AVM processing...
2024-12-03 14:30:23 - RentCastAVMProcessor - INFO - Total addresses: 250
2024-12-03 14:30:24 - RentCastAVMProcessor - INFO - Processing address 1/100: 123 Main St
2024-12-03 14:30:25 - RentCastAVMProcessor - SUCCESS: 123 Main St
```

### In-Memory Logging Architecture

```
┌─────────────────────┐
│   Logger Instance   │
├─────────────────────┤
│  ┌───────────────┐ │
│  │ Console       │ │  ─────► Terminal/stdout
│  │ Handler       │ │
│  └───────────────┘ │
│                     │
│  ┌───────────────┐ │
│  │ StringIO      │ │  ─────► In-Memory Buffer
│  │ Handler       │ │         (uploaded at end)
│  └───────────────┘ │
└─────────────────────┘
```

### Log Contents

Each log file includes:
- **Initialization**: Application start, configuration loaded
- **Cleanup Summary**: Number of files deleted
- **Input Processing**: Address count, batch division
- **Batch Progress**: Current batch number, address range
- **API Responses**: Success/failure for each address
- **Error Details**: Stack traces for exceptions
- **Final Summary**: Total processed, success rate, completion time

### Monitoring Recommendations

#### Key Metrics to Monitor
1. **Success Rate**: Percentage of successful API calls
2. **Processing Time**: Time to complete full batch
3. **API Response Times**: Average time per API call
4. **Error Rate**: Failed addresses per batch
5. **File Cleanup**: Number of files deleted

#### Alerting Thresholds
```yaml
critical:
  - success_rate < 80%
  - processing_time > 60 minutes
  - error_rate > 20%

warning:
  - success_rate < 95%
  - processing_time > 30 minutes
  - api_response_time > 5 seconds
```

#### GCP Monitoring Integration
- Use Cloud Logging to aggregate logs
- Create log-based metrics for key indicators
- Set up alert policies in Cloud Monitoring
- Configure notification channels (email, Slack, PagerDuty)

---

## Error Handling

### Error Handling Strategy

The application implements graceful degradation:
- **Continue on Error**: Individual address failures don't stop batch processing
- **Comprehensive Logging**: All errors captured with context
- **Error Categorization**: Distinguish between API errors, network issues, and data problems

### Error Types and Responses

#### 1. API Errors (4xx, 5xx)

**Scenario**: RentCast API returns error status code

**Handling**:
```python
{
    "address": "123 Main St",
    "status": "error",
    "error_code": 404,
    "error_message": "Address not found in database"
}
```

**Common Error Codes**:
- `400`: Invalid address format
- `401`: Invalid API key
- `404`: Address not found
- `429`: Rate limit exceeded
- `500`: Internal server error

#### 2. Network Exceptions

**Scenario**: Connection timeout, DNS failure, network interruption

**Handling**:
```python
{
    "address": "456 Oak Ave",
    "status": "error",
    "error_message": "Connection timeout after 30 seconds"
}
```

#### 3. Data Validation Errors

**Scenario**: Empty input file, malformed addresses

**Handling**:
- Log warning
- Skip empty lines
- Continue with valid addresses

#### 4. GCP Storage Errors

**Scenario**: Bucket access denied, file not found

**Handling**:
- Log critical error
- Exit application (cannot continue without storage)
- Alert operators

### Retry Logic

**Current Implementation**: No automatic retries

**Rationale**:
- Batch processing nature allows manual re-run
- Avoids duplicate API charges
- Failed addresses logged for manual investigation

**Future Enhancement**: Implement exponential backoff for rate limit errors (429)

### Error Recovery

#### For Individual Address Failures:
1. Log error details
2. Include in batch results JSON
3. Continue to next address
4. Report in final summary

#### For Batch Failures:
1. Log complete stack trace
2. Upload partial results if any succeeded
3. Do not move input file to processed
4. Allow manual retry

#### For Critical Failures:
1. Log error to console and buffer
2. Attempt to upload log to GCP
3. Exit with non-zero status code
4. Send alert notification (if configured)

---

## Deployment Guide

### Prerequisites

1. **GCP Project**:
   - Active GCP project with billing enabled
   - Cloud Storage API enabled
   - Secret Manager API enabled

2. **GCP Bucket**:
   ```bash
   gsutil mb -c STANDARD -l us-central1 gs://rent-cast-avm
   ```

3. **Folder Structure**:
   ```bash
   gsutil mkdir gs://rent-cast-avm/AVM
   gsutil mkdir gs://rent-cast-avm/AVM/processed
   gsutil mkdir gs://rent-cast-avm/JSON
   gsutil mkdir gs://rent-cast-avm/Logs
   ```

4. **Service Account**:
   ```bash
   gcloud iam service-accounts create rentcast-processor \
       --display-name="RentCast AVM Processor"
   
   gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
       --member="serviceAccount:rentcast-processor@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
       --role="roles/storage.objectAdmin"
   
   gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
       --member="serviceAccount:rentcast-processor@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
       --role="roles/secretmanager.secretAccessor"
   ```

5. **API Key Setup**:
   ```bash
   # Create secret
   gcloud secrets create rentcast-api-key --replication-policy="automatic"
   
   # Add API key value
   echo -n "YOUR_RENTCAST_API_KEY" | \
       gcloud secrets versions add rentcast-api-key --data-file=-
   ```

### Python Environment Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install google-cloud-storage google-cloud-secret-manager requests
```

### Application Deployment

#### Option 1: Local/VM Deployment

```bash
# Clone or copy the application code
cd /path/to/application

# Set environment variables
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
export GCP_PROJECT_ID=your-gcp-project-id

# Run the application
python rentcast_avm_processor.py
```

#### Option 2: Cloud Run Deployment

**Dockerfile**:
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY rentcast_avm_processor.py .

CMD ["python", "rentcast_avm_processor.py"]
```

**Deploy**:
```bash
gcloud run deploy rentcast-avm-processor \
    --source . \
    --region us-central1 \
    --service-account rentcast-processor@YOUR_PROJECT_ID.iam.gserviceaccount.com \
    --set-env-vars GCP_PROJECT_ID=YOUR_PROJECT_ID
```

#### Option 3: Cloud Functions Deployment

```bash
gcloud functions deploy process_rentcast_avm \
    --runtime python39 \
    --trigger-http \
    --entry-point process_all_addresses \
    --service-account rentcast-processor@YOUR_PROJECT_ID.iam.gserviceaccount.com \
    --set-env-vars GCP_PROJECT_ID=YOUR_PROJECT_ID
```

### Scheduling (Cloud Scheduler)

```bash
# Create a daily schedule at 2 AM
gcloud scheduler jobs create http rentcast-daily-processing \
    --schedule="0 2 * * *" \
    --uri="https://YOUR_CLOUD_RUN_URL" \
    --http-method=POST \
    --time-zone="America/New_York"
```

---

## API Integration

### RentCast AVM API v1

**Base URL**: `https://api.rentcast.io/v1/avm/value`

**Authentication**: API Key in header

**Request Format**:
```
GET /v1/avm/value?address={encoded_address}&compCount={comp_count}

Headers:
  X-Api-Key: your-api-key-here
  Accept: application/json
```

**Parameters**:
- `address` (required): URL-encoded property address
- `compCount` (optional): Number of comparable properties (default: 5)

**Example Request**:
```python
url = "https://api.rentcast.io/v1/avm/value"
params = {
    "address": "123 Main St, New York, NY 10001",
    "compCount": 5
}
headers = {
    "X-Api-Key": "your-api-key",
    "Accept": "application/json"
}
response = requests.get(url, params=params, headers=headers)
```

**Success Response (200)**:
```json
{
  "address": "123 Main St, New York, NY 10001",
  "propertyType": "Single Family",
  "bedrooms": 3,
  "bathrooms": 2,
  "squareFootage": 1500,
  "price": 450000,
  "priceRangeLow": 420000,
  "priceRangeHigh": 480000,
  "comparables": [
    {
      "address": "125 Main St",
      "distance": 0.1,
      "price": 455000
    }
  ]
}
```

**Error Responses**:
- `400`: Bad Request - Invalid parameters
- `401`: Unauthorized - Invalid API key
- `404`: Not Found - Address not in database
- `429`: Rate Limit Exceeded
- `500`: Internal Server Error

### Rate Limits

**RentCast API Limits** (verify with your subscription):
- Requests per minute: Varies by plan
- Daily request limit: Varies by plan

**Application Rate Control**:
- Sequential processing (no parallel requests)
- 30-second timeout per request
- No automatic retries (avoids duplicate charges)

### Data Quality Considerations

1. **Address Format**: Ensure consistent formatting in input file
2. **Geocoding**: RentCast handles address normalization
3. **Data Availability**: Not all addresses may have AVM data
4. **Comparables**: Request appropriate `compCount` for accuracy

---

## Troubleshooting

### Common Issues and Solutions

#### Issue 1: "Failed to retrieve API key from Secret Manager"

**Symptoms**:
```
ERROR - Failed to retrieve API key: 403 Permission Denied
```

**Solutions**:
1. Verify service account has `secretmanager.secretAccessor` role
2. Check secret name matches: `rentcast-api-key`
3. Ensure secret exists in correct GCP project
4. Verify `GCP_PROJECT_ID` environment variable is set

**Verification**:
```bash
gcloud secrets describe rentcast-api-key
gcloud secrets get-iam-policy rentcast-api-key
```

---

#### Issue 2: "No addresses found to process"

**Symptoms**:
```
WARNING - No addresses found to process
```

**Solutions**:
1. Check if `AVM/avmfile.txt` exists in bucket
2. Verify file is not empty
3. Ensure file has proper line breaks (`\n`)
4. Check service account has read permissions

**Verification**:
```bash
gsutil ls gs://rent-cast-avm/AVM/
gsutil cat gs://rent-cast-avm/AVM/avmfile.txt
```