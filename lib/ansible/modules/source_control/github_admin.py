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
    org:
        required: true
        description:
            - The Github organization you would like to use
        default: null
    parentteam:
        required: false
        description:
            - Optionally define a parent team for 'org_list_teams'
        default: null
    action:
        required: true
        description:
            - Action to perform
        choices: [ 'org_list_users', 'org_list_teams' ]


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
    parentteam: testparent
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
            parentteam=dict(),
            action=dict(
                required=True, choices=['org_list_users','org_list_teams']),
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
    parentteam = module.params['parentteam']

    # define headers for beta features
    headers = 'application/vnd.github.hellcat-preview+json'

    # login to github
    try:
        if user and password:
            gh_obj = github3.login(user, password=password)
        elif login_token:
            gh_obj = github3.login(token=login_token)

        # test if we're actually logged in
        gh_obj.me()

        # Set headers for beta features
        gh_obj.session.headers['Accept'] = headers

    except github3.AuthenticationFailed as e:
        module.fail_json(msg='Failed to connect to GitHub: %s' % to_native(e),
                         details="Please check username and password or token " )

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
                tobj = org.team(t.id)
                
                # Uncomment the below if you want to see the full JSON
                #print(tobj.as_json())

                parentobj = tobj.parent
                parent = None
                if parentobj is not None:
                    parent = parentobj.get('slug')
                if (parentteam and parent == parentteam) or not parentteam:
                    members_count = tobj.members_count
                    print(t.name, " - ", t.description, " (", t.id, ")", " ", members_count, " members - Parent Team: ", parent)
                    #members = t.members()
                    #if members is not "[]":
                    #    for m in members:
                    #        print("  - ", m)


if __name__ == '__main__':
    main()
