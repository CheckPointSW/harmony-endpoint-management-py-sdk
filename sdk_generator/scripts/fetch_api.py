import os
import json
import requests

# The API owner
API_SPEC_OWNER = 'Check-Point'

BRANCH_NAME = os.environ.get('CI_COMMIT_REF_NAME') or os.environ.get('BRANCH_NAME')

print(f'[fetch-api] Set {BRANCH_NAME} as CI/CD branch')
print(f'[fetch-api] Set {os.environ.get("BUILD_JOB_ID")} as CI/CD job id')

# Commons
# Build API based on the develop branch, unless it's built for the main branch, then use the main branch API.
CLOUD_SPEC_NAME = os.environ.get('CLOUD_SPEC_NAME', 'web-mgmt-external-api-production')
PREMISE_SPEC_NAME = os.environ.get('PREMISE_SPEC_NAME', 'web-mgmt-external-api-premise')
SAAS_SPEC_NAME = os.environ.get('SAAS_SPEC_NAME', 'harmony-endpoint-cloud-api-prod')

print(f'[fetch-api] The spec for cloud is {CLOUD_SPEC_NAME} for "{BRANCH_NAME}"')
print(f'[fetch-api] The spec for premise is {PREMISE_SPEC_NAME} for "{BRANCH_NAME}"')
print(f'[fetch-api] The spec for saas is {SAAS_SPEC_NAME} for "{BRANCH_NAME}"')

LOCAL_GENERATED_API_PATH = os.environ.get('LOCAL_GENERATED_API_PATH')
LOCAL_PREMISE_GENERATED_API_PATH = os.environ.get('LOCAL_PREMISE_GENERATED_API_PATH')
LOCAL_SAAS_GENERATED_API_PATH = os.environ.get('LOCAL_SAAS_GENERATED_API_PATH')

if LOCAL_GENERATED_API_PATH:
    print('[fetch-api] Generating API using local generated API ...')

if LOCAL_PREMISE_GENERATED_API_PATH:
    print('[fetch-api] Generating Premise API using local generated API ...')

if LOCAL_SAAS_GENERATED_API_PATH:
    print('[fetch-api] Generating SaaS API using local generated API ...')

SWAGGERHUB_API_KEY = os.environ.get('SWAGGERHUB_API_KEY')

swagger_headers = {
    'Content-Type': 'application/json',
}

if SWAGGERHUB_API_KEY:
    swagger_headers['Authorization'] = f'Bearer {SWAGGERHUB_API_KEY}'

SWAGGER_CONF = 'swagger.json'

OUTPUT_BASE_PATH = 'resources/specs'

# Create directories and fetch Swagger configurations
def __mkdir_recursive(dir_path):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

def __deposit_file(api_root_path, file_name, file_content):
    file_path = os.path.join(api_root_path, file_name)
    with open(file_path, 'w') as file:
        file.write(file_content)

def __download_spec(spec):
    print('[fetch-api] Fetching API versions from SwaggerHub...')

    # Fetch all available versions from SwaggerHub API (Replace with Python requests)
    all_specs_res = requests.get(f'https://api.swaggerhub.com/apis/{API_SPEC_OWNER}/{spec}', headers=swagger_headers)
    all_specs = all_specs_res.json()

    # Get the latest API available
    latest_version_info = all_specs['apis'][-1]

    # Find the Swagger property with the URL to the spec (Replace with Python requests)
    latest_version_url = next((prop['url'] for prop in latest_version_info['properties'] if prop['type'] == 'Swagger'), None)

    print(f'[fetch-api] Fetching API Spec from SwaggerHub URL "{latest_version_url}"')

    # Fetch the spec (Replace with Python requests)
    latest_spec_res = requests.get(latest_version_url, headers=swagger_headers)
    latest_spec = latest_spec_res.json()

    return latest_spec

def __read_local_file(root, file_name):
    try:
        with open(os.path.join(root, file_name), 'r') as file:
            return file.read()
    except Exception as e:
        print(f'[fetch-api] Error while trying to read local file {file_name}', e)

def __get_swagger_config(local_swagger_path, spec, dist):
    print('[fetch-api] Getting swagger config...')
    if local_swagger_path:
        swagger_spec = __read_local_file(local_swagger_path, SWAGGER_CONF)
    else:
        swagger_spec = __download_spec(spec)

    content = json.loads(swagger_spec) if local_swagger_path else swagger_spec

    # content_schemas = content['components']['schemas']

    # for schema_name, schema in content_schemas.items():
    #     if not schema.get('oneOf') or len(schema['oneOf']) != 2:
    #         continue

    #     job_schema_index = next((i for i, s in enumerate(schema['oneOf']) if s.get('$ref') == '#/components/schemas/JobCreationResult'), -1)

    #     if job_schema_index == -1:
    #         continue

    #     schema['oneOf'].pop(job_schema_index)
    #     original_res = schema['oneOf'][0].copy()
    #     del schema['oneOf']

    #     for item_name, item in original_res.items():
    #         schema[item_name] = item


    final_dist = os.path.join(OUTPUT_BASE_PATH, dist)
    __mkdir_recursive(final_dist)

    __deposit_file(final_dist, SWAGGER_CONF, json.dumps(content))
    __deposit_file(final_dist, 'spec', spec)


def fetch_api_specs():

    # Make sure the output directory exists
    __mkdir_recursive(OUTPUT_BASE_PATH)

    # Downloads swagger.conf from LOCAL or ARTIFACTORY
    __get_swagger_config(LOCAL_GENERATED_API_PATH, CLOUD_SPEC_NAME, 'cloud')
	# TODO: Open when on-premise will be release to public
    # __get_swagger_config(LOCAL_PREMISE_GENERATED_API_PATH, PREMISE_SPEC_NAME, 'premise')
    __get_swagger_config(LOCAL_SAAS_GENERATED_API_PATH, SAAS_SPEC_NAME, 'saas')

