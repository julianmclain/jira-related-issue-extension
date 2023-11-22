from jira import JIRA
from jira.resources import Issue
from jira.client import ResultList

import json
from typing import Dict, List, Any, Self
from dataclasses import dataclass


@dataclass
class SimpleIssue:
    key: str
    summary: str  # basically the title
    description: str
    url: str # TODO
    labels: List[Any]  # TODO
    components: List[str]
    comments: List[str]  # this is only the body of the comment

    @staticmethod
    def from_raw_issue(issue: Dict[str, Any]) -> Self:
        return SimpleIssue(
            issue["key"],
            issue["fields"]["summary"],
            issue["fields"]["description"],
            None,
            None,
            [component["name"] for component in issue["fields"]["components"]],
            [comment["body"] for comment in issue["fields"]["comment"]["comments"]],
        )


# JIRA API config
EXPAND_FIELDS = {
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


def jira_search_paginated(
    jira: JIRA, qs: str, max_results: int = 100, start_at: int = 0
) -> dict[str, Any] | ResultList[Issue]:
    return jira.search_issues(
        qs,
        maxResults=max_results,
        startAt=start_at,
        expand=EXPAND_FIELDS,
    )


def get_issue_field_list(jira: JIRA) -> List[Dict[str, str]]:
    fields = jira.fields()
    simple_field_list = [
        {"key": field["key"], "name": field["name"]} for field in fields
    ]
    return simple_field_list


def get_and_print_issue_field_list(jira) -> None:
    fields = get_issue_field_list(jira)
    print(json.dumps(fields, indent=4))
