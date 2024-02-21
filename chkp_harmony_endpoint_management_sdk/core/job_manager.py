
from typing import Any, Callable
import time
from chkp_harmony_endpoint_management_sdk.classes.harmony_api_exception import HarmonyApiException, HarmonyErrorScope
from chkp_harmony_endpoint_management_sdk.core.sdk_platform import JOBS_PULLING_INTERVAL, MAX_FAILED_PULLING_ATTEMPTS
from chkp_harmony_endpoint_management_sdk.core.logger import logger, error_logger

def await_for_job(job_id: str, job_status_operation: Callable[[], Any], request_id: str):

    if not job_id:
        msg = f'No job provided from service for request "{request_id}"'
        error_logger(msg)
        raise HarmonyApiException(error_scope=HarmonyErrorScope.SERVICE,
                           request_id=request_id,
                           message=msg)
    
    logger(f'Starting job "{job_id}" pulling process..')

    pulling_failed_attempts = 0

    job_status_res = None
    while True:
        time.sleep(JOBS_PULLING_INTERVAL.seconds)
        logger(f'Pulling job "{job_id}" status...')

        try:
            job_status_res = job_status_operation(job_id)
            pulling_failed_attempts = 0
        except:
            pulling_failed_attempts = pulling_failed_attempts + 1
            if pulling_failed_attempts > MAX_FAILED_PULLING_ATTEMPTS:
                    msg = f'Pulling job "{job_id}" failed attempt "{pulling_failed_attempts}", aborting pulling'
                    error_logger(msg)
                    raise HarmonyApiException(error_scope=HarmonyErrorScope.SERVICE, request_id=request_id, message=msg, payload_error=job_status_res.payload)
                   
            error_logger(f'Pulling job "{job_id}" failed attempt "{pulling_failed_attempts}", will try again in next pulling attempt')
            continue
        
        logger(f'Job "{job_id}" status is "{job_status_res.payload["status"]}"')

        if job_status_res.payload['status'] == 'DONE':
            break
        
        if job_status_res.payload["status"] == 'NOT_FOUND' or job_status_res.payload["status"] == 'FAILED':
                error_logger(f'Job "{job_id}" failed with status "{job_status_res.payload["status"]}", error: {job_status_res.payload}')
                raise HarmonyApiException(error_scope=HarmonyErrorScope.SERVICE, request_id=request_id, message=msg, payload_error=job_status_res.payload)
             
    logger(f'Job "{job_id}" finished successfully')
    
    return job_status_res.payload.get('data')
