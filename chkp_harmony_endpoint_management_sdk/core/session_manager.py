import json
import threading
import time
from typing import Any
from unitsnet_py import Duration
from chkp_harmony_endpoint_management_sdk.classes import harmony_endpoint_saas_options
from chkp_harmony_endpoint_management_sdk.classes.harmony_endpoint_saas_options import HarmonyEndpointSaaSOptions
from chkp_harmony_endpoint_management_sdk.classes.harmony_api_exception import HarmonyApiException, HarmonyErrorScope
from chkp_harmony_endpoint_management_sdk.classes.on_premise_portal_auth import OnPremisePortalAuth
from chkp_harmony_endpoint_management_sdk.classes.sdk_connection_state import SDKConnectionState
from chkp_harmony_endpoint_management_sdk.classes.infinity_portal_auth import InfinityPortalAuth
from chkp_harmony_endpoint_management_sdk.classes.internal import SessionOperations
from chkp_harmony_endpoint_management_sdk.core.logger import logger, error_logger
from chkp_harmony_endpoint_management_sdk.core.sdk_platform import KEEP_ALIVE_INTERVAL, KEEP_ALIVE_PERFORM_GRACE, MSSP_KEEP_ALIVE_EXPIRATION
from chkp_harmony_endpoint_management_sdk.generated.cloud.api_client import ApiClient as CloudApiClient, Configuration as CloudConfiguration
# from chkp_harmony_endpoint_management_sdk.generated.premise.api_client import ApiClient as PremiseApiClient , Configuration as PremiseConfiguration
from chkp_harmony_endpoint_management_sdk.generated.saas.api_client import ApiClient as SAASApiClient, Configuration as SAASConfiguration
import uuid
from enum import Enum
from urllib.parse import urlparse
import jwt
import requests


class WorkMode(Enum):
    CLOUD = "cloud"
    SAAS = "saas"
    PREMISE = "premise"


CI_APPLICATION_PATH = '/app/endpoint-web-mgmt'
EXTERNAL_API_BASE_PATH = '/harmony/endpoint/api'
CI_AUTH_PATH = '/auth/external'

SOURCE_HEADER = 'harmony-endpoint-py-sdk'

VERIFY_CONTENT = False


