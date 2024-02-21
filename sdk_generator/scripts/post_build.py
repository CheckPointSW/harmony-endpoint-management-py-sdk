import os
import shutil
import json
from datetime import datetime

BASE_PATH = 'chkp_harmony_endpoint_management_sdk'
OUTPUT_BASE_PATH = f'{BASE_PATH}/generated'

def __replace_string_in_file(file_path, search_str, replace_str):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = file.read()
    
    data = data.replace(search_str, replace_str)
    
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(data)


def __prepare_build_info(output_path, spec_path, spec_source):
    swagger_spec = ''
    spec_name = ''

    with open(os.path.join(spec_path, 'swagger.json'), 'r') as file:
        # Parse the JSON data from the file
        swagger_spec = json.load(file)
    with open(os.path.join(spec_path, 'spec'), 'r') as file:
        # Read the first line and trim it
        spec_name = file.readline().strip()

    sdk_build = os.environ.get('BUILD_JOB_ID', '')
    released_on = datetime.now().isoformat()
    sdk_version = os.environ.get('BUILD_VERSION', '')
    spec = spec_name
    spec_version =  swagger_spec['info']['version']

    sdk_build_module = f'''
from chkp_harmony_endpoint_management_sdk.classes.harmony_endpoint_sdk_info import HarmonyEndpointSDKInfo

def sdk_build_info() -> HarmonyEndpointSDKInfo:
    return HarmonyEndpointSDKInfo(sdk_build="{sdk_build}",sdk_version="{sdk_version}",spec="{spec}",spec_version="{spec_version}",released_on="{released_on}")
'''

    with open(os.path.join(output_path, spec_source, 'sdk_build.py'), 'w', encoding='utf-8') as file:
        # Write the string to the file
        file.write(sdk_build_module)



def post_build_process():
    # Manually and hard-coded set session management to be private and to be used by SDK internally only.
    print("[post-generate-api] Set session management to be private")
    __replace_string_in_file(os.path.join(OUTPUT_BASE_PATH, 'cloud/__init__.py'), 'def session_api(self):', 'def _session_api(self):')
	# TODO: Open when on-premise will be release to public
    # __replace_string_in_file(os.path.join(OUTPUT_BASE_PATH, 'premise/__init__.py'), 'def session_api(self):', 'def _session_api(self):')
    __replace_string_in_file(os.path.join(OUTPUT_BASE_PATH, 'saas/__init__.py'), 'def manage_session_api(self):', 'def _manage_session_api(self):')
    print("[post-generate-api] Set session management to be private done")

    print("[post-generate-api] Preparing build info manifest")
    __prepare_build_info(OUTPUT_BASE_PATH, 'resources/specs/cloud', 'cloud')
	# TODO: Open when on-premise will be release to public
    # __prepare_build_info(OUTPUT_BASE_PATH, 'resources/specs/premise', 'premise')
    __prepare_build_info(OUTPUT_BASE_PATH, 'resources/specs/saas', 'saas')
    print("[post-generate-api] Preparing build info manifest finished")

    print("[post-generate-api] Clearing unwanted generated files ...")
    
    shutil.rmtree('test/test_paths')
    
    shutil.rmtree(os.path.join(OUTPUT_BASE_PATH, 'cloud/test'))
	# TODO: Open when on-premise will be release to public
    # shutil.rmtree(os.path.join(OUTPUT_BASE_PATH, 'premise/test'))
    shutil.rmtree(os.path.join(OUTPUT_BASE_PATH, 'saas/test'))

    shutil.rmtree(os.path.join(OUTPUT_BASE_PATH, 'cloud/docs'))
	# TODO: Open when on-premise will be release to public
    # shutil.rmtree(os.path.join(OUTPUT_BASE_PATH, 'premise/docs'))
    shutil.rmtree(os.path.join(OUTPUT_BASE_PATH, 'saas/docs'))
    
    print("[post-generate-api] Clearing unwanted generated files finished")



    print("[post-generate-api] Setting the proper __init__ export file ...")
    shutil.copy(os.path.join(BASE_PATH, '__init__template.py'), os.path.join(BASE_PATH, '__init__.py'))
    print("[post-generate-api] Setting the proper __init__ export file finished")

