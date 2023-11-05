"""
reference
- https://www.youtube.com/watch?v=QdDoFfkVkcw
- https://colab.research.google.com/drive/1UP5ttpgtiRzLcr_3x4Q5rIcIwyPBNUJp#scrollTo=dIQJliStfDlJ
- https://github.com/huggingface/transformers
- https://www.sbert.net/
"""
import os

from jira import JIRA
from dotenv import load_dotenv


load_dotenv()

# Init Jira connection
JIRA_HOST = "https://iterable.atlassian.net/"
jira = JIRA(
    server=JIRA_HOST,
    basic_auth=(os.getenv("JIRA_USERNAME"), os.getenv("JIRA_API_TOKEN")),
)

print(issue = jira.issue("PRO-9392"))
"""
Traceback (most recent call last):
  File "/Users/julian.mclain/code/jira-related-issue-extension/build_dataset.py", line 17, in <module>
    print(issue = jira.issue("PRO-9392"))
  File "/Users/julian.mclain/.pyenv/versions/3.10.4/lib/python3.10/site-packages/jira/client.py", line 1467, in issue
    issue.find(id, params=params)
  File "/Users/julian.mclain/.pyenv/versions/3.10.4/lib/python3.10/site-packages/jira/resources.py", line 259, in find
    self._find_by_url(url, params)
  File "/Users/julian.mclain/.pyenv/versions/3.10.4/lib/python3.10/site-packages/jira/resources.py", line 275, in _find_by_url
    self._load(url, params=params)
  File "/Users/julian.mclain/.pyenv/versions/3.10.4/lib/python3.10/site-packages/jira/resources.py", line 447, in _load
    r = self._session.get(url, headers=headers, params=params)
  File "/Users/julian.mclain/.pyenv/versions/3.10.4/lib/python3.10/site-packages/requests/sessions.py", line 600, in get
    return self.request("GET", url, **kwargs)
  File "/Users/julian.mclain/.pyenv/versions/3.10.4/lib/python3.10/site-packages/jira/resilientsession.py", line 246, in request
    elif raise_on_error(response, **processed_kwargs):
  File "/Users/julian.mclain/.pyenv/versions/3.10.4/lib/python3.10/site-packages/jira/resilientsession.py", line 71, in raise_on_error
    raise JIRAError(
jira.exceptions.JIRAError: JiraError HTTP 404 url: https://iterable.atlassian.net/rest/api/2/issue/PRO-9392
	text: Issue does not exist or you do not have permission to see it.

	response headers = {'Date': 'Sat, 04 Nov 2023 23:47:30 GMT', 'Content-Type': 'application/json;charset=UTF-8', 'Server': 'AtlassianEdge', 'Timing-Allow-Origin': '*', 'X-Arequestid': '57555a2c47c6c0d628e597051cf5b605', 'X-Seraph-Loginreason': 'AUTHENTICATED_FAILED', 'Cache-Control': 'no-cache, no-store, no-transform', 'Content-Encoding': 'gzip', 'X-Content-Type-Options': 'nosniff', 'X-Xss-Protection': '1; mode=block', 'Atl-Traceid': 'bb16510412764eac965232b2ee3529e2', 'Report-To': '{"endpoints": [{"url": "https://dz8aopenkvv6s.cloudfront.net"}], "group": "endpoint-1", "include_subdomains": true, "max_age": 600}', 'Nel': '{"failure_fraction": 0.001, "include_subdomains": true, "max_age": 600, "report_to": "endpoint-1"}', 'Strict-Transport-Security': 'max-age=63072000; includeSubDomains; preload', 'Transfer-Encoding': 'chunked'}
	response text = {"errorMessages":["Issue does not exist or you do not have permission to see it."],"errors":{}}
"""