class SessionManager:
    def __init__(self):
        self.__session_operations: SessionOperations = None
        self.__infinity_portal_auth: InfinityPortalAuth = None
        self.__infinity_portal_token: str = ''
        self.__endpoint_token: str = ''
        self.__session_id: str = str(uuid.uuid4())
        self.__work_mode: WorkMode = None
        self.__url: str = ''

        self.__harmony_endpoint_saas_options: harmony_endpoint_saas_options = None
        """
        The CI token expiration
        """

        self.__on_premise_portal_auth: OnPremisePortalAuth = None
        """
        The CI token expiration
        """

        self.__next_ci_expiration: Duration = None
        """
        The CI token expiration
        """

        self.__next_endpoint_session_expiration: Duration = None
        """
        The endpoint service token expiration
        """

        self.__next_endpoint_login_expiration: Duration = None
        """
         The endpoint service token uses CI token expiration (endpoint token can be valid as long as CI token is valid, and no more)
        """

        self.__next_mssp_expiration: Duration = None
        """
          The mssp service token expiration
        """

        self.__keep_alive_on_flag: bool = False
        self.__keep_alive_running_flag: bool = False
        self.__sdk_connection_state: SDKConnectionState = SDKConnectionState.DISCONNECTED

    def __get_url(self) -> str:
        if self.__work_mode == WorkMode.PREMISE:
            return f'{self.__url}{EXTERNAL_API_BASE_PATH}'
        if self.__work_mode == WorkMode.SAAS:
            return f'{self.__url}{CI_APPLICATION_PATH}'

        return f'{self.__url}{CI_APPLICATION_PATH}{EXTERNAL_API_BASE_PATH}'

    @property
    def client(self) -> Any:

        if self.__sdk_connection_state == SDKConnectionState.DISCONNECTED:
            error_logger('Unable to process operation call, no session configured, connect first')
            raise HarmonyApiException(error_scope=HarmonyErrorScope.SESSION, message='No session configured, connect first')

        configuration = None

        if self.__work_mode == WorkMode.CLOUD:
            configuration = CloudConfiguration()
        # TODO: Open when on-premise will be release to public
        # if self.__work_mode == WorkMode.PREMISE:
        #     configuration = PremiseConfiguration()
        if self.__work_mode == WorkMode.SAAS:
            configuration = SAASConfiguration()

        session_info = {
            "session_id": self.__session_id,
            "request_id": str(uuid.uuid4()),
            "job_status_operation": self.__session_operations.job_status_operation,
            "do_not_handle_job": False,
            "endpoint_token": self.__endpoint_token,
            "infinity_portal_token": self.__infinity_portal_token,
            "source_header": SOURCE_HEADER,
        }

        configuration.host = self.__get_url()

        if self.__infinity_portal_token:
            configuration.access_token = self.__infinity_portal_token

        if self.__endpoint_token:
            configuration.api_key['apiJwt'] = self.__endpoint_token

        # This is an hack to keep dynamic data in the configuration object
        configuration.api_key['session'] = session_info

        if self.__work_mode == WorkMode.PREMISE and self.__on_premise_portal_auth.disable_tls_chain_validation:
            configuration.assert_hostname = False
            configuration.verify_ssl = False

        if self.__work_mode == WorkMode.CLOUD:
            return CloudApiClient(configuration)
        # TODO: Open when on-premise will be release to public
        # if self.__work_mode == WorkMode.PREMISE:
        #     return PremiseApiClient(configuration)
        if self.__work_mode == WorkMode.SAAS:
            return SAASApiClient(configuration)

    def __perform_endpoint_login(self):
        try:
            logger(f'Preforming endpoint login to session id "{self.__session_id}" ...')
            endpoint_response = self.__session_operations.login_operation()
            logger(f'Preforming endpoint login to session id "{self.__session_id}" done')
            self.__endpoint_token = endpoint_response.http_response.headers.get('x-mgmt-api-token')
            expires_in_sec = endpoint_response.http_response.headers.get('x-mgmt-session-expiry-seconds')
            self.__next_endpoint_session_expiration = Duration.from_seconds(time.time()) + Duration.from_seconds(int(expires_in_sec))
            self.__next_endpoint_login_expiration = self.__next_ci_expiration  # login is valid as long the CI token is valid
        except Exception as e:
            error_logger(f'Failed to login to endpoint for session "{self.__session_id}", error: {e}')
            self.__sdk_connection_state = SDKConnectionState.CONNECTION_ISSUE
            raise e

    def __perform_mssp_login(self):
        try:
            logger(f'Preforming mssp login to session id "{self.__session_id}" ...')
            self.__session_operations.login_operation()
            logger(f'Preforming mssp login to session id "{self.__session_id}" done')
            self.__next_mssp_expiration = Duration.from_seconds(time.time()) + MSSP_KEEP_ALIVE_EXPIRATION
        except Exception as e:
            error_logger(f'Failed to login to mssp for session "{self.__session_id}", error: {e}')
            self.__sdk_connection_state = SDKConnectionState.CONNECTION_ISSUE
            raise e

    def __perform_ci_login(self):
        auth_url = f'{self.__url}{CI_AUTH_PATH}'

        try:
            logger(f'Preforming CI login to session id "{self.__session_id}" with url "${auth_url}"...')
            payload = {
                "clientId": self.__infinity_portal_auth.client_id,
                "accessKey": self.__infinity_portal_auth.access_key
            }
            headers = {
                "Content-Type": "application/json"
            }
            response = requests.post(url=auth_url, data=json.dumps(payload), headers=headers)

            if not 200 <= response.status_code <= 299:
                error_logger(f'Login to CI GW failed with status "{response.status_code}" payload: "{response.text}"')
                raise HarmonyApiException(
                    error_scope=HarmonyErrorScope.SERVICE,
                    payload_error=response.text,
                    url=auth_url,
                    status_code=response.status_code,
                )

            response_json = response.json()

            if not response_json['success']:
                error_logger(f'Failed to login to CI GW for session "{self.__session_id}" url "{auth_url}", error payload: {response_json}')
                raise response_json
            logger(f'Preforming CI login to session id "{self.__session_id}" succeeded')

            self.__infinity_portal_token = response_json['data']['token']
            self.__assert_token_is_for_correct_application(self.__infinity_portal_token)
            self.__next_ci_expiration = Duration.from_seconds(time.time()) + Duration.from_seconds(response_json['data']['expiresIn'])
        except Exception as e:
            error_logger(f'Failed to login to CI GW for session "{self.__session_id}" url "{auth_url}", error: {e}')
            self.__sdk_connection_state = SDKConnectionState.CONNECTION_ISSUE
            raise e

    def __perform_keep_alive(self):
        now = Duration.from_seconds(time.time())
        logger(f'Preforming keep-alive to session id {self.__session_id} ...')

        # CI relevant only when using CI GWs
        require_ci_login = self.__work_mode in [WorkMode.CLOUD, WorkMode.SAAS]
        # Endpoint login relevant only when using endpoint management API, and only on cloud after CI token expired
        require_endpoint_login = self.__work_mode in [WorkMode.CLOUD]
        # Endpoint KA is relevant only when using endpoint management APIs
        require_endpoint_keep_alive = self.__work_mode in [WorkMode.CLOUD, WorkMode.PREMISE]
        # MSSP KA is relevant only when using SAAS on cloud, and consumer choose to activate MSSP session management
        require_mssp_keep_alive = (self.__work_mode in [WorkMode.SAAS]) and self.__harmony_endpoint_saas_options.activate_mssp_session

        try:
            if require_ci_login and (not self.__next_ci_expiration or self.__next_ci_expiration - now < KEEP_ALIVE_PERFORM_GRACE):
                try:
                    logger(f'CI token for session {self.__session_id} is about to expired, about to re-login...')
                    self.__perform_ci_login()
                    logger(f'CI token for session {self.__session_id} re-created successfully')
                except Exception as e:
                    error_logger(f'Failed to re-login to CI for session {self.__session_id}')
                    raise e

            if require_endpoint_login and (
                not self.__next_endpoint_login_expiration
                or self.__next_endpoint_login_expiration - now < KEEP_ALIVE_PERFORM_GRACE
            ):
                try:
                    logger(f'CI token for session {self.__session_id} used by endpoint re-created, about to re-login endpoint...')
                    self.__perform_endpoint_login()
                    logger(f'Token for {self.__session_id} used by endpoint re-created successfully')
                except Exception as e:
                    error_logger(f'Failed to re-login to endpoint by CI token for session {self.__session_id}')
                    raise e

            if require_endpoint_keep_alive and (
                not self.__next_endpoint_session_expiration
                or self.__next_endpoint_session_expiration - now < KEEP_ALIVE_PERFORM_GRACE
            ):
                try:
                    logger(f'Endpoint token for session {self.__session_id} is about to expired, about to send keep-alive..')
                    endpoint_response = self.__session_operations.keep_alive_operation()
                    logger(f'Endpoint token for session {self.__session_id} refreshed successfully')
                    expires_in_sec = endpoint_response.http_response.headers.get('x-mgmt-session-expiry-seconds')
                    self.__next_endpoint_session_expiration = now + Duration.from_seconds(int(expires_in_sec))
                    self.__sdk_connection_state = SDKConnectionState.CONNECTED
                except Exception as e:
                    error_logger(f'Failed to perform endpoint keep-alive for {self.__session_id}')
                    raise e

            if require_mssp_keep_alive and (not self.__next_mssp_expiration or self.__next_mssp_expiration - now < KEEP_ALIVE_PERFORM_GRACE):
                try:
                    logger(f'MSSP token for session {self.__session_id} is about to expired, about to send keep-alive..')
                    logger(f'MSSP token for session {self.__session_id} refreshed successfully')
                    endpoint_response = self.__session_operations.keep_alive_operation()
                    self.__next_mssp_expiration = now + MSSP_KEEP_ALIVE_EXPIRATION
                    self.__sdk_connection_state = SDKConnectionState.CONNECTED
                except Exception as e:
                    error_logger(f'Failed to perform MSSP keep-alive for {self.__session_id}')
                    raise e

        except Exception as e:
            error_logger(f'Failed to perform keep-alive for {self.__session_id} error: {e}')
            self.__sdk_connection_state = SDKConnectionState.CONNECTION_ISSUE
        finally:
            logger(f'Preforming keep-alive to session id {self.__session_id} done')

    def __keep_alive_activation(self):
        while self.__keep_alive_on_flag:
            time.sleep(KEEP_ALIVE_INTERVAL.seconds)
            logger(f'Keep alive for session id {self.__session_id} triggered')
            if self.__keep_alive_running_flag:
                logger(f'Another keep alive for session id {self.__session_id} already triggered, aborting')
                continue
            self.__keep_alive_running_flag = True
            self.__perform_keep_alive()
            self.__keep_alive_running_flag = False
        logger(f'Keep-alive activation  {self.__session_id} already triggered, aborting')

    def __activate_keep_alive(self):
        logger(f'Session id {self.__session_id} is ready, starting keep-alive activation')
        self.__sdk_connection_state = SDKConnectionState.CONNECTED
        self.__keep_alive_on_flag = True
        keep_alive_thread = threading.Thread(target=self.__keep_alive_activation)
        # Start the thread in the background
        keep_alive_thread.daemon = True
        keep_alive_thread.start()

    def __validate_cloud_params(self, infinity_portal_auth: InfinityPortalAuth):
        if not infinity_portal_auth.gateway:
            msg = "Passing gateway is mandatory"
            error_logger(msg)
            raise HarmonyApiException(
                error_scope=HarmonyErrorScope.INVALID_PARAMS,
                message=msg,
            )

        if not infinity_portal_auth.client_id:
            msg = "Passing client_id is mandatory"
            error_logger(msg)
            raise HarmonyApiException(
                error_scope=HarmonyErrorScope.INVALID_PARAMS,
                message=msg,
            )

        if not infinity_portal_auth.access_key:
            msg = "Passing access_key is mandatory"
            error_logger(msg)
            raise HarmonyApiException(
                error_scope=HarmonyErrorScope.INVALID_PARAMS,
                message=msg,
            )

        try:
            parsed_url = urlparse(infinity_portal_auth.gateway)
            if parsed_url.scheme != "https":
                message = f"Gateway provided {infinity_portal_auth.gateway} is not using https protocol"
                error_logger(message)
                raise HarmonyApiException(
                    message=message,
                    error_scope=HarmonyErrorScope.INVALID_PARAMS,
                )

            # In any case of providing extra path (e.g., extra / in the end, etc.), take only the protocol + domain from URL.
            infinity_portal_auth.gateway = f"{parsed_url.scheme}://{parsed_url.netloc}"
            return
        except Exception as error:
            message = f"Gateway provided '{infinity_portal_auth.gateway}' is not a valid URL  '{error}'"
            error_logger(message)
            raise HarmonyApiException(
                message=message,
                error_scope=HarmonyErrorScope.INVALID_PARAMS,
            )

    def __validate_premise_params(self, on_premise_portal_auth: OnPremisePortalAuth):
        if not on_premise_portal_auth.username:
            error_logger("No username provided, aborting connection")
            raise HarmonyApiException(
                error_scope=HarmonyErrorScope.INVALID_PARAMS,
                message="Username is missing",
            )

        if not on_premise_portal_auth.password:
            error_logger("No password provided, aborting connection")
            raise HarmonyApiException(
                error_scope=HarmonyErrorScope.INVALID_PARAMS,
                message="Password is missing",
            )

        if not on_premise_portal_auth.url:
            error_logger("No URL provided, aborting connection")
            raise HarmonyApiException(
                error_scope=HarmonyErrorScope.INVALID_PARAMS,
                message="URL is missing",
            )

        try:
            parsed_url = urlparse(on_premise_portal_auth.url)
            if not parsed_url.scheme.startswith('http'):
                message = f"URL provided {on_premise_portal_auth.url} is not an http/s protocol"
                error_logger(message)
                raise HarmonyApiException(
                    message=message,
                    error_scope=HarmonyErrorScope.INVALID_PARAMS,
                )
        except Exception as error:
            message = f"URL provided {on_premise_portal_auth.url} is not a valid URL '{error}'"
            error_logger(message)
            raise HarmonyApiException(
                message=message,
                error_scope=HarmonyErrorScope.INVALID_PARAMS,
            )

    def __assert_token_is_for_correct_application(self, bearer_token: str) -> None:
        if not bearer_token:
            error_logger('No bearer token was given. Ignoring. Requests may fail')
            return

        try:
            # Token verification is NOT required here - this is just to determine whether
            # the Infinity Portal bearer is for the 'Endpoint' application
            decoded_token = jwt.decode(bearer_token, verify=VERIFY_CONTENT)
            if not decoded_token:
                error_logger('Bearer decoding yielded nothing. Ignoring. Requests may fail')
                return

            app_id = decoded_token['appId']
            if not app_id:
                error_logger('An Application ID claim was not present in the bearer token. Ignoring. Requests may fail')
                return

            endpoint_app_id = '12345678-8888-1234-1234-123456789123'
            if app_id != endpoint_app_id:
                error_logger(f"Target application is incorrect - expected '{endpoint_app_id}' but got '{app_id}'. Raising an error")
                raise HarmonyApiException(
                    message=(
                            "The provided API key must be for the 'Endpoint' service. Please refer to the documentation at "
                            'https://app.swaggerhub.com/apis/Check-Point/web-mgmt-external-api-production for more details'
                    ),
                    error_scope=HarmonyErrorScope.INVALID_PARAMS,
                )

        except jwt.InvalidTokenError:
            error_logger('The given token could not be decoded. Ignoring. Requests may fail')
            return

    def connect_cloud(self, infinity_portal_auth: InfinityPortalAuth, session_operations: SessionOperations):
        self.__work_mode = WorkMode.CLOUD
        self.__sdk_connection_state = SDKConnectionState.CONNECTING
        self.__validate_cloud_params(infinity_portal_auth)
        self.__session_operations = session_operations
        self.__infinity_portal_auth = infinity_portal_auth
        self.__url = self.__infinity_portal_auth.gateway

        logger(f'New cloud session started, ID {self.__session_id} connecting to {self.__url} using client id {infinity_portal_auth.client_id}')

        self.__perform_ci_login()
        self.__perform_endpoint_login()

        self.__activate_keep_alive()

    def connect_saas(
            self,
            infinity_portal_auth: InfinityPortalAuth,
            harmony_endpoint_saas_options: HarmonyEndpointSaaSOptions,
            session_operations: SessionOperations
    ):
        self.__work_mode = WorkMode.SAAS
        self.__sdk_connection_state = SDKConnectionState.CONNECTING
        self.__validate_cloud_params(infinity_portal_auth)
        self.__harmony_endpoint_saas_options = harmony_endpoint_saas_options
        self.__infinity_portal_auth = infinity_portal_auth
        self.__session_operations = session_operations
        self.__url = self.__infinity_portal_auth.gateway

        with_mssp = "with" if self.__harmony_endpoint_saas_options.activate_mssp_session else "without"
        logger(
            f'New saas session started *{with_mssp}* MSSP session mgmt, '
            f'session id {self.__session_id} connecting to {self.__url} using client id {infinity_portal_auth.client_id}'
        )

        self.__perform_ci_login()
        if self.__harmony_endpoint_saas_options.activate_mssp_session:
            self.__perform_mssp_login()

        self.__activate_keep_alive()

    def connect_premise(self, on_premise_portal_auth: OnPremisePortalAuth, session_operations: SessionOperations):
        self.__work_mode = WorkMode.PREMISE
        self.__sdk_connection_state = SDKConnectionState.CONNECTING
        self.__validate_premise_params(on_premise_portal_auth)
        self.__on_premise_portal_auth = on_premise_portal_auth
        self.__session_operations = session_operations
        self.__url = self.__on_premise_portal_auth.url

        if on_premise_portal_auth.disable_tls_chain_validation:
            logger(f'DISABLING TLS VALIDATION, session id {self.__session_id} connecting to {self.__url}')

        logger(f'New premise session started, session id {self.__session_id} connecting to {self.__url} using user {on_premise_portal_auth.username}')

        self.__perform_endpoint_login()
        self.__activate_keep_alive()

    def disconnect(self):
        logger(f'Disconnecting session session id {self.__session_id}')
        self.__sdk_connection_state = SDKConnectionState.DISCONNECTED
        self.__infinity_portal_auth = None
        self.__keep_alive_on_flag = False
        self.__infinity_portal_token = ''
        self.__endpoint_token = ''
        self.__session_id = str(uuid.uuid4())

    def reconnect(self):
        if not self.__work_mode:
            error_logger("No connection established yet")
            raise HarmonyApiException(
                error_scope=HarmonyErrorScope.SESSION,
                message="No connection established, login first",
            )

        logger(f"Reconnecting session {self.__session_id}")
        self.disconnect()

        if self.__work_mode == WorkMode.CLOUD:
            self.connect_cloud(self.__infinity_portal_auth, self.__session_operations)
        elif self.__work_mode == WorkMode.SAAS:
            self.connect_saas(self.__infinity_portal_auth, self.__session_operations, self.__harmony_endpoint_saas_options)
        else:
            self.connect_premise(self.__on_premise_portal_auth, self.__session_operations)

    def connection_state(self) -> SDKConnectionState:
        return self.__sdk_connection_state
