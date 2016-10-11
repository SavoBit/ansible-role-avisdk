#!/usr/bin/python
#
# Created on Aug 25, 2016
# @author: Gaurav Rastogi (grastogi@avinetworks.com)
#          Eric Anderson (eanderson@avinetworks.com)
# module_check: not supported
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

from ansible.module_utils.basic import AnsibleModule
from copy import deepcopy
from avi.sdk.avi_api import ApiSession, ObjectNotFound
from avi.sdk.utils.ansible_utils import (ansible_return, purge_optional_fields,
    avi_obj_cmp, cleanup_absent_fields)

EXAMPLES = """
- code: 'avi_logcontrollermapping controller=10.10.25.42 username=admin '
            ' password=something'
            ' state=present name=sample_logcontrollermapping'
description: "Adds/Deletes LogControllerMapping configuration from Avi Controller."
"""

DOCUMENTATION = '''
---
module: avi_logcontrollermapping
author: Gaurav Rastogi (grastogi@avinetworks.com)

short_description: LogControllerMapping Configuration
description:
    - This module is used to configure LogControllerMapping object
    - more examples at <https://github.com/avinetworks/avi-ansible-samples>
requirements: [ avisdk ]
version_added: 2.1.2
options:
    controller:
        description:
            - location of the controller
        required: true
    username:
        description:
            - username to access the Avi
        required: true
    password:
        description:
            - password of the Avi user
        required: true
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
    controller_ip:
        description:
            - Not present.
        type: string
    metrics_mgr_port:
        description:
            - Not present.
        default: 5009
        type: string
    node_uuid:
        description:
            - Not present.
        type: string
    prev_controller_ip:
        description:
            - Not present.
        type: string
    prev_metrics_mgr_port:
        description:
            - Not present.
        default: 5009
        type: string
    static_mapping:
        description:
            - Not present.
        default: False
        type: bool
    tenant_ref:
        description:
            - Not present. object ref Tenant.
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
    vs_uuid:
        description:
            - Not present.
        required: true
        type: string
'''

RETURN = '''
obj:
    description: LogControllerMapping (api/logcontrollermapping) object
    returned: success, changed
    type: dict
'''


def main():
    try:
        module = AnsibleModule(
            argument_spec=dict(
                controller=dict(required=True),
                username=dict(required=True),
                password=dict(required=True),
                tenant=dict(default='admin'),
                tenant_uuid=dict(default=''),
                state=dict(default='present',
                           choices=['absent', 'present']),
                controller_ip=dict(
                    type='str',
                    ),
                metrics_mgr_port=dict(
                    type='str',
                    ),
                node_uuid=dict(
                    type='str',
                    ),
                prev_controller_ip=dict(
                    type='str',
                    ),
                prev_metrics_mgr_port=dict(
                    type='str',
                    ),
                static_mapping=dict(
                    type='bool',
                    ),
                tenant_ref=dict(
                    type='str',
                    ),
                url=dict(
                    type='str',
                    ),
                uuid=dict(
                    type='str',
                    ),
                vs_uuid=dict(
                    type='str',
                    ),
                ),
        )
        api = ApiSession.get_session(
                module.params['controller'],
                module.params['username'],
                module.params['password'],
                tenant=module.params['tenant'])

        state = module.params['state']
        name = module.params['name']
        sensitive_fields = set([])

        obj = deepcopy(module.params)
        obj.pop('state', None)
        obj.pop('controller', None)
        obj.pop('username', None)
        obj.pop('password', None)
        tenant = obj.pop('tenant', '')
        tenant_uuid = obj.pop('tenant_uuid', '')
        obj.pop('cloud_ref', None)

        purge_optional_fields(obj, module)

        if state == 'absent':
            try:
                rsp = api.delete_by_name(
                    'logcontrollermapping', name,
                    tenant=tenant, tenant_uuid=tenant_uuid)
            except ObjectNotFound:
                return module.exit_json(changed=False)
            if rsp.status_code == 204:
                return module.exit_json(changed=True)
            return module.fail_json(msg=rsp.text)
        existing_obj = api.get_object_by_name(
                'logcontrollermapping', name,
                tenant=tenant, tenant_uuid=tenant_uuid,
                params={'include_refs': '', 'include_name': ''})
        changed = False
        rsp = None
        if existing_obj:
            # this is case of modify as object exists. should find out
            # if changed is true or not
            changed = not avi_obj_cmp(obj, existing_obj, sensitive_fields)
            cleanup_absent_fields(obj)
            if changed:
                obj_uuid = existing_obj['uuid']
                rsp = api.put(
                    'logcontrollermapping/%s' % obj_uuid, data=obj,
                    tenant=tenant, tenant_uuid=tenant_uuid)
        else:
            changed = True
            rsp = api.post('logcontrollermapping', data=obj,
                           tenant=tenant, tenant_uuid=tenant_uuid)
        if rsp is None:
            return module.exit_json(changed=changed, obj=existing_obj)
        else:
            return ansible_return(module, rsp, changed)
    except:
        raise


if __name__ == '__main__':
    main()