#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it
import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

    def __str__(self):
        return f"{self.code}\r\n{self.body}"

class HTTPClient(object):
    #def get_host_port(self,url):

    def __init__(self):
        self.protocol = 'HTTP/1.1'

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(1)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        return None

    def get_headers(self,data):
        return None

    def get_body(self, data):
        return None
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:

            # Not sure how to know exactly when the server is done responding. But for now using timeouts.
            try:
                part = sock.recv(1024)
            except socket.timeout as e:
                part = b''

            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def parse_raw_response(self, response):
        """
        Parses a raw string response from a server
        :param response:
        :return: HTTPResponse
        """
        headers, body = response.split('\r\n\r\n', 1)

        headers = headers.split('\r\n')
        # Parse out the response code
        response_header = re.match(r'^HTTP/([0-9.]+ ([0-9]+) ([A-Z]+))', headers[0])
        response_http_ver = response_header.group(1)
        response_code = int(response_header.group(2))
        response_code_desc = response_header.group(3)

        return HTTPResponse(response_code, body)

    def request(self, url, method, args=None):
        """
        Handles connecting to a resource and passing the request. Returns the response as a raw string.
        :param url: string, the url to request to
        :return: string|false
        """
        port = 80
        url_parts = urllib.parse.urlparse(url, 'http')
        host = url_parts.netloc
        # Check for a specific port passed in
        host_parts = host.split(':', 1)
        if len(host_parts) > 1:
            host, port = host_parts
            port = int(port)


        request = f"{method} {url_parts.path or '/'} {self.protocol}\r\n"

        # Calculate body based on arguments
        body = ''
        post_args = []
        if(args is not None):
            body += urllib.parse.urlencode(args)
        # for arg in (args or {}).keys():
        #     post_args.append(f'{arg}={args[arg]}')
        # body += '&'.join(post_args)

        # Add headers
        headers = {
            "Accept": "*/*",
            "Host": host,
            "Content-Length": str(len(body))
        }
        for header in headers.keys():
            request += f"{header}: {headers[header]}\r\n"
        # Separate headers from body
        request += '\r\n'
        request += body

        #  Get the response from the server
        self.connect(host, port)
        self.sendall(request)
        result = self.recvall(self.socket)
        self.close()

        return result


    def GET(self, url, args=None):
        code = 500
        body = ""

        try:
            response = self.request(url, 'GET')
            # Parse the response
            response = self.parse_raw_response(response)
        except Exception as e:
            # Something failed, respond with an error code
            # print(e)
            return HTTPResponse(code, body)



        return response

    def POST(self, url, args=None):
        code = 500
        body = ""
        try:
            response = self.request(url, 'POST', args)
            # Parse the response
            response = self.parse_raw_response(response)
        except:
            return HTTPResponse(code, body)

        return response

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
