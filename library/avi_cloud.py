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
- code: 'avi_cloud controller=10.10.25.42 username=admin '
            ' password=something'
            ' state=present name=sample_cloud'
description: "Adds/Deletes Cloud configuration from Avi Controller."
"""

DOCUMENTATION = '''
---
module: avi_cloud
author: Gaurav Rastogi (grastogi@avinetworks.com)

short_description: Cloud Configuration
description:
    - This module is used to configure Cloud object
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
    apic_configuration:
        description:
            - Not present.
        type: APICConfiguration
    apic_mode:
        description:
            - Not present.
        default: False
        type: bool
    aws_configuration:
        description:
            - Not present.
        type: AwsConfiguration
    cloudstack_configuration:
        description:
            - Not present.
        type: CloudStackConfiguration
    dhcp_enabled:
        description:
            - Select the IP address management scheme
        default: False
        type: bool
    dns_provider_ref:
        description:
            - DNS Provider for the cloud object ref IpamDnsProviderProfile.
        type: string
    docker_configuration:
        description:
            - Not present.
        type: DockerConfiguration
    east_west_dns_provider_ref:
        description:
            - DNS Profile for East-West applications object ref IpamDnsProviderProfile.
        type: string
    east_west_ipam_provider_ref:
        description:
            - Ipam Profile for East-West applications object ref IpamDnsProviderProfile.
        type: string
    enable_vip_static_routes:
        description:
            - Use static routes for VIP side network resolution during VirtualService placement.
        default: False
        type: bool
    ipam_provider_ref:
        description:
            - Ipam Provider for the cloud object ref IpamDnsProviderProfile.
        type: string
    license_type:
        description:
            - If no license type is specified then default license enforcement for the cloud type is chosen. The default mappings are Container Cloud is Max Ses, OpenStack and VMware is cores and linux it is Sockets.
        type: string
    linuxserver_configuration:
        description:
            - Not present.
        type: LinuxServerConfiguration
    mesos_configuration:
        description:
            - Not present.
        type: MesosConfiguration
    mtu:
        description:
            - MTU setting for the cloud
        default: 1500
        type: integer
    name:
        description:
            - Not present.
        required: true
        type: string
    obj_name_prefix:
        description:
            - Default prefix for all automatically created objects in this cloud. This prefix can be overridden by the SE-Group template. 
        type: string
    openstack_configuration:
        description:
            - Not present.
        type: OpenStackConfiguration
    oshiftk8s_configuration:
        description:
            - Not present.
        type: OShiftK8SConfiguration
    prefer_static_routes:
        description:
            - Prefer static routes over interface routes during VirtualService placement.
        default: False
        type: bool
    proxy_configuration:
        description:
            - Not present.
        type: ProxyConfiguration
    rancher_configuration:
        description:
            - Not present.
        type: RancherConfiguration
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
    vca_configuration:
        description:
            - Not present.
        type: vCloudAirConfiguration
    vcenter_configuration:
        description:
            - Not present.
        type: vCenterConfiguration
    vtype:
        description:
            - Cloud type
        required: true
        type: string
'''

RETURN = '''
obj:
    description: Cloud (api/cloud) object
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
                apic_configuration=dict(
                    type='dict',
                    ),
                apic_mode=dict(
                    type='bool',
                    ),
                aws_configuration=dict(
                    type='dict',
                    ),
                cloudstack_configuration=dict(
                    type='dict',
                    ),
                dhcp_enabled=dict(
                    type='bool',
                    ),
                dns_provider_ref=dict(
                    type='str',
                    ),
                docker_configuration=dict(
                    type='dict',
                    ),
                east_west_dns_provider_ref=dict(
                    type='str',
                    ),
                east_west_ipam_provider_ref=dict(
                    type='str',
                    ),
                enable_vip_static_routes=dict(
                    type='bool',
                    ),
                ipam_provider_ref=dict(
                    type='str',
                    ),
                license_type=dict(
                    type='str',
                    ),
                linuxserver_configuration=dict(
                    type='dict',
                    ),
                mesos_configuration=dict(
                    type='dict',
                    ),
                mtu=dict(
                    type='int',
                    ),
                name=dict(
                    type='str',
                    ),
                obj_name_prefix=dict(
                    type='str',
                    ),
                openstack_configuration=dict(
                    type='dict',
                    ),
                oshiftk8s_configuration=dict(
                    type='dict',
                    ),
                prefer_static_routes=dict(
                    type='bool',
                    ),
                proxy_configuration=dict(
                    type='dict',
                    ),
                rancher_configuration=dict(
                    type='dict',
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
                vca_configuration=dict(
                    type='dict',
                    ),
                vcenter_configuration=dict(
                    type='dict',
                    ),
                vtype=dict(
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
                    'cloud', name,
                    tenant=tenant, tenant_uuid=tenant_uuid)
            except ObjectNotFound:
                return module.exit_json(changed=False)
            if rsp.status_code == 204:
                return module.exit_json(changed=True)
            return module.fail_json(msg=rsp.text)
        existing_obj = api.get_object_by_name(
                'cloud', name,
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
                    'cloud/%s' % obj_uuid, data=obj,
                    tenant=tenant, tenant_uuid=tenant_uuid)
        else:
            changed = True
            rsp = api.post('cloud', data=obj,
                           tenant=tenant, tenant_uuid=tenant_uuid)
        if rsp is None:
            return module.exit_json(changed=changed, obj=existing_obj)
        else:
            return ansible_return(module, rsp, changed)
    except:
        raise


if __name__ == '__main__':
    main()