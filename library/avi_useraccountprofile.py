#!/usr/bin/python
#
# Created on Aug 25, 2016
# @author: Gaurav Rastogi (grastogi@avinetworks.com)
#          Eric Anderson (eanderson@avinetworks.com)
# module_check: not supported
# Avi Version: 16.3
#
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.
#

import os
# Comment: import * is to make the modules work in ansible 2.0 environments
# from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.basic import *
from avi.sdk.utils.ansible_utils import (ansible_return, purge_optional_fields,
    avi_obj_cmp, cleanup_absent_fields, avi_ansible_api)

EXAMPLES = """
- code: 'avi_useraccountprofile controller=10.10.25.42 username=admin '
            ' password=something'
            ' state=present name=sample_useraccountprofile'
description: "Adds/Deletes UserAccountProfile configuration from Avi Controller."
"""

DOCUMENTATION = '''
---
module: avi_useraccountprofile
author: Gaurav Rastogi (grastogi@avinetworks.com)

short_description: UserAccountProfile Configuration
description:
    - This module is used to configure UserAccountProfile object
    - more examples at <https://github.com/avinetworks/avi-ansible-samples>
requirements: [ avisdk ]
version_added: 2.3
options:
    controller:
        description:
            - location of the controller. Environment variable AVI_CONTROLLER is default
    username:
        description:
            - username to access the Avi. Environment variable AVI_USERNAME is default
    password:
        description:
            - password of the Avi user. Environment variable AVI_PASSWORD is default
    tenant:
        description:
            - tenant for the operations
        default: admin
    tenant_uuid:
        description:
            - tenant uuid for the operations
        default: ''
    state:
        description:
            - The state that should be applied on the entity.
        required: false
        default: present
        choices: ["absent","present"]
    account_lock_timeout:
        description:
            - Lock timeout period (in minutes). Default is 30 minutes.
        default: 30
        type: integer
    credentials_timeout_threshold:
        description:
            - The time period after which credentials expire. Default is 180 days.
        default: 180
        type: integer
    max_concurrent_sessions:
        description:
            - Maximum number of concurrent sessions allowed. There are unlimited sessions by default.
        default: 0
        type: integer
    max_login_failure_count:
        description:
            - Number of login attempts before lockout. Default is 3 attempts.
        default: 3
        type: integer
    max_password_history_count:
        description:
            - Maximum number of passwords to be maintained in the password history. Default is 4 passwords.
        default: 4
        type: integer
    name:
        description:
            - Not present.
        required: true
        type: string
    url:
        description:
            - url
        required: true
        type: string
    uuid:
        description:
            - Not present.
        type: string
'''

RETURN = '''
obj:
    description: UserAccountProfile (api/useraccountprofile) object
    returned: success, changed
    type: dict
'''

def main():
    try:
        module = AnsibleModule(
            argument_spec=dict(
                controller=dict(default=os.environ.get('AVI_CONTROLLER', '')),
                username=dict(default=os.environ.get('AVI_USERNAME', '')),
                password=dict(default=os.environ.get('AVI_PASSWORD', '')),
                tenant=dict(default='admin'),
                tenant_uuid=dict(default=''),
                state=dict(default='present',
                           choices=['absent', 'present']),
                account_lock_timeout=dict(
                    type='int',
                    ),
                credentials_timeout_threshold=dict(
                    type='int',
                    ),
                max_concurrent_sessions=dict(
                    type='int',
                    ),
                max_login_failure_count=dict(
                    type='int',
                    ),
                max_password_history_count=dict(
                    type='int',
                    ),
                name=dict(
                    type='str',
                    ),
                url=dict(
                    type='str',
                    ),
                uuid=dict(
                    type='str',
                    ),
                ),
        )
        return avi_ansible_api(module, 'useraccountprofile',
                               set([]))
    except:
        raise


if __name__ == '__main__':
    main()