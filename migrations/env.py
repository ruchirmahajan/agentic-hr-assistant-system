"""
Alembic environment configuration for HR Assistant
"""
import logging
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool

from alembic import context

# Import your models here to ensure they are available for autogenerate
from src.core.database_sync import sync_engine, Base
from src.models import User, Candidate, Job, Application
from src.models.job import Job
from src.models.application import Application
from src.core.database import Base
from src.core.config import settings

# Alembic Config object
config = context.config

# Setup logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

logger = logging.getLogger('alembic.env')

# Add your model's MetaData object here for 'autogenerate' support
target_metadata = Base.metadata

# Set the database URL from settings
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    
    # Create synchronous engine  
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=target_metadata,
            render_as_batch=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()