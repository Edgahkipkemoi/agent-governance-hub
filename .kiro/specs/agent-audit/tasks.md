# Implementation Plan: Agent Audit System

## Overview

This implementation plan breaks down the Agent Audit System into discrete, incremental tasks. The system consists of a Python FastAPI backend that orchestrates AI agent interactions, a Supabase database for persistence and real-time updates, and a Next.js 15 frontend dashboard for monitoring and testing.

The implementation follows a bottom-up approach: core services first, then API endpoints, then frontend components, with testing integrated throughout.

## Tasks

- [x] 1. Project setup and environment configuration
  - Create backend directory structure (main.py, services/, utils/, tests/)
  - Create frontend Next.js 15 project with App Router
  - Set up .env.example files for both backend and frontend with all required variables
  - Install backend dependencies: fastapi, uvicorn, groq, google-generativeai, supabase, python-dotenv, httpx
  - Install frontend dependencies: next, react, @supabase/supabase-js, @tremor/react, shadcn/ui components
  - Configure TypeScript and Tailwind CSS for frontend
  - _Requirements: 10.1, 10.2, 10.3, 10.5_

- [x] 2. Database setup and schema
  - [x] 2.1 Create Supabase database schema
    - Write SQL migration for logs table with all columns (id, created_at, query, response, audit, status)
    - Add CHECK constraint for status values
    - Create indexes for created_at, status, and risk_score
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_
  
  - [x]* 2.2 Write property test for UUID uniqueness
    - **Property 8: Unique log identifiers**
    - **Validates: Requirements 3.2, 9.2**
  
  - [x]* 2.3 Write property test for timestamp generation
    - **Property 9: Automatic timestamp generation**
    - **Validates: Requirements 3.3, 9.3**
  
  - [x]* 2.4 Write property test for audit JSON structure
    - **Property 11: Audit JSON structure**
    - **Validates: Requirements 2.2, 9.4**

- [x] 3. Backend core utilities
  - [x] 3.1 Implement risk calculator utility
    - Write calculate_risk_status function (0-3: Safe, 4-6: Warning, 7-10: Flagged)
    - Write calculate_average_risk function
    - _Requirements: 2.4_
  
  - [x] 3.2 Write property test for risk status classification
    - **Property 5: Risk status classification**
    - **Validates: Requirements 2.4**
  
  - [ ]* 3.3 Write unit tests for risk calculator edge cases
    - Test boundary values (0, 3, 4, 6, 7, 10)
    - Test empty log list for average calculation
    - _Requirements: 2.4_

- [-] 4. Backend database service
  - [x] 4.1 Implement DatabaseService class
    - Initialize Supabase client with environment variables
    - Implement create_audit_log method
    - Implement get_recent_logs method
    - Add error handling for connection and query failures
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 10.2_
  
  - [ ]* 4.2 Write property test for audit log completeness
    - **Property 7: Audit log completeness**
    - **Validates: Requirements 3.1, 3.5**
  
  - [ ]* 4.3 Write property test for database error handling
    - **Property 10: Database error handling**
    - **Validates: Requirements 3.4**
  
  - [ ]* 4.4 Write unit tests for database service
    - Test successful log creation
    - Test retrieval with various limits
    - Test connection failure scenarios
    - _Requirements: 3.1, 3.4_

- [ ] 5. Backend agent service
  - [x] 5.1 Implement AgentService class with Groq integration
    - Initialize Groq client with API key from environment
    - Implement process_worker_query method with Llama 3
    - Add retry logic with exponential backoff
    - Add request/response logging
    - _Requirements: 1.1, 7.1, 7.3, 7.4, 7.5_
  
  - [x] 5.2 Implement Gemini auditor integration
    - Initialize Gemini client with API key from environment
    - Implement audit_response method with structured prompt
    - Parse audit results into AuditResult model
    - Add retry logic and error handling
    - _Requirements: 2.1, 2.2, 2.3, 7.2, 7.3, 7.4, 7.5_
  
  - [ ]* 5.3 Write property test for audit trigger completeness
    - **Property 3: Audit trigger completeness**
    - **Validates: Requirements 2.1**
  
  - [ ]* 5.4 Write property test for risk score validity
    - **Property 4: Risk score validity**
    - **Validates: Requirements 2.3**
  
  - [ ]* 5.5 Write property test for retry with exponential backoff
    - **Property 15: Retry with exponential backoff**
    - **Validates: Requirements 7.4**
  
  - [ ]* 5.6 Write property test for API interaction logging
    - **Property 16: API interaction logging**
    - **Validates: Requirements 7.5**
  
  - [ ]* 5.7 Write unit tests for agent service
    - Test successful worker query processing
    - Test successful audit response
    - Test API failure scenarios
    - _Requirements: 1.1, 2.1, 2.2_

