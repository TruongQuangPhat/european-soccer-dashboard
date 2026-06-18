from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

import pandas as pd


def quote_identifier(identifier: str) -> str:
    """Return a safely quoted SQLite identifier."""
    return '"' + identifier.replace('"', '""') + '"'


def connect_sqlite_readonly(database_path: Path) -> sqlite3.Connection:
    """Open a SQLite database connection in read-only mode."""
    database_uri = f"file:{database_path.resolve().as_posix()}?mode=ro"
    return sqlite3.connect(database_uri, uri=True)


def list_user_tables(connection: sqlite3.Connection) -> pd.DataFrame:
    """List non-system SQLite tables."""
    return pd.read_sql_query(
        """
        SELECT name AS table_name
        FROM sqlite_master
        WHERE type = 'table'
          AND name NOT LIKE 'sqlite_%'
        ORDER BY name;
        """,
        connection,
    )


def get_table_schema(connection: sqlite3.Connection, table_name: str) -> pd.DataFrame:
    """Return SQLite schema metadata for one table."""
    quoted_table = quote_identifier(table_name)
    schema = pd.read_sql_query(f"PRAGMA table_info({quoted_table});", connection)
    schema["table_name"] = table_name
    return schema.rename(
        columns={
            "name": "column_name",
            "type": "data_type",
            "notnull": "not_null",
            "pk": "primary_key",
        }
    )


def count_table_rows(connection: sqlite3.Connection, table_name: str) -> int:
    """Count rows in one SQLite table."""
    quoted_table = quote_identifier(table_name)
    result = pd.read_sql_query(
        f"SELECT COUNT(*) AS row_count FROM {quoted_table};",
        connection,
    )
    return int(result.iloc[0, 0])


def profile_key_candidate(
    connection: sqlite3.Connection,
    table_name: str,
    key_columns: list[str],
) -> dict[str, Any]:
    """Profile NULL and duplicate groups for a candidate key."""
    quoted_table = quote_identifier(table_name)
    quoted_columns = [quote_identifier(column) for column in key_columns]
    key_expression = ", ".join(quoted_columns)
    null_condition = " OR ".join(f"{column} IS NULL" for column in quoted_columns)
    not_null_condition = " AND ".join(
        f"{column} IS NOT NULL" for column in quoted_columns
    )

    total_rows = count_table_rows(connection, table_name)
    null_key_rows = pd.read_sql_query(
        f"SELECT COUNT(*) AS row_count FROM {quoted_table} WHERE {null_condition};",
        connection,
    ).iloc[0, 0]
    duplicate_key_groups = pd.read_sql_query(
        f"""
        SELECT COUNT(*) AS duplicate_key_groups
        FROM (
            SELECT {key_expression}, COUNT(*) AS row_count
            FROM {quoted_table}
            WHERE {not_null_condition}
            GROUP BY {key_expression}
            HAVING COUNT(*) > 1
        ) AS duplicate_groups;
        """,
        connection,
    ).iloc[0, 0]

    return {
        "table_name": table_name,
        "key_columns": " + ".join(key_columns),
        "null_key_rows": int(null_key_rows),
        "duplicate_key_groups": int(duplicate_key_groups),
        "unique_and_not_null": int(null_key_rows) == 0
        and int(duplicate_key_groups) == 0,
        "row_count": total_rows,
    }


def check_foreign_key_integrity(
    connection: sqlite3.Connection,
    child_table: str,
    child_column: str,
    parent_table: str,
    parent_column: str,
) -> dict[str, Any]:
    """Check orphan keys for one foreign-key relationship."""
    child_values = pd.read_sql_query(
        f"""
        SELECT {quote_identifier(child_column)} AS child_value
        FROM {quote_identifier(child_table)}
        WHERE {quote_identifier(child_column)} IS NOT NULL;
        """,
        connection,
    )["child_value"]
    parent_values = pd.read_sql_query(
        f"""
        SELECT {quote_identifier(parent_column)} AS parent_value
        FROM {quote_identifier(parent_table)}
        WHERE {quote_identifier(parent_column)} IS NOT NULL;
        """,
        connection,
    )["parent_value"]

    parent_value_set = set(parent_values.dropna().unique())
    orphan_mask = ~child_values.isin(parent_value_set)
    orphan_values = child_values.loc[orphan_mask]

    return {
        "child_table": child_table,
        "child_column": child_column,
        "parent_table": parent_table,
        "parent_column": parent_column,
        "non_null_child_rows": int(child_values.shape[0]),
        "orphan_key_count": int(orphan_values.nunique()),
        "orphan_row_count": int(orphan_mask.sum()),
        "all_valid": int(orphan_mask.sum()) == 0,
    }


