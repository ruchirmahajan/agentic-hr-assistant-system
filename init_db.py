#!/usr/bin/env python3
"""
Simple database initialization script for SQLite MVP
No complex migrations needed - just create the tables!
"""
import sys
import asyncio
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

async def init_database():
    """Initialize the SQLite database with tables"""
    from core.database import engine, Base
    from models import user, candidate, job, application  # Import all models
    
    print("🗄️ Creating SQLite database tables...")
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    print("✅ Database tables created successfully!")
    
    # Create default admin user
    from core.security import security_utils
    from models.user import User, UserRole
    from core.database import get_db_session
    
    async for session in get_db_session():
        try:
            # Check if admin user exists
            from sqlalchemy import select
            result = await session.execute(select(User).where(User.username == "admin"))
            admin_user = result.scalar_one_or_none()
            
            if not admin_user:
                print("👤 Creating default admin user...")
                admin_user = User(
                    username="admin",
                    email="admin@hrapp.com",
                    hashed_password=security_utils.hash_password("admin123"),
                    first_name="Admin",
                    last_name="User",
                    role=UserRole.ADMIN,
                    is_active=True,
                    is_verified=True
                )
                session.add(admin_user)
                await session.commit()
                print("✅ Default admin user created!")
                print("   Username: admin")
                print("   Password: admin123")
            else:
                print("ℹ️ Admin user already exists")
            
            break
            
        except Exception as e:
            print(f"⚠️ Could not create admin user: {e}")
            await session.rollback()
            break

def main():
    """Run database initialization"""
    print("🚀 Initializing FREE HR Assistant Database...")
    try:
        asyncio.run(init_database())
        print("🎉 Database initialization complete!")
        return True
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False

if __name__ == "__main__":
    if main():
        print("\n💡 Next steps:")
        print("   1. Run: python start_mvp.py")
        print("   2. Open: http://localhost:8000/docs")
        print("   3. Login with admin/admin123")
        sys.exit(0)
    else:
        print("❌ Setup failed")
        sys.exit(1)