- [x] 6. Checkpoint - Core backend services complete
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 7. Backend API endpoints and middleware
  - [x] 7.1 Implement FastAPI application with CORS
    - Set up FastAPI app with CORS middleware
    - Configure allowed origins from FRONTEND_URL environment variable
    - Add request logging middleware
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 10.3_
  
  - [x] 7.2 Implement environment variable validation
    - Check all required environment variables at startup
    - Fail with clear error messages if any are missing
    - _Requirements: 10.4_
  
  - [ ] 7.3 Implement POST /process-agent endpoint
    - Validate request payload (user_query field, non-empty)
    - Call worker agent service
    - Call auditor agent service
    - Calculate risk status
    - Store audit log in database
    - Return complete audit log response
    - Handle all error cases with appropriate status codes
    - _Requirements: 1.1, 1.3, 1.4, 1.5, 2.1, 2.4, 2.5, 3.1, 12.2, 12.4_
  
  - [ ] 7.4 Implement GET /health endpoint
    - Return simple health check response
    - _Requirements: (infrastructure)_
  
  - [ ]* 7.5 Write property test for empty query rejection
    - **Property 1: Empty query rejection**
    - **Validates: Requirements 1.5**
  
  - [ ]* 7.6 Write property test for worker agent error handling
    - **Property 2: Worker agent error handling**
    - **Validates: Requirements 1.3**
  
  - [ ]* 7.7 Write property test for auditor failure fallback
    - **Property 6: Auditor failure fallback**
    - **Validates: Requirements 2.5**
  
  - [ ]* 7.8 Write property test for CORS header presence
    - **Property 12: CORS header presence**
    - **Validates: Requirements 8.3**
  
  - [ ]* 7.9 Write property test for CORS origin validation
    - **Property 13: CORS origin validation**
    - **Validates: Requirements 8.5**
  
  - [ ]* 7.10 Write property test for environment variable configuration
    - **Property 14: Environment variable configuration**
    - **Validates: Requirements 10.1, 10.2, 10.3, 10.4**
  
  - [ ]* 7.11 Write property test for concurrent request handling
    - **Property 17: Concurrent request handling**
    - **Validates: Requirements 11.2**
  
  - [ ]* 7.12 Write property test for error response structure
    - **Property 18: Error response structure**
    - **Validates: Requirements 12.2**
  
  - [ ]* 7.13 Write property test for error classification
    - **Property 19: Error classification**
    - **Validates: Requirements 12.4**
  
  - [ ]* 7.14 Write property test for request logging
    - **Property 20: Request logging**
    - **Validates: Requirements 12.5**
  
  - [ ]* 7.15 Write property test for error detail logging
    - **Property 21: Error detail logging**
    - **Validates: Requirements 12.1**
  
  - [ ]* 7.16 Write unit tests for API endpoints
    - Test successful query processing
    - Test validation errors (empty query, missing field)
    - Test worker failure handling
    - Test auditor failure handling
    - Test database failure handling
    - _Requirements: 1.3, 1.4, 1.5, 2.5, 3.4_

- [x] 8. Checkpoint - Backend API complete
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 9. Frontend setup and configuration
  - [ ] 9.1 Configure Supabase client
    - Create Supabase client with environment variables
    - Set up TypeScript types for AuditLog
    - _Requirements: 10.2_
  
  - [ ] 9.2 Create API client utility
    - Implement function to call POST /process-agent
    - Add error handling and type safety
    - _Requirements: 6.2_
  
  - [ ] 9.3 Set up Shadcn/ui and Tremor components
    - Install and configure required UI components
    - Set up dark theme configuration
    - _Requirements: (UI infrastructure)_

- [ ] 10. Frontend core components
  - [ ] 10.1 Implement StatusBadge component
    - Create badge with color mapping (Safe: green, Warning: yellow, Flagged: red)
    - Add optional risk score display
    - _Requirements: 5.2_
  
  - [ ]* 10.2 Write property test for status badge color mapping
    - **Property 27: Status badge color mapping**
    - **Validates: Requirements 5.2**
  
  - [ ] 10.3 Implement RiskGauge component
    - Use Tremor chart component for visualization
    - Calculate and display average risk score
    - Color-code based on risk level
    - _Requirements: 5.1_
  
  - [ ]* 10.4 Write property test for average risk calculation
    - **Property 26: Average risk calculation**
    - **Validates: Requirements 5.1**
  
  - [ ]* 10.5 Write unit tests for RiskGauge
    - Test with empty logs (zero state)
    - Test with various risk score combinations
    - Test color coding at boundaries
    - _Requirements: 5.1, 5.5_