def profile_relationship_cardinality(
    connection: sqlite3.Connection,
    child_table: str,
    child_column: str,
    parent_table: str,
    parent_column: str,
) -> dict[str, Any]:
    """Profile observed cardinality for one relationship."""
    child_counts = pd.read_sql_query(
        f"""
        SELECT {quote_identifier(child_column)} AS key_value, COUNT(*) AS child_row_count
        FROM {quote_identifier(child_table)}
        WHERE {quote_identifier(child_column)} IS NOT NULL
        GROUP BY {quote_identifier(child_column)};
        """,
        connection,
    )
    parent_counts = pd.read_sql_query(
        f"""
        SELECT {quote_identifier(parent_column)} AS key_value, COUNT(*) AS parent_row_count
        FROM {quote_identifier(parent_table)}
        WHERE {quote_identifier(parent_column)} IS NOT NULL
        GROUP BY {quote_identifier(parent_column)};
        """,
        connection,
    )

    parent_has_duplicate_keys = bool((parent_counts["parent_row_count"] > 1).any())
    max_child_rows_per_key = (
        int(child_counts["child_row_count"].max()) if not child_counts.empty else 0
    )

    if parent_has_duplicate_keys:
        observed_cardinality = "Parent key không unique"
    elif max_child_rows_per_key <= 1:
        observed_cardinality = "1:1 observed"
    else:
        observed_cardinality = "1:N observed"

    return {
        "child_table": child_table,
        "child_column": child_column,
        "parent_table": parent_table,
        "parent_column": parent_column,
        "parent_has_duplicate_keys": parent_has_duplicate_keys,
        "max_child_rows_per_key": max_child_rows_per_key,
        "observed_cardinality": observed_cardinality,
    }


def check_functional_dependency(
    connection: sqlite3.Connection,
    table_name: str,
    determinant_columns: list[str],
    dependent_column: str,
    dependency_type: str,
) -> dict[str, Any]:
    """Check whether determinant columns identify one dependent value."""
    quoted_table = quote_identifier(table_name)
    quoted_determinants = [quote_identifier(column) for column in determinant_columns]
    determinant_expression = ", ".join(quoted_determinants)
    determinant_not_null_condition = " AND ".join(
        f"{column} IS NOT NULL" for column in quoted_determinants
    )
    dependent_value_expression = (
        f"COALESCE(CAST({quote_identifier(dependent_column)} AS TEXT), '__NULL__')"
    )

    group_report = pd.read_sql_query(
        f"""
        SELECT dependent_value_count
        FROM (
            SELECT {determinant_expression},
                   COUNT(DISTINCT {dependent_value_expression}) AS dependent_value_count
            FROM {quoted_table}
            WHERE {determinant_not_null_condition}
            GROUP BY {determinant_expression}
        ) AS grouped_values;
        """,
        connection,
    )

    if group_report.empty:
        max_dependent_values = 0
        violation_group_count = 0
    else:
        max_dependent_values = int(group_report["dependent_value_count"].max())
        violation_group_count = int((group_report["dependent_value_count"] > 1).sum())

    return {
        "table_name": table_name,
        "determinant": " + ".join(determinant_columns),
        "dependent": dependent_column,
        "dependency_type": dependency_type,
        "max_dependent_values": max_dependent_values,
        "violation_group_count": violation_group_count,
        "dependency_status": "Supported" if violation_group_count == 0 else "Violated",
    }


def summarize_missing_values(
    dataframe: pd.DataFrame,
    columns: list[str] | None = None,
    *,
    table_name: str | None = None,
) -> pd.DataFrame:
    """Summarize missing values for selected DataFrame columns."""
    selected = dataframe[columns].copy() if columns is not None else dataframe.copy()
    report = pd.DataFrame(
        {
            "column_name": selected.columns,
            "missing_count": selected.isna().sum().values,
            "missing_rate_pct": (selected.isna().mean().values * 100).round(2),
        }
    )
    if table_name is not None:
        report.insert(0, "table_name", table_name)
    return report


def summarize_duplicate_key(
    dataframe: pd.DataFrame,
    key_columns: list[str],
) -> dict[str, Any]:
    """Summarize duplicated rows for a key column set."""
    duplicated_mask = dataframe.duplicated(subset=key_columns, keep=False)
    duplicate_groups = (
        dataframe.loc[duplicated_mask]
        .groupby(key_columns, dropna=False)
        .size()
        .shape[0]
    )
    return {
        "key_columns": " + ".join(key_columns),
        "duplicate_rows": int(duplicated_mask.sum()),
        "duplicate_groups": int(duplicate_groups),
    }


def calculate_iqr_bounds(
    series: pd.Series,
    multiplier: float = 1.5,
) -> tuple[float, float]:
    """Return lower and upper IQR fences for a numeric Series."""
    q1 = float(series.quantile(0.25))
    q3 = float(series.quantile(0.75))
    iqr = q3 - q1
    return q1 - multiplier * iqr, q3 + multiplier * iqr
