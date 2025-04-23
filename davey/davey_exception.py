class DaveyAPIException(Exception):
    pass


class DaveyAuthException(DaveyAPIException):
    pass


class DaveyRequestException(DaveyAPIException):
    pass