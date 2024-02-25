# -*- coding: utf-8 -*-
from pathlib import Path
from setuptools import find_packages, setup

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

package_data = \
{'': ['*']}

prod_dependencies = [
    'aenum==3.1.15',
    'certifi==2023.7.22',
    'charset-normalizer==3.3.0',
    'frozendict==2.3.10',
    'idna==3.4',
    'MarkupSafe==2.1.3',
    'python-dateutil==2.8.2',
    'python-dotenv==1.0.0',
    'requests==2.31.0',
    'typing-extensions==4.8.0',
    'unitsnet-py==0.1.82',
    'urllib3==2.0.7',
]

setup_kwargs = {
    'name': "chkp-harmony-endpoint-management-sdk",
    'version': '1.1.26',
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

