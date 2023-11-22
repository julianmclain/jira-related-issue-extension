import sqlite3
from sqlite3 import Connection

from jira_ops import SimpleIssue


def connect_to_db(name: str) -> Connection:
    conn = sqlite3.connect(name)
    conn.enable_load_extension(True)
    return conn


def create_tables(conn: Connection) -> None:
    conn.execute(
        """
            CREATE TABLE IF NOT EXISTS issues(
                id INTEGER PRIMARY KEY,
                key TEXT UNIQUE,
                summary TEXT,
                url TEXT,
                embedding BLOB
            );
        """
    )

    # This is the vector search index
    # 384 == number of dimensions by all-MiniLM-L6-v2
    # See https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2
    conn.execute(
        """
            CREATE VIRTUAL TABLE IF NOT EXISTS vss_issues USING vss0(
                embedding(384)
            );
        """
    )


def insert_issue(
    conn: Connection, issue: SimpleIssue, embedding: bytes
) -> None:
    conn.execute(
        "INSERT INTO issues (id, key, summary, url, embedding) values (?, ?, ?, ?, ?);",
        (None, issue.key, issue.summary, None, embedding),
    )
    conn.commit()


def populate_vss_index(conn: Connection) -> None:
    conn.execute(
        "INSERT INTO vss_issues(rowid, embedding) SELECT rowid, embedding FROM issues;"
    )
    conn.commit()
