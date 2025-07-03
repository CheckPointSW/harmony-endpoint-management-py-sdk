
class HarmonyEndpointSDKInfo:
    def __init__(self, sdk_build: str, sdk_version: str, spec: str, spec_version: str, released_on: str):
        self.sdk_build = sdk_build
        self.sdk_version = sdk_version
        self.spec = spec
        self.spec_version = spec_version
        self.released_on = released_on

    def __str__(self):
        return (
            f'sdk_build:"{self.sdk_build}", '
            f'sdk_version:"{self.sdk_version}", '
            f'spec:"{self.spec}", '
            f'spec_version:"{self.spec_version}", '
            f'released_on:"{self.released_on}"'
        )
