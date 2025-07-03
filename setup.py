# -*- coding: utf-8 -*-
from pathlib import Path
from setuptools import find_packages, setup

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

package_data = \
    {'': ['*']}

prod_dependencies = [
    'aenum~=3.1',
    'certifi>=2024.0,<2026.0',
    'charset-normalizer~=3.3',
    'frozendict~=2.3',
    'idna~=3.7',
    'MarkupSafe~=2.1',
    'python-dateutil~=2.8',
    'python-dotenv~=1.0',
    'requests~=2.32',
    'typing-extensions~=4.9.0',
    'pyjwt~=2.8',
    'unitsnet-py>=0.1.82',
    'urllib3~=2.2',
]

setup_kwargs = {
    'name': "chkp-harmony-endpoint-management-sdk",
    'version': '1.2.2',
    'keywords': 'python, harmony, endpoint, sdk, checkpoint',
    'license': 'MIT',
    'description': 'Harmony Endpoint Official Python SDK',
    'long_description': long_description,
    'long_description_content_type': "text/markdown",
    'author': 'Haim Kastner',
    'author_email': 'haimk@checkpoint.com',
    'maintainer': 'Haim Kastner',
    'maintainer_email': 'haimk@checkpoint.com',
    'url': 'https://github.com/CheckPointSW/harmony-endpoint-management-py-sdk',
    'packages': find_packages(exclude=['sdk_generator', 'scripts' 'tests']),
    'package_data': package_data,
    'install_requires': prod_dependencies,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
