

from chkp_harmony_endpoint_management_sdk.classes.harmony_endpoint_saas_options import HarmonyEndpointSaaSOptions
from chkp_harmony_endpoint_management_sdk.classes.infinity_portal_auth import InfinityPortalAuth
from chkp_harmony_endpoint_management_sdk.classes.internal import SessionOperations
from chkp_harmony_endpoint_management_sdk.core.session_manager import SessionManager
from chkp_harmony_endpoint_management_sdk.generated.cloud import HarmonyEndpointBase as HarmonyEndpointCloudBase
from chkp_harmony_endpoint_management_sdk.generated.saas import HarmonyEndpointBase as HarmonyEndpointSaaSBase

# from chkp_harmony_endpoint_management_sdk.classes.on_premise_portal_auth import OnPremisePortalAuth
# from chkp_harmony_endpoint_management_sdk.generated.premise import HarmonyEndpointBase as HarmonyEndpointPremiseBase

print_ea_message = True


class HarmonyEndpoint(HarmonyEndpointCloudBase):

    def __init__(self):
        super().__init__('HarmonyEndpoint', SessionManager())

    def connect(self, infinity_portal_auth: InfinityPortalAuth):
        def keep_alive():
            return self._session_api.keep_alive()

        def login():
            return self._session_api.login_cloud()

        def job_status(job_id):
            return self.jobs_api.get_job_by_id(path_params={'jobId': job_id})

        session_operations = SessionOperations(keep_alive_operation=keep_alive, login_operation=login, job_status_operation=job_status)
        self._session_manager.connect_cloud(infinity_portal_auth, session_operations)

# TODO: Open when on-premise will be release to public
# class HarmonyEndpointPremise(HarmonyEndpointPremiseBase):

#     def __init__(self):
#         super().__init__('HarmonyEndpointPremise', SessionManager())

#     def connect(self, on_premise_portal_auth: OnPremisePortalAuth):
#         def keep_alive():
#             return self._session_api.keep_alive()
#         def login():
#             return self._session_api.login_premise(body={"username": on_premise_portal_auth.username, "password": on_premise_portal_auth.password})
#         def job_status(job_id):
#             return self.jobs_api.get_job_by_id(path_params={ 'jobId': job_id })
#         session_operations = SessionOperations(keep_alive_operation=keep_alive, login_operation=login, job_status_operation=job_status)
#         self._session_manager.connect_premise(on_premise_portal_auth, session_operations)


class HarmonyEndpointSaaS(HarmonyEndpointSaaSBase):

    def __init__(self):
        super().__init__('HarmonyEndpointSaaS', SessionManager())

    def connect(self, infinity_portal_auth: InfinityPortalAuth, harmony_endpoint_saas_options: HarmonyEndpointSaaSOptions):
        def keep_alive():
            return self._manage_session_api.public_mssp_keep_alive()

        def login():
            return self._manage_session_api.public_mssp_login()
        session_operations = SessionOperations(keep_alive_operation=keep_alive, login_operation=login, job_status_operation=None)
        self._session_manager.connect_saas(infinity_portal_auth, harmony_endpoint_saas_options, session_operations)
