import sqlite3
from sqlite3 import Connection
from jira import JIRA
from jira.resources import Issue
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer, util

import sys
import os
import traceback
from typing import Dict, List


def save_embeddings(
    query_string: str, jira: JIRA, db: Connection, model: SentenceTransformer
) -> int:
    total_hits = 0
    last_hits = None

    while last_hits != 0:
        issues = search_jira_paginated(
            jira,
            query_string,
            10,
            total_hits,
        )
        handle_search_page(db, model, issues)

        hits = len(issues)
        total_hits += hits
        last_hits = hits
        print(f"processed {last_hits} hits")

    return total_hits


def search_jira_paginated(
    jira: JIRA, qs: str, max_results: int = 100, start_at: int = 0
):
    expand_fields = {
        "children": True,
        "ancestors": True,
        "issuetypes": True,
        "names": True,
        "changelog": False,
        "renderedFields": False,
        "operations": False,
        "editmeta": False,
        "versionedRepresentations": False,
    }

    FIELD_MAP = {"_".join(f["name"].lower().split()): f["key"] for f in jira.fields()}
    FIELDS = [
        "key",
        "summary",
        "issuetype",
        "components",
        "created",
        "resolved",
        "description",
        "labels",
        "priority",
        "comment",
    ]
    FIELD_LIST = sorted([FIELD_MAP.get(f, f) for f in FIELDS])

    return jira.search_issues(
        qs,
        maxResults=max_results,
        startAt=start_at,
        expand=expand_fields,
        fields=FIELD_LIST,
    )


def handle_search_page(
    db: Connection, model: SentenceTransformer, issues: List[Issue]
) -> None:
    for issue in issues:
        simple_issue = create_simple_issue(issue)
        issue_string = ". ".join(list(simple_issue.values()))
        embedding = model.encode(issue_string)
        insert_issue(db, simple_issue, embedding.tobytes())


def create_simple_issue(issue: Issue, include_comments: bool = True):
    raw_issue = issue.raw
    all_fields = raw_issue["fields"]

    simple_issue = {}
    simple_issue["key"] = raw_issue["key"]
    simple_issue["summary"] = all_fields["summary"]
    simple_issue["description"] = all_fields["description"]
    simple_issue["labels"] = " ".join([f["name"] for f in all_fields["components"]])
    if include_comments:
        simple_issue["comments"] = " ".join(
            [f["body"] for f in all_fields["comment"]["comments"]]
        )

    return simple_issue


def connect_to_db(name: str) -> Connection:
    db = sqlite3.connect(name)
    db.enable_load_extension(True)
    return db


def create_issue_table(db: Connection) -> None:
    db.execute(
        """
            CREATE TABLE IF NOT EXISTS issues(
                id INTEGER PRIMARY KEY,
                jira_key TEXT UNIQUE,
                embedding BLOB
            )
        """
    )


def insert_issue(
    db: Connection, simple_issue: Dict[str, str], embedding: bytes
) -> None:
    db.execute(
        "INSERT INTO issues (id, jira_key, embedding) values (?, ?, ?)",
        (None, simple_issue["key"], embedding),
    )
    db.commit()


if __name__ == "__main__":
    load_dotenv()
    try:
        db_name = "jira-issue-embeddings.db"
        db = connect_to_db(db_name)
        create_issue_table(db)

        jira = JIRA(
            server="https://iterable.atlassian.net/",
            basic_auth=(os.getenv("JIRA_USERNAME"), os.getenv("JIRA_API_TOKEN")),
        )

        query = "type = 'On Call Question' and created > -180d and created < -30d"

        model = SentenceTransformer("all-MiniLM-L6-v2")

        save_embeddings(query, jira, db, model)

    except Exception as e:
        print(traceback.format_exc())
        sys.exit(1)

    finally:
        db.close
