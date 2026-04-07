from pathlib import Path


def test_events_migration_exists() -> None:
    migration_path = (
        Path(__file__).resolve().parents[1]
        / "migrations"
        / "versions"
        / "003_add_events_table.py"
    )
    assert migration_path.is_file()


def test_events_migration_revision_chain() -> None:
    migration_path = (
        Path(__file__).resolve().parents[1]
        / "migrations"
        / "versions"
        / "003_add_events_table.py"
    )
    content = migration_path.read_text(encoding="utf-8")
    assert 'revision: str = "003"' in content
    assert 'down_revision: Union[str, None] = "002"' in content


def test_events_migration_indexes_present() -> None:
    migration_path = (
        Path(__file__).resolve().parents[1]
        / "migrations"
        / "versions"
        / "003_add_events_table.py"
    )
    content = migration_path.read_text(encoding="utf-8")
    assert "ix_events_start_datetime" in content
    assert "ix_events_name" in content
    assert "ix_events_category" in content
    assert "ix_events_is_recurring" in content
    assert "ix_events_dedup_key" in content
