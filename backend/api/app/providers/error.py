class ProviderApiError(Exception):
    def __init__(
        self,
        provider: str,
        status_code: int,
        message: str,
    ) -> None:
        self.provider = provider
        self.status_code = status_code
        self.message = message
