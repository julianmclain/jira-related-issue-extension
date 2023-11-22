import sqlite_vss
from jira import JIRA
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

import sys
import os
import traceback
from jira_ops import SimpleIssue, jira_search_paginated
from database import connect_to_db, create_tables, insert_issue, populate_vss_index


if __name__ == "__main__":
    load_dotenv()

    try:
        db_name = "jira-issue-embeddings.db"
        conn = connect_to_db(db_name)
        sqlite_vss.load(conn)
        print(conn.execute("select vss_version()").fetchone()[0])
        create_tables(conn)

        jira = JIRA(
            server="https://iterable.atlassian.net/",
            basic_auth=(os.getenv("JIRA_USERNAME"), os.getenv("JIRA_API_TOKEN")),
        )

        model = SentenceTransformer("all-MiniLM-L6-v2")

        query = "type = 'On Call Question' and created < -30d"
        total_hits = 0
        last_hits = None

        while last_hits != 0:
            issues = jira_search_paginated(jira, query, 1000, total_hits)

            for issue in issues:
                simple_issue = SimpleIssue.from_raw_issue(issue.raw)
                # issue_string = ". ".join(list(simple_issue.values()))
                issue_string = simple_issue.summary
                embedding = model.encode(issue_string)
                insert_issue(conn, simple_issue, embedding.tobytes())

            hits = len(issues)
            total_hits += hits
            last_hits = hits
            print(f"processed {last_hits} issues...")

        print(f"Done. {total_hits} issues processed")

    except Exception as e:
        print(traceback.format_exc())
        sys.exit(1)

    finally:
        conn.close()