- [ ] 11. Frontend test query input
  - [ ] 11.1 Implement TestQueryInput component
    - Create input field with submit button
    - Add loading state during processing
    - Add error message display
    - Call API client on submission
    - _Requirements: 6.1, 6.2, 6.4, 6.5_
  
  - [ ]* 11.2 Write property test for test query submission
    - **Property 30: Test query submission**
    - **Validates: Requirements 6.2**
  
  - [ ]* 11.3 Write property test for loading state feedback
    - **Property 32: Loading state feedback**
    - **Validates: Requirements 6.4**
  
  - [ ]* 11.4 Write property test for error message display
    - **Property 33: Error message display**
    - **Validates: Requirements 6.5, 12.3**
  
  - [ ]* 11.5 Write unit tests for TestQueryInput
    - Test form submission
    - Test loading state transitions
    - Test error display
    - _Requirements: 6.2, 6.4, 6.5_

- [ ] 12. Frontend audit log table
  - [ ] 12.1 Implement AuditLogTable component
    - Create table with Shadcn/ui Table component
    - Display columns: timestamp, query, response, risk score, status badge
    - Add pagination or virtual scrolling for performance
    - _Requirements: 5.4, 11.5_
  
  - [ ]* 12.2 Write property test for risk score display
    - **Property 29: Risk score display**
    - **Validates: Requirements 5.4**
  
  - [ ]* 12.3 Write unit tests for AuditLogTable
    - Test rendering with sample data
    - Test empty state
    - Test pagination/virtualization
    - _Requirements: 5.4_

- [ ] 13. Frontend real-time subscription
  - [ ] 13.1 Implement real-time subscription in dashboard page
    - Set up Supabase real-time channel for logs table
    - Subscribe to INSERT events
    - Update logs state when new logs arrive
    - Add connection status tracking
    - Implement automatic reconnection logic
    - Implement missed update synchronization on reconnect
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_
  
  - [ ]* 13.2 Write property test for real-time log display
    - **Property 22: Real-time log display**
    - **Validates: Requirements 4.2**
  
  - [ ]* 13.3 Write property test for automatic reconnection
    - **Property 23: Automatic reconnection**
    - **Validates: Requirements 4.3**
  
  - [ ]* 13.4 Write property test for connection status indicator
    - **Property 24: Connection status indicator**
    - **Validates: Requirements 4.4**
  
  - [ ]* 13.5 Write property test for missed update synchronization
    - **Property 25: Missed update synchronization**
    - **Validates: Requirements 4.5**
  
  - [ ]* 13.6 Write unit tests for real-time subscription
    - Test connection establishment
    - Test disconnection handling
    - Test reconnection flow
    - _Requirements: 4.2, 4.3, 4.5_

- [ ] 14. Frontend dashboard page integration
  - [ ] 14.1 Implement main dashboard page
    - Compose all components (TestQueryInput, RiskGauge, AuditLogTable)
    - Set up state management for logs and metrics
    - Wire up real-time subscription
    - Calculate and update average risk on log changes
    - Add connection status indicator
    - Apply dark theme styling
    - _Requirements: 4.2, 5.1, 5.3, 6.3_
  
  - [ ]* 14.2 Write property test for risk gauge updates
    - **Property 28: Risk gauge updates**
    - **Validates: Requirements 5.3**
  
  - [ ]* 14.3 Write property test for result display after submission
    - **Property 31: Result display after submission**
    - **Validates: Requirements 6.3**
  
  - [ ]* 14.4 Write unit tests for dashboard page
    - Test initial render
    - Test empty state
    - Test state updates on new logs
    - _Requirements: 4.2, 5.3, 6.3_

- [x] 15. Checkpoint - Frontend complete
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 16. Integration and documentation
  - [ ] 16.1 Create comprehensive .env.example files
    - Backend: GROQ_API_KEY, GEMINI_API_KEY, SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, FRONTEND_URL
    - Frontend: NEXT_PUBLIC_SUPABASE_URL, NEXT_PUBLIC_SUPABASE_ANON_KEY, NEXT_PUBLIC_API_URL
    - _Requirements: 10.5_
  
  - [ ] 16.2 Create README with setup instructions
    - Installation steps for backend and frontend
    - Environment variable configuration
    - Database setup instructions
    - Running the application
    - Testing instructions
    - _Requirements: 10.5_
  
  - [ ] 16.3 Add API documentation
    - Document POST /process-agent endpoint
    - Document GET /health endpoint
    - Include request/response examples
    - Document error responses
    - _Requirements: (documentation)_

- [x] 17. Final checkpoint - End-to-end testing
  - Test complete flow: submit query → worker processes → auditor evaluates → database stores → dashboard displays
  - Test error scenarios: worker failure, auditor failure, database failure
  - Test real-time updates: multiple queries, connection loss/reconnection
  - Test concurrent queries
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Property tests validate universal correctness properties with minimum 100 iterations
- Unit tests validate specific examples and edge cases
- The implementation follows a bottom-up approach: services → API → frontend
- Checkpoints ensure incremental validation at major milestones
- All environment variables must be configured before running the application
- The system requires active Groq, Gemini, and Supabase accounts with valid API keys
