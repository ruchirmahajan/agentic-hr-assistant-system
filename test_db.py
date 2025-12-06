#!/usr/bin/env python
"""
Simple database connection test
"""
import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from sqlalchemy import create_engine, text
from src.core.config import settings

def test_database_connection():
    """Test database connection without models"""
    try:
        # Create simple engine
        engine = create_engine(settings.DATABASE_URL, echo=True)
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"✅ Database connected successfully!")
            print(f"PostgreSQL version: {version}")
            
        # Create schema if it doesn't exist
        with engine.connect() as conn:
            conn.execute(text("CREATE SCHEMA IF NOT EXISTS hr_core"))
            conn.commit()
            print("✅ Schema 'hr_core' created/verified")
            
        print("✅ Database setup successful!")
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

if __name__ == "__main__":
    test_database_connection()