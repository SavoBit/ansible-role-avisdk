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
- code: 'avi_analyticsprofile controller=10.10.25.42 username=admin '
            ' password=something'
            ' state=present name=sample_analyticsprofile'
description: "Adds/Deletes AnalyticsProfile configuration from Avi Controller."
"""

DOCUMENTATION = '''
---
module: avi_analyticsprofile
author: Gaurav Rastogi (grastogi@avinetworks.com)

short_description: AnalyticsProfile Configuration
description:
    - This module is used to configure AnalyticsProfile object
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
    apdex_response_threshold:
        description:
            - If a client receives an HTTP response in less than the Satisfactory Latency Threshold, the request is considered Satisfied.  If the response time is greater than the Satisfactory Latency Threshold but less than the Tolerated Latency Factor multiplied by the Satisfactory Latency Threshold, it is considered Tolerated.  Greater than this number and the client's request is considered Frustrated.
        default: 500
        type: integer
    apdex_response_tolerated_factor:
        description:
            - Client tolerated response latency factor. Clientmust receive a response within this factor times the satisfactory threshold (apdex_response_threshold) to be considered tolerated
        default: 4
        type: float
    apdex_rtt_threshold:
        description:
            - Satisfactory client to Avi Round Trip Time(RTT).
        default: 250
        type: integer
    apdex_rtt_tolerated_factor:
        description:
            - Tolerated client to Avi Round Trip Time(RTT) factor.  It is a multiple of apdex_rtt_tolerated_factor.
        default: 4
        type: float
    apdex_rum_threshold:
        description:
            - If a client is able to load a page in less than the Satisfactory Latency Threshold, the PageLoad is considered Satisfied.  If the load time is greater than the Satisfied Latency but less than the Tolerated Latency multiplied by Satisifed Latency, it is considered Tolerated.  Greater than this number and the client's request is considered Frustrated.  A PageLoad includes the time for DNS lookup, download of all HTTP objects, and page render time.
        default: 5000
        type: integer
    apdex_rum_tolerated_factor:
        description:
            - Virtual service threshold factor for tolerated Page Load Time (PLT) as multiple of apdex_rum_threshold.
        default: 4
        type: float
    apdex_server_response_threshold:
        description:
            - If Avi receives an HTTP response from a server in less than the Satisfactory Latency Threshold, the server response is considered Satisfied.  If the response time is greater than the Satisfactory Latency Threshold but less than the Tolerated Latency Factor multiplied by the Satisfactory Latency Threshold, it is considered Tolerated.  Greater than this number and the server response is considered Frustrated.
        default: 400
        type: integer
    apdex_server_response_tolerated_factor:
        description:
            - Server tolerated response latency factor. Servermust response within this factor times the satisfactory threshold (apdex_server_response_threshold) to be considered tolerated
        default: 4
        type: float
    apdex_server_rtt_threshold:
        description:
            - Satisfactory client to Avi Round Trip Time(RTT).
        default: 125
        type: integer
    apdex_server_rtt_tolerated_factor:
        description:
            - Tolerated client to Avi Round Trip Time(RTT) factor.  It is a multiple of apdex_rtt_tolerated_factor.
        default: 4
        type: float
    client_log_config:
        description:
            - Not present.
        type: ClientLogConfiguration
    conn_lossy_ooo_threshold:
        description:
            - A connection between client and Avi is considered lossy when more than this percentage of out of order packets are received.
        default: 50
        type: integer
    conn_lossy_timeo_rexmt_threshold:
        description:
            - A connection between client and Avi is considered lossy when more than this percentage of packets are retransmitted due to timeout.
        default: 20
        type: integer
    conn_lossy_total_rexmt_threshold:
        description:
            - A connection between client and Avi is considered lossy when more than this percentage of packets are retransmitted.
        default: 50
        type: integer
    conn_lossy_zero_win_size_event_threshold:
        description:
            - A connection between client and Avi is considered lossy when more than this percentage of times a packet could not be trasmitted due to zero window.
        default: 2
        type: integer
    conn_server_lossy_ooo_threshold:
        description:
            - A connection between Avi and server is considered lossy when more than this percentage of out of order packets are received.
        default: 50
        type: integer
    conn_server_lossy_timeo_rexmt_threshold:
        description:
            - A connection between Avi and server is considered lossy when more than this percentage of packets are retransmitted due to timeout.
        default: 20
        type: integer
    conn_server_lossy_total_rexmt_threshold:
        description:
            - A connection between Avi and server is considered lossy when more than this percentage of packets are retransmitted.
        default: 50
        type: integer
    conn_server_lossy_zero_win_size_event_threshold:
        description:
            - A connection between Avi and server is considered lossy when more than this percentage of times a packet could not be trasmitted due to zero window.
        default: 2
        type: integer
    description:
        description:
            - Not present.
        type: string
    disable_se_analytics:
        description:
            - Disable node (service engine) level analytics forvs metrics
        default: False
        type: bool
    disable_server_analytics:
        description:
            - Disable analytics on backend servers. This may be desired in container environment when there are large number of  ephemeral servers
        default: False
        type: bool
    exclude_client_close_before_request_as_error:
        description:
            - Exclude client closed connection before an HTTP request could be completed from being classified as an error.
        default: False
        type: bool
    exclude_gs_down_as_error:
        description:
            - Exclude 'global service down' from the list of errors.
        default: False
        type: bool
    exclude_http_error_codes:
        description:
            - List of HTTP status codes to be excluded from being classified as an error.  Error connections or responses impacts health score, are included as significant logs, and may be classified as part of a DoS attack.
        type: integer
    exclude_invalid_dns_domain_as_error:
        description:
            - Exclude 'invalid dns domain' from the list of errors.
        default: False
        type: bool
    exclude_invalid_dns_query_as_error:
        description:
            - Exclude 'invalid dns query' from the list of errors.
        default: False
        type: bool
    exclude_no_dns_record_as_error:
        description:
            - Exclude 'no dns record' from the list of errors.
        default: False
        type: bool
    exclude_no_valid_gs_member_as_error:
        description:
            - Exclude 'no valid global service member' from the list of errors.
        default: False
        type: bool
    exclude_persistence_change_as_error:
        description:
            - Exclude persistence server changed while load balancing' from the list of errors.
        default: False
        type: bool
    exclude_server_tcp_reset_as_error:
        description:
            - Exclude server TCP reset from errors.  It is common for applications like MS Exchange.
        default: False
        type: bool
    exclude_syn_retransmit_as_error:
        description:
            - Exclude 'server unanswered syns' from the list of errors.
        default: False
        type: bool
    exclude_tcp_reset_as_error:
        description:
            - Exclude TCP resets by client from the list of potential errors.
        default: False
        type: bool
    hs_event_throttle_window:
        description:
            - Time window (in secs) within which only unique health change events should occur
        default: 1209600
        type: integer
    hs_max_anomaly_penalty:
        description:
            - Maximum penalty that may be deducted from health score for anomalies.
        default: 10
        type: integer
    hs_max_resources_penalty:
        description:
            - Maximum penalty that may be deducted from health score for high resource utilization.
        default: 25
        type: integer
    hs_max_security_penalty:
        description:
            - Maximum penalty that may be deducted from health score based on security assessment.
        default: 100
        type: integer
    hs_min_dos_rate:
        description:
            - DoS connection rate below which the DoS security assessment will not kick in.
        default: 1000
        type: integer
    hs_performance_boost:
        description:
            - Adds free performance score credits to health score. It can be used for compensating health score for known slow applications.
        default: 0
        type: integer
    hs_pscore_traffic_threshold_l4_client:
        description:
            - Threshold number of connections in 5min, below which apdexr, apdexc, rum_apdex, and other network quality metrics are not computed.
        default: 10
        type: float
    hs_pscore_traffic_threshold_l4_server:
        description:
            - Threshold number of connections in 5min, below which apdexr, apdexc, rum_apdex, and other network quality metrics are not computed.
        default: 10
        type: float
    hs_security_certscore_expired:
        description:
            - Score assigned when the certificate has expired
        default: 0
        type: float
    hs_security_certscore_gt30d:
        description:
            - Score assigned when the certificate expires in more than 30 days
        default: 5
        type: float
    hs_security_certscore_le07d:
        description:
            - Score assigned when the certificate expires in less than or equal to 7 days
        default: 2
        type: float
    hs_security_certscore_le30d:
        description:
            - Score assigned when the certificate expires in less than or equal to 30 days
        default: 4
        type: float
    hs_security_chain_invalidity_penalty:
        description:
            - Penalty for allowing certificates with invalid chain.
        default: 1
        type: float
    hs_security_cipherscore_eq000b:
        description:
            - Score assigned when the minimum cipher strength is 0 bits
        default: 0
        type: float
    hs_security_cipherscore_ge128b:
        description:
            - Score assigned when the minimum cipher strength is greater than equal to 128 bits
        default: 5
        type: float
    hs_security_cipherscore_lt128b:
        description:
            - Score assigned when the minimum cipher strength is less than 128 bits
        default: 3.5
        type: float
    hs_security_encalgo_score_none:
        description:
            - Score assigned when no algorithm is used for encryption.
        default: 0
        type: float
    hs_security_encalgo_score_rc4:
        description:
            - Score assigned when RC4 algorithm is used for encryption.
        default: 2.5
        type: float
    hs_security_hsts_penalty:
        description:
            - Penalty for not enabling HSTS.
        default: 1
        type: float
    hs_security_nonpfs_penalty:
        description:
            - Penalty for allowing non-PFS handshakes.
        default: 1
        type: float
    hs_security_selfsignedcert_penalty:
        description:
            - Deprecated
        default: 1
        type: float
    hs_security_ssl30_score:
        description:
            - Score assigned when supporting SSL3.0 encryption protocol
        default: 3.5
        type: float
    hs_security_tls10_score:
        description:
            - Score assigned when supporting TLS1.0 encryption protocol
        default: 5
        type: float
    hs_security_tls11_score:
        description:
            - Score assigned when supporting TLS1.1 encryption protocol
        default: 5
        type: float
    hs_security_tls12_score:
        description:
            - Score assigned when supporting TLS1.2 encryption protocol
        default: 5
        type: float
    hs_security_weak_signature_algo_penalty:
        description:
            - Penalty for allowing weak signature algorithm(s).
        default: 1
        type: float
    name:
        description:
            - The name of the analytics profile.
        required: true
        type: string
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
            - UUID of the analytics profile.
        type: string
'''

RETURN = '''
obj:
    description: AnalyticsProfile (api/analyticsprofile) object
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
                apdex_response_threshold=dict(
                    type='int',
                    ),
                apdex_response_tolerated_factor=dict(
                    type='float',
                    ),
                apdex_rtt_threshold=dict(
                    type='int',
                    ),
                apdex_rtt_tolerated_factor=dict(
                    type='float',
                    ),
                apdex_rum_threshold=dict(
                    type='int',
                    ),
                apdex_rum_tolerated_factor=dict(
                    type='float',
                    ),
                apdex_server_response_threshold=dict(
                    type='int',
                    ),
                apdex_server_response_tolerated_factor=dict(
                    type='float',
                    ),
                apdex_server_rtt_threshold=dict(
                    type='int',
                    ),
                apdex_server_rtt_tolerated_factor=dict(
                    type='float',
                    ),
                client_log_config=dict(
                    type='dict',
                    ),
                conn_lossy_ooo_threshold=dict(
                    type='int',
                    ),
                conn_lossy_timeo_rexmt_threshold=dict(
                    type='int',
                    ),
                conn_lossy_total_rexmt_threshold=dict(
                    type='int',
                    ),
                conn_lossy_zero_win_size_event_threshold=dict(
                    type='int',
                    ),
                conn_server_lossy_ooo_threshold=dict(
                    type='int',
                    ),
                conn_server_lossy_timeo_rexmt_threshold=dict(
                    type='int',
                    ),
                conn_server_lossy_total_rexmt_threshold=dict(
                    type='int',
                    ),
                conn_server_lossy_zero_win_size_event_threshold=dict(
                    type='int',
                    ),
                description=dict(
                    type='str',
                    ),
                disable_se_analytics=dict(
                    type='bool',
                    ),
                disable_server_analytics=dict(
                    type='bool',
                    ),
                exclude_client_close_before_request_as_error=dict(
                    type='bool',
                    ),
                exclude_gs_down_as_error=dict(
                    type='bool',
                    ),
                exclude_http_error_codes=dict(
                    type='list',
                    ),
                exclude_invalid_dns_domain_as_error=dict(
                    type='bool',
                    ),
                exclude_invalid_dns_query_as_error=dict(
                    type='bool',
                    ),
                exclude_no_dns_record_as_error=dict(
                    type='bool',
                    ),
                exclude_no_valid_gs_member_as_error=dict(
                    type='bool',
                    ),
                exclude_persistence_change_as_error=dict(
                    type='bool',
                    ),
                exclude_server_tcp_reset_as_error=dict(
                    type='bool',
                    ),
                exclude_syn_retransmit_as_error=dict(
                    type='bool',
                    ),
                exclude_tcp_reset_as_error=dict(
                    type='bool',
                    ),
                hs_event_throttle_window=dict(
                    type='int',
                    ),
                hs_max_anomaly_penalty=dict(
                    type='int',
                    ),
                hs_max_resources_penalty=dict(
                    type='int',
                    ),
                hs_max_security_penalty=dict(
                    type='int',
                    ),
                hs_min_dos_rate=dict(
                    type='int',
                    ),
                hs_performance_boost=dict(
                    type='int',
                    ),
                hs_pscore_traffic_threshold_l4_client=dict(
                    type='float',
                    ),
                hs_pscore_traffic_threshold_l4_server=dict(
                    type='float',
                    ),
                hs_security_certscore_expired=dict(
                    type='float',
                    ),
                hs_security_certscore_gt30d=dict(
                    type='float',
                    ),
                hs_security_certscore_le07d=dict(
                    type='float',
                    ),
                hs_security_certscore_le30d=dict(
                    type='float',
                    ),
                hs_security_chain_invalidity_penalty=dict(
                    type='float',
                    ),
                hs_security_cipherscore_eq000b=dict(
                    type='float',
                    ),
                hs_security_cipherscore_ge128b=dict(
                    type='float',
                    ),
                hs_security_cipherscore_lt128b=dict(
                    type='float',
                    ),
                hs_security_encalgo_score_none=dict(
                    type='float',
                    ),
                hs_security_encalgo_score_rc4=dict(
                    type='float',
                    ),
                hs_security_hsts_penalty=dict(
                    type='float',
                    ),
                hs_security_nonpfs_penalty=dict(
                    type='float',
                    ),
                hs_security_selfsignedcert_penalty=dict(
                    type='float',
                    ),
                hs_security_ssl30_score=dict(
                    type='float',
                    ),
                hs_security_tls10_score=dict(
                    type='float',
                    ),
                hs_security_tls11_score=dict(
                    type='float',
                    ),
                hs_security_tls12_score=dict(
                    type='float',
                    ),
                hs_security_weak_signature_algo_penalty=dict(
                    type='float',
                    ),
                name=dict(
                    type='str',
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
                    'analyticsprofile', name,
                    tenant=tenant, tenant_uuid=tenant_uuid)
            except ObjectNotFound:
                return module.exit_json(changed=False)
            if rsp.status_code == 204:
                return module.exit_json(changed=True)
            return module.fail_json(msg=rsp.text)
        existing_obj = api.get_object_by_name(
                'analyticsprofile', name,
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
                    'analyticsprofile/%s' % obj_uuid, data=obj,
                    tenant=tenant, tenant_uuid=tenant_uuid)
        else:
            changed = True
            rsp = api.post('analyticsprofile', data=obj,
                           tenant=tenant, tenant_uuid=tenant_uuid)
        if rsp is None:
            return module.exit_json(changed=changed, obj=existing_obj)
        else:
            return ansible_return(module, rsp, changed)
    except:
        raise


if __name__ == '__main__':
    main()