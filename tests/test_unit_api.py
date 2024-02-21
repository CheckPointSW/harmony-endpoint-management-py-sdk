import os
import unittest

from tests.test_unit_global import EndpointTestCase

class TestUnitCloudUses(EndpointTestCase):
    def test_job_off(self):
        self._harmony_endpoint.policy_general_api.get_all_rules_metadata(header_params={ 'x-mgmt-run-as-job': 'off' })

    def test_job_with_payload_on(self):
        self._harmony_endpoint.policy_general_api.get_all_rules_metadata(header_params={ 'x-mgmt-run-as-job': 'on' })

    def test_operation_wo_job(self):
        self._harmony_endpoint.policy_general_api.install_all_policies(header_params={ 'x-mgmt-run-as-job': 'off' })
  
    def test_operation_with_job(self):
        self._harmony_endpoint.policy_general_api.install_all_policies(header_params={ 'x-mgmt-run-as-job': 'on' })

class TestUnitSAASUses(EndpointTestCase):
    def test_operation(self):
        self._harmony_endpoint_saas.self_service_api.public_machines_single_status()

if __name__ == "__main__":
    unittest.main()
