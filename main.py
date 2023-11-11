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
"""
import sqlite3
import sqlite_vss
from jira import JIRA
from jira.resources import Issue
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer, util
from sentence_transformers.util import cos_sim

import os


load_dotenv()

JIRA_HOST = "https://iterable.atlassian.net/"
jira = JIRA(
    server=JIRA_HOST,
    basic_auth=(os.getenv("JIRA_USERNAME"), os.getenv("JIRA_API_TOKEN")),
)

# JIRA settings
children = True #@param {type:"boolean"}
ancestors = True #@param {type:"boolean"}
issuetypes = True #@param {type:"boolean"}
names = True #@param {type: "boolean"}
changelog = False #@param {type:"boolean"}
renderedFields = False #@param {type:"boolean"}
operations = False #@param {type:"boolean"}
editmeta = False #@param {type:"boolean"}
versionedRepresentations = False #@param {type:"boolean"}

EXPAND_NAMES = set([
    "issuetypes", "names","ancestors","children","operations",
    "versionedRepresentations","editmeta","changelog","renderedFields"
    ])
API_OPTIONS = ",".join([f for f in EXPAND_NAMES if globals()[f]])
FIELD_MAP = {"_".join(f['name'].lower().split()): f['key'] for f in jira.fields() }
FIELDS = [
    'key',
    'summary',
    'issuetype',
    'components',
    'created',
    'resolved',
    'description',
    'labels',
    'priority',
    'comment'
    ]
FIELD_LIST = sorted([FIELD_MAP.get(f,f) for f in FIELDS])


def query_jira(qs: str, max_results: int = 1, start_at: int = 0):
    return jira.search_issues(qs, maxResults=max_results, startAt=start_at, expand=API_OPTIONS,
                            fields=FIELD_LIST)


def create_issue_summary(issue: Issue, include_comments=True):
    raw_issue = issue.raw
    fields = raw_issue['fields']
    summary_items = [raw_issue['key']]
    summary_items.append ((fields['summary'] or ""))
    summary_items.append ((fields['description'] or ""))
    summary_items += fields['labels']
    summary_items += [f['name'] for f in fields['components']]
    if include_comments:
        summary_items += [f['body'] for f in fields['comment']['comments']]

    return ". ".join(summary_items)




if __name__ == "__main__":
    # issues = jira.search_issues("type = 'On Call Question' and created > -180d and created < -30d", 10, 0)
    # issue_summaries = [create_issue_summary(i) for i in issues]

    # model = SentenceTransformer('all-MiniLM-L6-v2')
    # embeddings = model.encode(issue_summaries)
    # for sentence, embedding in zip(issue_summaries, embeddings):
    #     print("Sentence:", sentence)
    #     print("Embedding:", embedding)
    #     print("")

    db = sqlite3.connect(':memory:')
    db.enable_load_extension(True)
    sqlite_vss.load(db)

    version, = db.execute('select vss_version()').fetchone()
    print(version)

    # next steps
    # - store tickets in sqlite so you don't need to query every time
    # - test https://github.com/asg017/sqlite-vss/tree/main/bindings/python
