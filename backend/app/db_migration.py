from sqlalchemy import inspect, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.engine import Engine


def _add_column_if_missing(engine: Engine, table_name: str, column_name: str, ddl: str):
    with engine.begin() as conn:
        inspector = inspect(conn)
        if table_name not in inspector.get_table_names():
            return
        existing_columns = {column["name"] for column in inspector.get_columns(table_name)}
        if column_name in existing_columns:
            return
        try:
            conn.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {ddl}"))
        except SQLAlchemyError:
            pass


def run_schema_migrations(engine: Engine):
    from . import models

    models.AudioExplanation.__table__.create(bind=engine, checkfirst=True)

    _add_column_if_missing(engine, "volunteers", "gender", "VARCHAR(10)")
    _add_column_if_missing(engine, "volunteers", "id_card", "VARCHAR(18)")
    _add_column_if_missing(engine, "volunteers", "age", "INTEGER")
    _add_column_if_missing(engine, "volunteers", "ethnicity", "VARCHAR(30)")
    _add_column_if_missing(engine, "volunteers", "service_time", "VARCHAR(100)")
    _add_column_if_missing(engine, "volunteers", "organization", "VARCHAR(120)")
    _add_column_if_missing(engine, "volunteers", "position", "VARCHAR(120)")
