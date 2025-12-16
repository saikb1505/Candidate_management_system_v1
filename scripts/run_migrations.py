#!/usr/bin/env python
"""
Run database migrations for Railway deployment.
This script can be executed directly with python.
"""
import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from alembic import command
from alembic.config import Config


def run_migrations():
    """Run all pending database migrations."""
    try:
        # Get the alembic.ini file path
        alembic_ini_path = project_root / "alembic.ini"

        if not alembic_ini_path.exists():
            print(f"Error: alembic.ini not found at {alembic_ini_path}")
            sys.exit(1)

        # Create Alembic config
        alembic_cfg = Config(str(alembic_ini_path))

        # Set the script location (alembic directory)
        alembic_cfg.set_main_option("script_location", str(project_root / "alembic"))

        print("Starting database migrations...")
        print(f"Alembic config: {alembic_ini_path}")
        print(f"Script location: {project_root / 'alembic'}")

        # Run migrations to head
        command.upgrade(alembic_cfg, "head")

        print("✓ Database migrations completed successfully!")
        return 0

    except Exception as e:
        print(f"✗ Migration failed: {str(e)}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(run_migrations())
