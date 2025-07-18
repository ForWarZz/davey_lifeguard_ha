"""Custom exceptions for Davey API interactions."""


class DaveyAPIException(Exception):
    """Base exception for Davey API errors."""


class DaveyAuthException(DaveyAPIException):
    """Exception raised for authentication errors in Davey API."""


class DaveyRequestException(DaveyAPIException):
    """Exception raised for errors during Davey API requests."""
