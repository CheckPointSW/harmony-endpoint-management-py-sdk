import logging
import os

handler = logging.StreamHandler()

formatter = logging.Formatter('[%(name)s][%(asctime)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
handler.setFormatter(formatter)

_logger = logging.getLogger('chkp_harmony_endpoint_management_sdk:info')
_error_logger = logging.getLogger('chkp_harmony_endpoint_management_sdk:error')
_network_logger = logging.getLogger('chkp_harmony_endpoint_management_sdk:network')

_logger.addHandler(handler)
_error_logger.addHandler(handler)
_network_logger.addHandler(handler)

# * OR info, error, network
__activate_logs = os.environ.get('HARMONY_ENDPOINT_SDK_LOGGER', '')

_logger.setLevel(logging.CRITICAL + 1)
_error_logger.setLevel(logging.CRITICAL + 1)
_network_logger.setLevel(logging.CRITICAL + 1)

logger = _logger.debug
error_logger = _error_logger.error
network_logger = _network_logger.info

logger(f'logger is activated with "{__activate_logs}"')


def activate_all_loggers():
    _logger.setLevel(logging.DEBUG)
    _error_logger.setLevel(logging.DEBUG)
    _network_logger.setLevel(logging.DEBUG)


def activate_info_logger():
    _logger.setLevel(logging.DEBUG)


def activate_error_logger():
    _error_logger.setLevel(logging.DEBUG)


def activate_network_logger():
    _network_logger.setLevel(logging.DEBUG)


if __activate_logs == '*':
    activate_all_loggers()
else:
    loggers = __activate_logs.split(',')

    if 'info' in loggers:
        activate_info_logger()

    if 'error' in loggers:
        activate_error_logger()

    if 'network' in loggers:
        activate_network_logger()
