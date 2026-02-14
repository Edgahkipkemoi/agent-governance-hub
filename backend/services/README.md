# Backend Services

## DatabaseService

The `DatabaseService` class provides database operations for storing and retrieving audit logs using Supabase.

### Features

1. **Initialization**
   - Validates required environment variables (`SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`)
   - Creates Supabase client connection
   - Fails fast with clear error messages if configuration is missing

2. **Create Audit Log** (`create_audit_log`)
   - Stores query, response, audit results, and risk status
   - Validates all inputs before insertion:
     - Query and response must be non-empty
     - Status must be "Safe", "Warning", or "Flagged"
     - Audit must contain required fields: risk_score, hallucination_detected, pii_detected, toxic_content_detected
   - Returns UUID of created log entry
   - Handles database errors with detailed error messages

3. **Get Recent Logs** (`get_recent_logs`)
   - Retrieves logs ordered by created_at (descending)
   - Supports custom limit (default: 50)
   - Validates limit parameter
   - Returns empty list if no logs exist
   - Handles database errors with detailed error messages

### Usage Example

```python
from services.database_service import DatabaseService

# Initialize service
service = DatabaseService()

# Create audit log
audit_data = {
    "risk_score": 2,
    "hallucination_detected": False,
    "pii_detected": False,
    "toxic_content_detected": False,
    "details": "Response appears factual and safe",
    "confidence": 0.95
}

log_id = await service.create_audit_log(
    query="What is the capital of France?",
    response="The capital of France is Paris.",
    audit=audit_data,
    status="Safe"
)

# Retrieve recent logs
logs = await service.get_recent_logs(limit=10)
```

### Error Handling

The service implements comprehensive error handling:

- **Configuration Errors**: Raises `ValueError` if environment variables are missing
- **Validation Errors**: Raises `ValueError` for invalid inputs (empty strings, invalid status, missing audit fields)
- **Database Errors**: Raises `Exception` with detailed error messages for connection or query failures
- **Logging**: All operations and errors are logged using Python's logging module

### Requirements Satisfied

- **Requirement 3.1**: Stores query, response, audit results, and status
- **Requirement 3.2**: Generates unique UUID for each log entry (handled by database)
- **Requirement 3.3**: Records timestamp automatically (handled by database)
- **Requirement 3.4**: Returns error response when database storage fails
- **Requirement 3.5**: Stores audit results as structured JSON data
- **Requirement 10.2**: Reads database connection strings from environment variables

### Testing

Unit tests are available in `tests/test_database_service.py` covering:
- Initialization with valid/invalid environment variables
- Successful log creation and retrieval
- Input validation for all methods
- Error handling for database failures

Manual integration test available in `test_database_manual.py` for testing with actual Supabase database.
