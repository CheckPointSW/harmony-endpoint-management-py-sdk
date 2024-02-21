import os
import unittest

from chkp_harmony_endpoint_management_sdk import HarmonyEndpoint, HarmonyEndpointSaaS, HarmonyEndpointSaaSOptions, InfinityPortalAuth

# Load environment variables from .env if it exists
if os.path.exists('./.env'):
    from dotenv import load_dotenv
    load_dotenv()
    
CI_CLIENT_ID=os.environ.get("CI_CLIENT_ID")
CI_ACCESS_KEY=os.environ.get("CI_ACCESS_KEY")
CI_GATEWAY=os.environ.get("CI_GATEWAY")
infinity_portal_auth = InfinityPortalAuth(access_key=CI_ACCESS_KEY, client_id=CI_CLIENT_ID, gateway=CI_GATEWAY) 



class EndpointTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self._harmony_endpoint = HarmonyEndpoint()
        self._harmony_endpoint.connect(infinity_portal_auth=infinity_portal_auth)
        self._harmony_endpoint_saas = HarmonyEndpointSaaS()
        self._harmony_endpoint_saas.connect(infinity_portal_auth=infinity_portal_auth, harmony_endpoint_saas_options=HarmonyEndpointSaaSOptions(activate_mssp_session=False))

    @classmethod
    def tearDownClass(self):
        self._harmony_endpoint.disconnect()
        self._harmony_endpoint_saas.disconnect()

    
if __name__ == "__main__":
    unittest.main()
