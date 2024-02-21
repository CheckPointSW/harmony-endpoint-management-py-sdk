from unitsnet_py import Duration

JOBS_PULLING_INTERVAL: Duration = Duration.from_seconds(5)
KEEP_ALIVE_INTERVAL: Duration = Duration.from_seconds(15)
KEEP_ALIVE_PERFORM_GRACE: Duration = Duration.from_seconds(40)
MSSP_KEEP_ALIVE_EXPIRATION: Duration = Duration.from_minutes(2)

MAX_FAILED_PULLING_ATTEMPTS = 5
