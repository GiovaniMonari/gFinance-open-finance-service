class OpenFinanceError(Exception):
    """Base class for errors raised while talking to a provider.

    Carries the HTTP status the router should answer with, so the transport
    layer never has to interpret provider-specific exception types.
    """

    status_code = 500
    default_detail = "Erro ao processar a conexão financeira"

    def __init__(self, detail: str | None = None):
        self.detail = detail or self.default_detail
        super().__init__(self.detail)


class ConnectionNotFoundError(OpenFinanceError):
    """The connection does not exist, or belongs to another user.

    Both cases answer 404 on purpose: telling a caller that an id exists but
    is owned by somebody else would leak another user's data.
    """

    status_code = 404
    default_detail = "Conexão não encontrada"


class ConnectionAlreadyDisconnectedError(OpenFinanceError):
    """The local record already says the connection was revoked."""

    status_code = 409
    default_detail = "A conexão já está desconectada"


class ProviderNotFoundError(OpenFinanceError):
    """The provider has no record of this connection any more.

    Treated as a terminal, already-revoked state rather than a failure: the
    outcome the user asked for is already true upstream.
    """

    status_code = 404
    default_detail = "O provedor não encontrou esta conexão"


class ProviderAuthError(OpenFinanceError):
    """We could not authenticate against the provider."""

    status_code = 502
    default_detail = "Não foi possível autenticar no provedor de Open Finance"


class ProviderUnavailableError(OpenFinanceError):
    """The provider answered with an error, or did not answer at all."""

    status_code = 502
    default_detail = "O provedor de Open Finance está indisponível"
