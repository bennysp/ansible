#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright: Ansible Team
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


ANSIBLE_METADATA = {'metadata_version': '1.0',
                    'status': ['preview'],
                    'supported_by': 'community'}


DOCUMENTATION = '''
---
module: github_admin
short_description: Interact with GitHub Admin functions
description:
    - Functions to help interact with admin functionality
version_added: 2.2
options:
    token:
        description:
            - GitHub Personal Access Token for authenticating
        default: null
    user:
        required: true
        description:
            - The GitHub account that owns the repository
        default: null
    password:
        description:
            - The GitHub account password for the user
        default: null
        version_added: "2.4"
    action:
        required: true
        description:
            - Action to perform
        choices: [ 'org_list_users' ]


author:
    - "Adrian Moisey (@adrianmoisey)"
requirements:
    - "github3.py >= 1.0.0a3"
'''

EXAMPLES = '''
- name: Get list of users from github organization
  github_admin:
    token: tokenabc1234567890
    user: testuser
    org: testcompany
    action: org_list_users


'''

RETURN = '''
github_admin:
    description: List of users in the organization
    type: string
    returned: success
    sample: 1.1.0
'''

try:
    import github3

    HAS_GITHUB_API = True
except ImportError:
    HAS_GITHUB_API = False

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils._text import to_native


def main():
    module = AnsibleModule(
        argument_spec=dict(
            user=dict(required=True),
            password=dict(no_log=True),
            token=dict(no_log=True),
            org=dict(required=True),
            action=dict(
                required=True, choices=['org_list_users']),
        ),
        supports_check_mode=True,
        required_one_of=(('password', 'token'),),
        mutually_exclusive=(('password', 'token'),),
    )

    if not HAS_GITHUB_API:
        module.fail_json(msg='Missing required github3 module (check docs or '
                             'install with: pip install github3.py==1.0.0a4)')

    user = module.params['user']
    password = module.params['password']
    login_token = module.params['token']
    action = module.params['action']
    organization = module.params['org']

    # login to github
    try:
        if user and password:
            gh_obj = github3.login(user, password=password)
        elif login_token:
            gh_obj = github3.login(token=login_token)

        # test if we're actually logged in
        gh_obj.me()
    except github3.AuthenticationFailed as e:
        module.fail_json(msg='Failed to connect to GitHub: %s' % to_native(e),
                         details="Please check username and password or token "
                                 "for repository %s" % repo)

    org = gh_obj.organization(organization)

    if action == 'org_list_users':
        members = org.members()
        if members is not "[]":
            for m in members:
                print(m)
    
    if action == 'org_list_teams':
        teams = org.teams()
        if teams is not "[]":
            for t in teams:
                print(t.name)


if __name__ == '__main__':
    main()
