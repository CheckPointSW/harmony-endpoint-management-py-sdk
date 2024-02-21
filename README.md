# Check Point - Harmony Endpoint Management Python SDK

[![License](https://img.shields.io/github/license/CheckPointSW/harmony-endpoint-management-py-sdk.svg?style=plastic)](https://github.com/CheckPointSW/harmony-endpoint-management-py-sdk/blob/release/LICENSE) [![Latest Release](https://img.shields.io/github/v/release/CheckPointSW/harmony-endpoint-management-py-sdk?style=plastic)](https://github.com/CheckPointSW/harmony-endpoint-management-py-sdk/releases) [![PyPI version](https://img.shields.io/pypi/v/chkp-harmony-endpoint-management-sdk.svg?style=plastic)](https://pypi.org/project/chkp-harmony-endpoint-management-sdk/)


<!-- 
Coming soon :)

[![npm downloads](https://img.shields.io/npm/dt/@chkp/harmony-endpoint-management-sdk.svg.svg?style=plastic)](https://npmjs.com/package/@chkp/harmony-endpoint-management-sdk.svg)

[![GitHub stars](https://img.shields.io/github/stars/CheckPointSW/harmony-endpoint-management-py-sdk.svg?style=social&label=Star)](https://github.com/CheckPointSW/harmony-endpoint-management-py-sdk/stargazers) -->

[![Build SDK Package](https://github.com/CheckPointSW/harmony-endpoint-management-py-sdk/actions/workflows/build.yml/badge.svg)](https://github.com/CheckPointSW/harmony-endpoint-management-py-sdk/actions/workflows/build.yml) [![Publish package to PyPI](https://github.com/CheckPointSW/harmony-endpoint-management-py-sdk/actions/workflows/release.yml/badge.svg)](https://github.com/CheckPointSW/harmony-endpoint-management-py-sdk/actions/workflows/release.yml)

This is the Harmony Endpoint management SDK for Python ecosystem.

The SDK is based on the public [Harmony Endpoint management OpenAPI](https://app.swaggerhub.com/apis/Check-Point/web-mgmt-external-api-production) specifications.

With the SDK, you do not have to manage log in, send keep alive requests, worry about session expiration or pull long processing jobs.

> 💡 The Harmony Endpoint SDK supports simultaneous instances with different tenants.

---
🚧🚧🚧 

**Note that the SDK package is in Early Availability (EA). Use with caution, as it may undergo changes and improvements. Feedback and contributions are highly encouraged.** 

To report a bug, please go to [Report Bug](#-report-bug)

For feedback, please get in touch with us at [Check Point Software Technologies Ltd.](mailto:harmony-endpoint-external-api@checkpoint.com)

🚧🚧🚧 

---

## ⬇️ SDK installation

To start using this SDK, add the SDK package to your project

Via PIP (PyPi registry)
```bash 
pip install chkp-harmony-endpoint-management-sdk
```

## 🚀 Getting started

First, import the `HarmonyEndpoint` object from the package.

```python
from chkp_harmony_endpoint_management_sdk import HarmonyEndpoint
```

Then, create a new instance of `HarmonyEndpoint`, which provides CloudInfra API credentials and a gateway to connect to.

To obtain CloudInfra credentials, open the Infinity Portal and create a suitable API Key. Make sure to select `Endpoint` in the `Service` field. For more information, see [Infinity Portal Administration Guide](https://sc1.checkpoint.com/documents/Infinity_Portal/WebAdminGuides/EN/Infinity-Portal-Admin-Guide/Content/Topics-Infinity-Portal/API-Keys.htm?tocpath=Global%20Settings%7C_____7#API_Keys).

Once the Client ID, Secret Key, and Authentication URL are obtained, Harmony Endpoint SDK can be used.

All API operations can be explored with the `HarmonyEndpoint` instance, notice to the documentation on each API operation, what and where are the arguments it requires.

All API's can be also explored in [SwaggerHub](https://app.swaggerhub.com/apis/Check-Point/web-mgmt-external-api-production)

A complete example:

```python
from chkp_harmony_endpoint_management_sdk import HarmonyEndpoint, InfinityPortalAuth

# Create a new instance of HarmonyEndpoint (we do support multiple instances in parallel)
he = HarmonyEndpoint()

# Connect to management using CloudInfra API credentials
he.connect(infinity_portal_auth=InfinityPortalAuth(
        client_id="place here your CI client-id", # The "Client ID"
        access_key= "place here your CI access-key", # The "Secret Key"
        gateway="https://cloudinfra-gw-us.portal.checkpoint.com/auth/external" # The "Authentication URL"
        )) 

# Query the API operation
rules_metadata_res = he.policy_general_api.get_all_rules_metadata(header_params={ "x-mgmt-run-as-job": 'off'})
print(rules_metadata_res.payload)  # Your rulebase metadata

# Also you can query this operation using job, no extra logic required, in the background, it will trigger a job and will pull the status till it finish and return the final results. 
rules_metadata_res = he.policy_general_api.get_all_rules_metadata(header_params={ "x-mgmt-run-as-job": 'on'})
print(rules_metadata_res.is_job)  # True
print(rules_metadata_res.payload)  # Your rulebase metadata

# Once finish, disconnect to stop all background session management. 
he.disconnect()
```

### 🏠 On-premise

🛠️🛠️🛠️ **Under Development** 🛠️🛠️🛠️

Harmony Endpoint On-premise instances are also supported.

> Pay attention! Not all cloud operations are available for on-premise, also need to specify the SDK version to comply with your Gaia / JHF version


```python
from chkp_harmony_endpoint_management_sdk import HarmonyEndpointPremise, OnPremisePortalAuth

# Create a new instance of HarmonyEndpoint (we do support multiple instances in parallel)
hep = HarmonyEndpointPremise()

# Connect to management using CloudInfra API credentials
hep.connect(on_premise_portal_auth=OnPremisePortalAuth(
    username="xxxx", 
    password= "xxxx", 
    url="https://x.x.x.x",
    disable_tls_chain_validation=False # Set it true only if you fully trust this URL (e.g. case of internal but not verified https certificate)
    )) 

# Query the API operation
rules_metadata_res = hep.policy_general_api.get_all_rules_metadata(header_params={ "x-mgmt-run-as-job": 'off'})
print(rules_metadata_res.payload)  # Your rulebase metadata

# Once all finish, disconnect to stop all background session management. 
hep.disconnect()
```

On-Premises API can be explored in [SwaggerHub](https://app.swaggerhub.com/apis/Check-Point/web-mgmt-external-api-premise)

### ☁️ Cloud & MSSP services APIs

Harmony Endpoint also provides APIs for MSSP and Cloud service management (relevant to SaaS customers only) 


The usage is similar to the management API
```python
from chkp_harmony_endpoint_management_sdk import HarmonyEndpointSaaS, InfinityPortalAuth

he_saas = HarmonyEndpointSaaS()

# Connect to management using CloudInfra API credentials
he_saas.connect(infinity_portal_auth=InfinityPortalAuth(
        client_id="place here your CI client-id", # The "Client ID"
        access_key= "place here your CI access-key", # The "Secret Key"
        gateway="https://cloudinfra-gw-us.portal.checkpoint.com/auth/external" # The "Authentication URL"
        )) 

# Query the cloud API operation
instance_status_res = he_saas.self_service_api.public_machines_single_status()
print(instance_status_res.payload)  # Your instance status

he_saas.disconnect()
```
API available at [SwaggerHub](https://app.swaggerhub.com/apis/Check-Point/harmony-endpoint-cloud-api-prod)

## 🔍 Troubleshooting and logging

The full version and build info of the SDK is available by `HarmonyEndpoint.info()` see example:
```python
from chkp_harmony_endpoint_management_sdk import HarmonyEndpoint, HarmonyEndpointSDKInfo

sdk_info: HarmonyEndpointSDKInfo = HarmonyEndpoint.info()
print(sdk_info) # sdk_build:"9728283", sdk_version:"1.0.2", spec:"web-mgmt-external-api-production", spec_version:"1.9.159", released_on:"2023-09-10T18:14:38.264Z"
```

Harmony Endpoint Management SDK uses the official python logger package for logging.

There are 3 loggers, for general info, errors and to inspect network.

As default they will be disabled, in order to enable logging, set to the `HARMONY_ENDPOINT_SDK_LOGGER` environment variable the following string:
```bash
HARMONY_ENDPOINT_SDK_LOGGER="*"
```

And for a specific/s logger set the logger name followed by a command as following:
```bash
HARMONY_ENDPOINT_SDK_LOGGER="info,error,network"
```

## 🐞 Report Bug

In case of an issue or a bug found in the SDK, please open an [issue](https://github.com/CheckPointSW/harmony-endpoint-management-py-sdk/issues) or report to us [Check Point Software Technologies Ltd](mailto:harmony-endpoint-external-api@checkpoint.com).

## 🤝 Contributors 
- Haim Kastner - [chkp-haimk](https://github.com/chkp-haimk)
- Yuval Pomerchik - [chkp-yuvalpo](https://github.com/chkp-yuvalpo)
