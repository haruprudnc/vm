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
daemon.httpadapter
~~~~~~~~~~~~~~~~~

This module provides a http adapter object to manage and persist 
http settings (headers, bodies). The adapter supports both
raw URL paths and RESTful route definitions, and integrates with
Request and Response objects to handle client-server communication.
"""

from .request import Request
from .response import Response
from .dictionary import CaseInsensitiveDict
#^^--------------------------------------------------------------------^^#
import json
#^^====================================================================^^#

VALID_USERS = {
    "admin": "0",
    "admin1": "1",
    "admin2": "2",
    "admin3": "3"
}
class HttpAdapter:
    """
    A mutable :class:`HTTP adapter <HTTP adapter>` for managing client connections
    and routing requests.

    The `HttpAdapter` class encapsulates the logic for receiving HTTP requests,
    dispatching them to appropriate route handlers, and constructing responses.
    It supports RESTful routing via hooks and integrates with :class:`Request <Request>` 
    and :class:`Response <Response>` objects for full request lifecycle management.

    Attributes:
        ip (str): IP address of the client.
        port (int): Port number of the client.
        conn (socket): Active socket connection.
        connaddr (tuple): Address of the connected client.
        routes (dict): Mapping of route paths to handler functions.
        request (Request): Request object for parsing incoming data.
        response (Response): Response object for building and sending replies.
    """

    __attrs__ = [
        "ip",
        "port",
        "conn",
        "connaddr",
        "routes",
        "request",
        "response",
    ]

    def __init__(self, ip, port, conn, connaddr, routes):
        """
        Initialize a new HttpAdapter instance.

        :param ip (str): IP address of the client.
        :param port (int): Port number of the client.
        :param conn (socket): Active socket connection.
        :param connaddr (tuple): Address of the connected client.
        :param routes (dict): Mapping of route paths to handler functions.
        """

        #: IP address.
        self.ip = ip
        #: Port.
        self.port = port
        #: Connection
        self.conn = conn
        #: Conndection address
        self.connaddr = connaddr
        #: Routes
        self.routes = routes
        #: Request
        self.request = Request()
        #: Response
        self.response = Response()

    def handle_client(self, conn, addr, routes):
        """
        Handle an incoming client connection.

        This method reads the request from the socket, prepares the request object,
        invokes the appropriate route handler if available, builds the response,
        and sends it back to the client.

        :param conn (socket): The client socket connection.
        :param addr (tuple): The client's address.
        :param routes (dict): The route mapping for dispatching requests.
        """

        # Connection handler.
        self.conn = conn        
        # Connection address.
        self.connaddr = addr
        # Request handler
        req = self.request
        # Response handler
        resp = self.response

        # Handle the request
        msg = conn.recv(1024).decode()
        req.prepare(msg, routes)

        # Handle authentication for POST /login (Task 1 - form-based only)
        # Only handle form-based login, JSON requests go to WeApRous routes (Tracker Server)
        if req.method == "POST" and req.path == "/login":
            content_type = req.headers.get('content-type', '').lower()
            
            # Only handle form-based login (Task 1), skip JSON requests (Tracker Server)
            if 'application/x-www-form-urlencoded' in content_type:
                print("[HttpAdapter] Handling form-based login request (Task 1)")
                # Parse form data from request body
                body_data = self._parse_form_data(msg)
                username = body_data.get('username', '')
                password = body_data.get('password', '')
                correct_password = VALID_USERS.get(username)
                # Validate credentials
                if correct_password and correct_password == password:
                    print("[HttpAdapter] Login successful")
                    # Set authentication cookie and serve index page
                    resp.headers['Set-Cookie'] = 'auth=true'
                    req.path = '/index.html'  # Redirect to index page
                else:
                    print("[HttpAdapter] Login failed - invalid credentials")
                    # Return 401 Unauthorized
                    resp.status_code = 401
                    resp.reason = "Unauthorized"
                    resp._content = b"<html><body><h1>401 Unauthorized</h1><p>Invalid credentials</p></body></html>"
                    resp.headers['Content-Type'] = 'text/html'
                    response = resp.build_response_header(req) + resp._content
                    conn.sendall(response)
                    conn.close()
                    return
            # If JSON request, skip Task 1 logic and let WeApRous routes handle it (Tracker Server)
            elif 'application/json' in content_type:
                print("[HttpAdapter] JSON login request detected - passing to WeApRous routes (Tracker Server)")

        # Handle cookie-based access control for GET /
        if req.method == "GET" and (req.path == "/" or req.path == "/index.html"):
            print("[HttpAdapter] Checking authentication for protected resource")
            # Check for auth cookie
            cookie_header = req.headers.get('cookie', '')
            if 'auth=true' not in cookie_header:
                print("[HttpAdapter] Access denied - no valid auth cookie")
                # Return 401 Unauthorized
                resp.status_code = 401
                resp.reason = "Unauthorized"
                resp._content = b"<html><body><h1>401 Unauthorized</h1><p>Please login first</p><a href='/login.html'>Login</a></body></html>"
                resp.headers['Content-Type'] = 'text/html'
                response = resp.build_response_header(req) + resp._content
                conn.sendall(response)
                conn.close()
                return
            else:
                print("[HttpAdapter] Access granted - valid auth cookie found")

        # Handle request hook
        if req.hook:
            print("[HttpAdapter] hook in route-path METHOD {} PATH {}".format(req.hook._route_methods, req.hook._route_path))
            # req.hook(headers = "bksysnet", body = "get in touch")
            req.hook(headers = req.headers, body = req.body)
            #
            # TODO: handle for App hook here
            #
        #^^--------------------------------------------------------------------^^#

            if not req.isJSON():
                # Exception: Allow GET /get-list to go through to handler (WeApRous route returns JSON)
                # Keep original logic for other non-JSON requests
                if req.method == "GET" and req.path == "/get-list":
                    print("[HttpAdapter] Exception: GET /get-list - allowing handler execution despite non-JSON request")
                    # Don't return here, continue to handler execution below
                else:
                    print("\n is not JSON or method GET\n")
                    # Build response
                    response = resp.build_response(req)

                    #print(response)
                    conn.sendall(response)
                    conn.close()
                    return
        #^^====================================================================^^#
            
            try:
                # Execute user-defined route handler

                result = req.hook(headers=req.headers, body=req.json_data or req.body)
                print("[httpadapter.py] result \n{}".format(result))
                print("[httpadapter.py] json data \n{}".format(req.json_data))
                print("[httpadapter.py] result isinstance \n{}".format(isinstance(req.json_data, dict)))
                # Determine response type
                if isinstance(result, dict):
                    resp._content = json.dumps(result).encode('utf-8')
                    resp.headers['Content-Type'] = 'application/json'
                elif isinstance(result, str):
                    resp._content = result.encode('utf-8')
                    resp.headers['Content-Type'] = 'text/html'
                else:
                    # default to bytes or fallback
                    resp._content = str(result).encode('utf-8')
                    resp.headers['Content-Type'] = 'text/plain'

                resp.status_code = 200
                resp.reason = "OK"

                # Build final response packet
                response = resp.build_response_header(req) + resp._content
                conn.sendall(response)
                print("[HttpAdapter] Hook executed successfully.")
                conn.close()
                return
            except Exception as e:
                print(f"[HttpAdapter] Hook execution failed: {e}")
                resp.status_code = 500
                resp.reason = "Internal Server Error"
                resp._content = b"<h1>500 Internal Server Error</h1>"
                resp.headers['Content-Type'] = 'text/html'
                response = resp.build_response_header(req) + resp._content
                conn.sendall(response)
                conn.close()
                return

        # Build response
        response = resp.build_response(req)

        #print(response)
        conn.sendall(response)
        conn.close()

    @property
    def extract_cookies(self, req, resp):
        """
        Build cookies from the :class:`Request <Request>` headers.

        :param req:(Request) The :class:`Request <Request>` object.
        :param resp: (Response) The res:class:`Response <Response>` object.
        :rtype: cookies - A dictionary of cookie key-value pairs.
        """
        cookies = {}
        for header in headers:
            if header.startswith("Cookie:"):
                cookie_str = header.split(":", 1)[1].strip()
                for pair in cookie_str.split(";"):
                    key, value = pair.strip().split("=")
                    cookies[key] = value
        return cookies

    def build_response(self, req, resp):
        """Builds a :class:`Response <Response>` object 

        :param req: The :class:`Request <Request>` used to generate the response.
        :param resp: The  response object.
        :rtype: Response
        """
        response = Response()

        # Set encoding.
        response.encoding = get_encoding_from_headers(response.headers)
        response.raw = resp
        response.reason = response.raw.reason

        if isinstance(req.url, bytes):
            response.url = req.url.decode("utf-8")
        else:
            response.url = req.url

        # Add new cookies from the server.
        response.cookies = extract_cookies(req)

        # Give the Response some context.
        response.request = req
        response.connection = self

        return response

    # def get_connection(self, url, proxies=None):
        # """Returns a url connection for the given URL. 

        # :param url: The URL to connect to.
        # :param proxies: (optional) A Requests-style dictionary of proxies used on this request.
        # :rtype: int
        # """

        # proxy = select_proxy(url, proxies)

        # if proxy:
            # proxy = prepend_scheme_if_needed(proxy, "http")
            # proxy_url = parse_url(proxy)
            # if not proxy_url.host:
                # raise InvalidProxyURL(
                    # "Please check proxy URL. It is malformed "
                    # "and could be missing the host."
                # )
            # proxy_manager = self.proxy_manager_for(proxy)
            # conn = proxy_manager.connection_from_url(url)
        # else:
            # # Only scheme should be lower case
            # parsed = urlparse(url)
            # url = parsed.geturl()
            # conn = self.poolmanager.connection_from_url(url)

        # return conn


    def _parse_form_data(self, raw_message):
        """
        Parse form data from POST request body.
        
        :param raw_message: Raw HTTP request message string.
        :rtype: dict: Dictionary of form field names and values.
        """
        form_data = {}
        
        try:
            lines = raw_message.split('\r\n')
            
            # Find the empty line that separates headers from body
            body_start = -1
            for i, line in enumerate(lines):
                if line == '':
                    body_start = i + 1
                    break
            
            if body_start > 0 and body_start < len(lines):
                # Parse the body as form data
                body = '\r\n'.join(lines[body_start:])
                if body:
                    pairs = body.split('&')
                    for pair in pairs:
                        if '=' in pair:
                            key, value = pair.split('=', 1)
                            form_data[key] = value
        except Exception as e:
            print("[HttpAdapter] Error parsing form data: {}".format(e))
            
        return form_data

    def add_headers(self, request):
        """
        Add headers to the request.

        This method is intended to be overridden by subclasses to inject
        custom headers. It does nothing by default.

        
        :param request: :class:`Request <Request>` to add headers to.
        """
        pass

    def build_proxy_headers(self, proxy):
        """Returns a dictionary of the headers to add to any request sent
        through a proxy. 

        :class:`HttpAdapter <HttpAdapter>`.

        :param proxy: The url of the proxy being used for this request.
        :rtype: dict
        """
        headers = {}
        #
        # TODO: build your authentication here
        #       username, password =...
        # we provide dummy auth here
        #
        username, password = ("user1", "password")

        if username:
            headers["Proxy-Authorization"] = (username, password)

        return headers

#^^====================================================================^^#

#^^====================================================================^^#