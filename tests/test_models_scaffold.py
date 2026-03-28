def test_models_import_and_tables(engine):
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    for name in ["users", "subscriptions", "schools", "planeaciones", "usage_log"]:
        assert name in tables, f"Missing table: {name}"
