import os
import sys
from pathlib import Path
import subprocess
import shutil
from scripts.fetch_api import fetch_api_specs
from scripts.post_build import post_build_process

# Load environment variables from .env if it exists
if os.path.exists('./.env'):
    from dotenv import load_dotenv
    load_dotenv()

def generate(spec: str):
    log_prefix: str = '[generate]'

    this_dir_path = os.path.join(os.path.dirname(__file__))
    project_dir =  Path(this_dir_path, '../')

    templates_dir = os.path.join(this_dir_path, 'templates')
    specs_path: str = os.path.join(project_dir, 'resources', 'specs', spec, 'swagger.json')

    generator_path: str = os.path.join(this_dir_path, 'open_api_tool', 'openapi-generator-cli-6.6.0' )

    jre_path = os.getenv('JRE_PATH', 'java')

    generated_path: str = os.path.join(project_dir, 'chkp_harmony_endpoint_management_sdk', 'generated', spec)


    try:

        if os.path.exists(generated_path):
            shutil.rmtree(
                generated_path,
                ignore_errors=True,
                onerror=lambda err: print(f'[generate.generate] Faulted whilst cleaning generator output directory: {err}'),
            )

        cmd_line = (
            f'"{jre_path}"' + f' -jar {generator_path}' + ' generate' + f' -t {templates_dir}'
            ' --generator-name python'
            + f' --input-spec {specs_path}'
            + f' --output {project_dir}'
            + f' --template-dir {templates_dir}'
            + f' --global-property modelDocs=false,modelTests=false'
            + f' --additional-properties=generateSourceCodeOnly=true,packageName=chkp_harmony_endpoint_management_sdk.generated.{spec}'
        )
        print(f'{log_prefix} Invoking generator at {generator_path} with command:\n{cmd_line}')
        subprocess.run(cmd_line, shell=True, check=True, stdout=sys.stdout)
       
    except subprocess.CalledProcessError as e:
        print(f'[generate.generate] Generator returned an error:\n\t{e}\n\tStdout: {e.stdout}\n\tStderr: {e.stderr}')


def build_spec(spec: str) -> None:
    log_prefix: str = '[Build.generate_api_client_stubs]'
    # output_path: str = str(Path(__file__).parent.joinpath('..', 'harmony_endpoint_management_sdk', 'generated', spec).resolve())
    # print(f"{log_prefix} Build starting. Target: {spec}, Output directory: '{output_path}'")
    print(f'{log_prefix} Generating client stubs...')
    generate(spec)


def build() -> None:
    build_spec('cloud')
	# TODO: Open when on-premise will be release to public
    # build_spec('premise')
    build_spec('saas')

def start_generate_process():
    fetch_api_specs()
    build()
    post_build_process()

start_generate_process()