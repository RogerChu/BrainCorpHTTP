#!/usr/bin/env python3
"""
Very simple HTTP server in python.
Usage::
    ./Server.py [<port>]
Send a GET request::
    curl http://localhost
"""
from http.server import BaseHTTPRequestHandler, HTTPServer

class S(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        self._set_headers()
        print(self.path)
        l = []
        l.append(10)
        l.append(20)
        l = str(l).encode()
        self.wfile.write(l)

        # self.wfile.write("<html><body><h1>hi!</h1></body></html>".encode())
        
        
def run(server_class=HTTPServer, handler_class=S, port=80):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print('Starting httpd on port')
    httpd.serve_forever()

if __name__ == "__main__":
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()