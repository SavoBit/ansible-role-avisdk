#!/usr/bin/python
#
# Created on Aug 25, 2016
# @author: Gaurav Rastogi (grastogi@avinetworks.com)
#          Eric Anderson (eanderson@avinetworks.com)
# module_check: supported
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

ANSIBLE_METADATA = {'metadata_version': '1.0',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: avi_wafpolicy
author: Gaurav Rastogi (grastogi@avinetworks.com)

short_description: Module for setup of WafPolicy Avi RESTful Object
description:
    - This module is used to configure WafPolicy object
    - more examples at U(https://github.com/avinetworks/devops)
requirements: [ avisdk ]
version_added: "2.4"
options:
    state:
        description:
            - The state that should be applied on the entity.
        default: present
        choices: ["absent","present"]
    crs_groups:
        description:
            - Waf rules are categorized in to groups based on their characterization.
            - These groups are system created with crs groups.
            - Field introduced in 17.2.1.
    description:
        description:
            - Field introduced in 17.2.1.
    mode:
        description:
            - Waf policy mode.
            - This can be detection only or enforcement.
            - Enum options - WAF_MODE_DETECTION_ONLY, WAF_MODE_ENFORCEMENT.
            - Field introduced in 17.2.1.
            - Default value when not specified in API or module is interpreted by Avi Controller as WAF_MODE_DETECTION_ONLY.
    name:
        description:
            - Field introduced in 17.2.1.
        required: true
    paranoia_level:
        description:
            - Waf ruleset paranoia  mode.
            - This is used to select rules based on the paranoia-level tag.
            - Enum options - WAF_PARANOIA_LEVEL_LOW, WAF_PARANOIA_LEVEL_MEDIUM, WAF_PARANOIA_LEVEL_HIGH, WAF_PARANOIA_LEVEL_EXTREME.
            - Field introduced in 17.2.1.
            - Default value when not specified in API or module is interpreted by Avi Controller as WAF_PARANOIA_LEVEL_LOW.
    post_crs_groups:
        description:
            - Waf rules are categorized in to groups based on their characterization.
            - These groups are created by the user and will be enforced after the crs groups.
            - Field introduced in 17.2.1.
    pre_crs_groups:
        description:
            - Waf rules are categorized in to groups based on their characterization.
            - These groups are created by the user and will be  enforced before the crs groups.
            - Field introduced in 17.2.1.
    tenant_ref:
        description:
            - It is a reference to an object of type tenant.
            - Field introduced in 17.2.1.
    url:
        description:
            - Avi controller URL of the object.
    uuid:
        description:
            - Field introduced in 17.2.1.
    waf_profile_ref:
        description:
            - Waf profile for waf policy.
            - It is a reference to an object of type wafprofile.
            - Field introduced in 17.2.1.
extends_documentation_fragment:
    - avi
'''

EXAMPLES = """
- name: Example to create WafPolicy object
  avi_wafpolicy:
    controller: 10.10.25.42
    username: admin
    password: something
    state: present
    name: sample_wafpolicy
"""

RETURN = '''
obj:
    description: WafPolicy (api/wafpolicy) object
    returned: success, changed
    type: dict
'''

from ansible.module_utils.basic import AnsibleModule
try:
    from avi.sdk.utils.ansible_utils import avi_common_argument_spec
    from pkg_resources import parse_version
    import avi.sdk
    sdk_version = getattr(avi.sdk, '__version__', None)
    if ((sdk_version is None) or (sdk_version and
            (parse_version(sdk_version) < parse_version('17.1')))):
        # It allows the __version__ to be '' as that value is used in development builds
        raise ImportError
    from avi.sdk.utils.ansible_utils import avi_ansible_api
    HAS_AVI = True
except ImportError:
    HAS_AVI = False


def main():
    argument_specs = dict(
        state=dict(default='present',
                   choices=['absent', 'present']),
        crs_groups=dict(type='list',),
        description=dict(type='str',),
        mode=dict(type='str',),
        name=dict(type='str', required=True),
        paranoia_level=dict(type='str',),
        post_crs_groups=dict(type='list',),
        pre_crs_groups=dict(type='list',),
        tenant_ref=dict(type='str',),
        url=dict(type='str',),
        uuid=dict(type='str',),
        waf_profile_ref=dict(type='str',),
    )
    argument_specs.update(avi_common_argument_spec())
    module = AnsibleModule(
        argument_spec=argument_specs, supports_check_mode=True)
    if not HAS_AVI:
        return module.fail_json(msg=(
            'Avi python API SDK (avisdk>=17.1) is not installed. '
            'For more details visit https://github.com/avinetworks/sdk.'))
    return avi_ansible_api(module, 'wafpolicy',
                           set([]))

if __name__ == '__main__':
    main()
