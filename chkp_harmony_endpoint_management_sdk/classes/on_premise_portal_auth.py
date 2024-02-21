class OnPremisePortalAuth:
    def __init__(self, username: str, password: str, url: str, disable_tls_chain_validation: bool = False):
        self.username = username
        self.password = password
        self.url = url
        self.disable_tls_chain_validation = disable_tls_chain_validation
