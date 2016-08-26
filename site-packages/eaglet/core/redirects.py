# -*- coding: utf-8 -*-

__author__ = 'bert'

import json
import falcon
from falcon.http_status import HTTPStatus

class HTTPFound(HTTPStatus):
    """302 Found.
    The 302 (Found) status code indicates that the target resource
    resides temporarily under a different URI.  Since the redirection
    might be altered on occasion, the client ought to continue to use the
    effective request URI for future requests.
    Note:
        For historical reasons, a user agent MAY change the request
        method from POST to GET for the subsequent request.  If this
        behavior is undesired, the 307 (Temporary Redirect) status code
        can be used instead.
    See also: https://tools.ietf.org/html/rfc7231#section-6.4.3
    Args:
        location (str): URI to provide as the Location header in the
            response.
    """

    def __init__(self, location):
        super(HTTPFound, self).__init__(
            '302 Moved Temporarily', {'location': location})


class HTTPMiddlewareError(HTTPStatus):
    """201
    用于中间件异常响应
    """
    def __init__(self, body, headers=None):
        super(HTTPMiddlewareError, self).__init__(
          falcon.HTTP_201, headers,json.dumps(body))    
