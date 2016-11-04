# -*- coding: utf-8 -*-
"""
Update JIRA issue with latest GitHub activity.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

from ....jira.tasks import update_latest_github_activity
from ....lib.jira.decorators import inject_jira
from ...models import GithubEvent


def _find_issues_for_pull_request(jira, pull_request_url):
    """
    Find corresponding JIRA issues for a given GitHub pull request.

    Arguments:
        jira (jira.JIRA): An authenticated JIRA API client session
        pull_request_url (str)

    Returns:
        jira.client.ResultList[jira.Issue]
    """
    jql = 'project=OSPR AND url="{}"'.format(pull_request_url)
    return jira.search_issues(jql)


def _process(jira, event_type, raw_event):
    """
    Update each corresponding JIRA issue with GitHub activity.

    Arguments:
        jira (jira.JIRA): An authenticated JIRA API client session
        event_type (str): GitHub event type
        raw_event (Dict[str, Any]): The parsed event payload
    """
    event = GithubEvent(event_type, raw_event)
    issues = _find_issues_for_pull_request(jira, event.html_url)
    for issue in issues:
        update_latest_github_activity(
            jira,
            issue.id,
            event.description,
            event.user.login,
            event.updated_at,
            event.is_edx_user,
        )


@inject_jira
def run(jira, event_type, raw_event):
    """
    Process the incoming event.

    Arguments:
        jira (jira.JIRA): An authenticated JIRA API client session
        event_type (str): `GitHub event type`_
        raw_event (Dict[str, Any]): The parsed event payload

    .. _GitHub event type:
        https://developer.github.com/v3/activity/events/types/
    """
    event_types = (
        'issue_comment',
        'pull_request',
        'pull_request_review',
        'pull_request_review_comment',
    )
    if event_type in event_types:
        _process(jira, event_type, raw_event)