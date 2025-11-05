#
# Copyright (C) 2025 pdnguyen of HCMC University of Technology VNU-HCM.
# All rights reserved.
# This file is part of the CO3093/CO3094 course.
#
# WeApRous release
#
# The authors hereby grant to Licensee personal permission to use
# and modify the Licensed Source Code for the sole purpose of studying
# while attending the course
#

"""
daemon.request
~~~~~~~~~~~~~~~~~

This module provides a Request object to manage and persist 
request settings (cookies, auth, proxies).
"""
from .dictionary import CaseInsensitiveDict
#^^--------------------------------------------------------------------^^#
import json
#^^====================================================================^^#


class Request():
    """The fully mutable "class" `Request <Request>` object,
    containing the exact bytes that will be sent to the server.

    Instances are generated from a "class" `Request <Request>` object, and
    should not be instantiated manually; doing so may produce undesirable
    effects.

    Usage::

      >>> import deamon.request
      >>> req = request.Request()
      ## Incoming message obtain aka. incoming_msg
      >>> r = req.prepare(incoming_msg)
      >>> r
      <Request>
    """
    __attrs__ = [
        "method",
        "url",
        "headers",
        "body",
        "reason",
        "cookies",
        "body",
        "routes",
        "hook",
    ]

    def __init__(self):
        #: HTTP verb to send to the server.
        self.method = None
        #: HTTP URL to send the request to.
        self.url = None
        #: dictionary of HTTP headers.
        self.headers = None
        #: HTTP path
        self.path = None        
        # The cookies set used to create Cookie header
        self.cookies = None
        #: request body to send to the server.
        self.body = None
        #: Routes
        self.routes = {}
        #: Hook point for routed mapped-path
        self.hook = None
        #^^ json
        self.json_data = None
        #^^====================================================================^^#


    def extract_request_line(self, request):
        try:
            lines = request.splitlines()
            first_line = lines[0]
            method, path, version = first_line.split()

            if path == '/':
                path = '/index.html'
        except Exception:
            return None, None

        return method, path, version
             
    def prepare_headers(self, request):
        """Prepares the given HTTP headers."""
        lines = request.split('\r\n')
        headers = {}
        for line in lines[1:]:
            if ': ' in line:
                key, val = line.split(': ', 1)
                headers[key.lower()] = val
        #^^--------------------------------------------------------------------^^#
        print("[request.py-prepare_headers] header content: \n{}".format(headers))
        #^^====================================================================^^#
        return headers

    def prepare(self, request, routes=None):
        """Prepares the entire request with the given parameters."""

        #^^ View RAW request^^#
        print("[Request] RAW request content: \n{}".format(request))
        #^^====================================================================^^#

        # Prepare the request line from the request header
        self.method, self.path, self.version = self.extract_request_line(request)
        print("[Request] {} path {} version {}".format(self.method, self.path, self.version))

        #
        # @bksysnet Preapring the webapp hook with WeApRous instance
        # The default behaviour with HTTP server is empty routed
        #
        # TODO manage the webapp hook in this mounting point
        #
        
        if not routes == {}:
            self.routes = routes
            self.hook = routes.get((self.method, self.path))
            #
            # self.hook manipulation goes here
            # ...
            #

        self.headers = self.prepare_headers(request)
        cookies = self.headers.get('cookie', '')
            #
            #  TODO: implement the cookie function here
            #        by parsing the header            #

        #^^--------------------------------------------------------------------^^#
        self.body = self.extract_body(request)
        
        if self.isJSON():
            self.json_data = self.parse_JSON(self.body)
        #^^====================================================================^^#
        return

    def prepare_body(self, data, files, json=None):
        self.prepare_content_length(self.body)
        self.body = body
        #
        # TODO prepare the request authentication
        #
	# self.auth = ...
        return


    def prepare_content_length(self, body):
        self.headers["Content-Length"] = "0"
        #
        # TODO prepare the request authentication
        #
	# self.auth = ...
        return


    def prepare_auth(self, auth, url=""):
        #
        # TODO prepare the request authentication
        #
	# self.auth = ...
        return

    def prepare_cookies(self, cookies):
            self.headers["Cookie"] = cookies

#^^--------------------------------------------------------------------^^#
    def isJSON(self):
        """Check if request has JSON content type."""
        content_type = self.headers.get('content-type', '')
        if (self.body is not None) and ('application/json' in content_type):
            return True
        return False

    def extract_body(self, request):
        """
        Extract body from HTTP request.
        Body is everything after \r\n\r\n separator.
        """
        separator = '\r\n\r\n'
        if separator in request:
            parts = request.split(separator, 1)
            if len(parts) == 2:
                body = parts[1].strip()
                print("[request.py-extract_body] {}".format(body))
                return body
        return None
    
    def parse_JSON(self, body):
        """
        Parse JSON from body string
        """
        if not body:
            return None
        try:
            print("[request.py-parse_JSON] {}".format(json.loads(body)))
            return json.loads(body)
        except Exception as e:
            print("[request.py-parse_JSON] Failed to parse {}!!!".format(e))
            return None



#^^====================================================================^^#
