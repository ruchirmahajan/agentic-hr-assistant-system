#!/bin/bash

# Create database schemas
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    -- Create schemas for HR data organization
    CREATE SCHEMA IF NOT EXISTS hr_core;
    CREATE SCHEMA IF NOT EXISTS hr_audit;
    CREATE SCHEMA IF NOT EXISTS hr_analytics;

    -- Create custom types
    CREATE TYPE job_status_enum AS ENUM (
        'draft', 'published', 'paused', 'closed', 'archived'
    );

    CREATE TYPE application_status_enum AS ENUM (
        'submitted', 'screening', 'interview_scheduled', 
        'interview_completed', 'shortlisted', 'rejected', 
        'offer_extended', 'hired', 'withdrawn'
    );

    CREATE TYPE interview_status_enum AS ENUM (
        'scheduled', 'in_progress', 'completed', 'cancelled', 'rescheduled'
    );

    CREATE TYPE seniority_level_enum AS ENUM (
        'intern', 'junior', 'mid', 'senior', 'lead', 'manager', 'director'
    );

    CREATE TYPE document_type_enum AS ENUM (
        'resume', 'cover_letter', 'portfolio', 'certificate', 'other'
    );

    -- Enable UUID extension
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
    CREATE EXTENSION IF NOT EXISTS "pgcrypto";

    -- Grant permissions to schemas
    GRANT USAGE ON SCHEMA hr_core TO $POSTGRES_USER;
    GRANT USAGE ON SCHEMA hr_audit TO $POSTGRES_USER;
    GRANT USAGE ON SCHEMA hr_analytics TO $POSTGRES_USER;

    GRANT CREATE ON SCHEMA hr_core TO $POSTGRES_USER;
    GRANT CREATE ON SCHEMA hr_audit TO $POSTGRES_USER;
    GRANT CREATE ON SCHEMA hr_analytics TO $POSTGRES_USER;

    COMMIT;
EOSQL