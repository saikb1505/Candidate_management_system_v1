-- Fix for CandidateStatus ENUM on Railway
-- This script ensures the candidatestatus type has all required values
-- It's idempotent - safe to run multiple times

-- ============================================================================
-- STEP 1: Check current enum values (for verification)
-- ============================================================================
-- Uncomment to see current values before running the fix:
-- SELECT e.enumlabel
-- FROM pg_type t
-- JOIN pg_enum e ON t.oid = e.enumtypid
-- WHERE t.typname = 'candidatestatus'
-- ORDER BY e.enumlabel;

-- ============================================================================
-- STEP 2: Fix the ENUM type
-- ============================================================================

-- Check if candidatestatus_new already exists and drop it if it does
DROP TYPE IF EXISTS candidatestatus_new;

-- Create a new enum type with all required values
CREATE TYPE candidatestatus_new AS ENUM (
    'uploaded',
    'processing',
    'completed',
    'failed',
    'reviewing',
    'callback_requested',
    'initial_screening_completed',
    'interview_scheduled',
    'selected',
    'rejected'
);

-- Drop the default constraint temporarily
ALTER TABLE candidates ALTER COLUMN status DROP DEFAULT;

-- Alter the column to use the new enum type
-- This will fail if there are any values in the table that don't match
ALTER TABLE candidates
ALTER COLUMN status TYPE candidatestatus_new
USING (status::text::candidatestatus_new);

-- Drop the old enum type
DROP TYPE candidatestatus;

-- Rename the new enum type to the original name
ALTER TYPE candidatestatus_new RENAME TO candidatestatus;

-- Re-add the default constraint
ALTER TABLE candidates ALTER COLUMN status SET DEFAULT 'uploaded'::candidatestatus;

-- ============================================================================
-- STEP 3: Verify the fix
-- ============================================================================
-- Uncomment to verify all values are present:
-- SELECT e.enumlabel
-- FROM pg_type t
-- JOIN pg_enum e ON t.oid = e.enumtypid
-- WHERE t.typname = 'candidatestatus'
-- ORDER BY e.enumlabel;

-- Expected output (10 values):
-- callback_requested
-- completed
-- failed
-- initial_screening_completed
-- interview_scheduled
-- processing
-- rejected
-- reviewing
-- selected
-- uploaded
