# Alembic Database Migrations

This directory contains database migration files for P24_SlotHunter.

## Files

- `env.py` - Alembic environment configuration
- `script.py.mako` - Template for generating migration files
- `versions/` - Directory containing migration files

## Usage

### Create a new migration
```bash
alembic revision --autogenerate -m "Description of changes"
```

### Apply migrations
```bash
alembic upgrade head
```

### Downgrade migrations
```bash
alembic downgrade -1
```

### Show current revision
```bash
alembic current
```

### Show migration history
```bash
alembic history
```

## Notes

- Migrations are automatically created and applied by the server manager
- The database uses SQLite by default
- All models are defined in `src/database/models.py`