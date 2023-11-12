"""
reference
- https://github.com/huggingface/transformers
- https://www.sbert.net/
- https://jira.readthedocs.io/
- Embeddings tutorial https://www.youtube.com/watch?v=QdDoFfkVkcw
- Pete's notebook https://colab.research.google.com/drive/1UP5ttpgtiRzLcr_3x4Q5rIcIwyPBNUJp#scrollTo=dIQJliStfDlJ
- Vector search with sqlite https://observablehq.com/@asg017/introducing-sqlite-vss
- In order to enable sqlite extensions https://stackoverflow.com/a/60481356
- sqlite-vss tutorial https://observablehq.com/@asg017/introducing-sqlite-vss
- python bindings for sqlite-vss https://github.com/asg017/sqlite-vss/tree/main/bindings/python
"""

import sqlite3
import sqlite_vss
from jira import JIRA
from jira.resources import Issue
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer, util
from sentence_transformers.util import cos_sim

import os
from typing import Dict

load_dotenv()

JIRA_HOST = "https://iterable.atlassian.net/"
jira = JIRA(
    server=JIRA_HOST,
    basic_auth=(os.getenv("JIRA_USERNAME"), os.getenv("JIRA_API_TOKEN")),
)

# JIRA settings
children = True  # @param {type:"boolean"}
ancestors = True  # @param {type:"boolean"}
issuetypes = True  # @param {type:"boolean"}
names = True  # @param {type: "boolean"}
changelog = False  # @param {type:"boolean"}
renderedFields = False  # @param {type:"boolean"}
operations = False  # @param {type:"boolean"}
editmeta = False  # @param {type:"boolean"}
versionedRepresentations = False  # @param {type:"boolean"}

EXPAND_NAMES = set(
    [
        "issuetypes",
        "names",
        "ancestors",
        "children",
        "operations",
        "versionedRepresentations",
        "editmeta",
        "changelog",
        "renderedFields",
    ]
)
API_OPTIONS = ",".join([f for f in EXPAND_NAMES if globals()[f]])
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


def save_all_jira_issues(db) -> int:
    total_hits = 0
    last_hits = None

    while last_hits != 0:
        issues = query_jira(
            "type = 'On Call Question' and created > -180d and created < -30d",
            10,
            total_hits,
        )
        simple_issues = [create_simple_issue(db, i) for i in issues]
        for si in simple_issues:
            insert_issue(db, si)

        hits = len(issues)
        total_hits += hits
        last_hits = hits
        print(f"processed {last_hits} hits")

    return total_hits


def query_jira(qs: str, max_results: int = 1, start_at: int = 0):
    return jira.search_issues(
        qs,
        maxResults=max_results,
        startAt=start_at,
        expand=API_OPTIONS,
        fields=FIELD_LIST,
    )


def create_simple_issue(db, issue: Issue, include_comments=True):
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


def insert_issue(db, simple_issue: Dict[str, str]):
    summary_string = ". ".join(list(simple_issue.values()))
    db.execute(
        "INSERT INTO issues (key, summary) values (?, ?)",
        (simple_issue["key"], summary_string),
    )
    db.commit()


def create_issue_table(db) -> None:
    db.execute(
        """
            CREATE TABLE IF NOT EXISTS issues(
                key TEXT NOT NULL,
                summary TEXT NOT NULL,
                embedding BLOB
            )
        """
    )


def insert_embeddings(db, model) -> None:
    query = db.execute(
        """
            SELECT * FROM issues WHERE embedding IS NULL
        """
    )
    issues = query.fetchall()
    print(f"got {len(issues)} issues")
    # embeddings = model.encode(issue_summaries)
    # for sentence, embedding in zip(issue_summaries, embeddings):
    #     print("Sentence:", sentence)
    #     print("Embedding:", embedding)
    #     print("")


if __name__ == "__main__":
    db = sqlite3.connect("jira-issue-embeddings.db")
    db.enable_load_extension(True)

    # create_issue_table(db)
    # save_all_jira_issues(db)

    model = SentenceTransformer("all-MiniLM-L6-v2")
    insert_embeddings(db, model)

    sqlite_vss.load(db)
    db.close
