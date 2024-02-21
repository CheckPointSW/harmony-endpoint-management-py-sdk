import logging
import os
import datetime

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

if __activate_logs == '*':
    _logger.setLevel(logging.DEBUG)
    _error_logger.setLevel(logging.DEBUG)
    _network_logger.setLevel(logging.DEBUG)
else:
    loggers = __activate_logs.split(',')
    
    if 'info' in loggers:
        _logger.setLevel(logging.DEBUG)

    if 'error' in loggers:
        _error_logger.setLevel(logging.DEBUG)

    if 'network' in loggers:
        _network_logger.setLevel(logging.DEBUG)

logger = _logger.debug
error_logger = _error_logger.error
network_logger = _network_logger.info

logger(f'logger is activated with "{__activate_logs}"')
