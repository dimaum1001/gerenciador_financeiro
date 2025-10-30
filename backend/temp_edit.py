import pathlib
import re

path = pathlib.Path('app/services/demo_data.py')
text = path.read_text(encoding='utf-8')

new_block1 = """def _ensure_is_demo_column(session: Session) -> None:
    # Garante que a coluna is_demo exista no banco (necessario para bases antigas).
    bind = session.bind
    dialect_name = bind.dialect.name if bind is not None else ""

    if dialect_name != "sqlite":
        try:
            session.execute(
                text(
                    "ALTER TABLE IF EXISTS users "
                    "ADD COLUMN IF NOT EXISTS is_demo BOOLEAN NOT NULL DEFAULT FALSE"
                )
            )
            session.commit()
        except OperationalError:
            session.rollback()
            raise
        return

    inspector = inspect(bind)
    columns = {column["name"] for column in inspector.get_columns("users")}
    if "is_demo" in columns:
        return

    try:
        session.execute(
            text("ALTER TABLE users ADD COLUMN is_demo BOOLEAN NOT NULL DEFAULT FALSE")
        )
        session.commit()
    except OperationalError:
        session.rollback()
        raise
"""

pattern1 = r"def _ensure_is_demo_column\(session: Session\) -> None:\r?\n(?:    .*\r?\n)+?(?=\r?\ndef _ensure_demo_data_columns)"
text = re.sub(pattern1, new_block1 + "\n", text, flags=re.S)

new_block2 = """def _ensure_demo_data_columns(session: Session) -> None:
    # Garante que as colunas is_demo_data existam nas tabelas relacionadas.
    bind = session.bind
    dialect_name = bind.dialect.name if bind is not None else ""

    tables = ["accounts", "categories", "transactions", "budgets", "recurring_rules"]
    if dialect_name != "sqlite":
        try:
            for table in tables:
                session.execute(
                    text(
                        "ALTER TABLE IF EXISTS "
                        f"{table} ADD COLUMN IF NOT EXISTS "
                        "is_demo_data BOOLEAN NOT NULL DEFAULT FALSE"
                    )
                )
            session.commit()
        except OperationalError:
            session.rollback()
            raise
        return

    inspector = inspect(bind)
    for table in tables:
        columns = {column["name"] for column in inspector.get_columns(table)}
        if "is_demo_data" in columns:
            continue
        try:
            session.execute(
                text(
                    f"ALTER TABLE {table} ADD COLUMN is_demo_data BOOLEAN NOT NULL DEFAULT FALSE"
                )
            )
            session.commit()
        except OperationalError:
            session.rollback()
            raise
"""

pattern2 = r"def _ensure_demo_data_columns\(session: Session\) -> None:\r?\n(?:    .*\r?\n)+?(?=\r?\ndef _mark_demo_rows)"
text = re.sub(pattern2, new_block2 + "\n", text, flags=re.S)

path.write_text(text, encoding='utf-8')
