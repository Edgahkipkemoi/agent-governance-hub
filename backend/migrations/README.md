# Database Migrations

This directory contains SQL migration files for the Agent Audit System database.

## Running Migrations

### Option 1: Supabase Dashboard (Recommended)

1. Log in to your Supabase project dashboard
2. Navigate to the SQL Editor
3. Copy the contents of `001_create_logs_table.sql`
4. Paste into the SQL Editor and run the query

### Option 2: Supabase CLI

If you have the Supabase CLI installed:

```bash
supabase db push
```

### Option 3: Direct PostgreSQL Connection

If you have direct access to your PostgreSQL database:

```bash
psql -h <your-supabase-host> -U postgres -d postgres -f migrations/001_create_logs_table.sql
```

## Migration Files

- `001_create_logs_table.sql` - Creates the logs table with all required columns, constraints, and indexes

## Schema Overview

The `logs` table stores audit logs with the following structure:

- `id` (UUID) - Primary key, auto-generated
- `created_at` (TIMESTAMP WITH TIME ZONE) - Auto-set to current time
- `query` (TEXT) - User query sent to worker agent
- `response` (TEXT) - Worker agent response
- `audit` (JSONB) - Audit results from auditor agent
- `status` (TEXT) - Risk status: 'Safe', 'Warning', or 'Flagged'

### Indexes

- `idx_logs_created_at` - Optimizes time-based queries (descending order)
- `idx_logs_status` - Optimizes filtering by risk status
- `idx_logs_risk_score` - Optimizes queries on risk_score from JSONB audit column

### Constraints

- `status` CHECK constraint ensures only valid values: 'Safe', 'Warning', 'Flagged'
