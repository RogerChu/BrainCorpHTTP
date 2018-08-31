#!/usr/bin/env python3
"""
Very simple HTTP server in python.
Usage::
    ./Server.py [<port>]
Send a GET request::
    curl http://localhost
"""
from http.server import BaseHTTPRequestHandler, HTTPServer
import os.path, time



class S(BaseHTTPRequestHandler):

    passwd_time = None
    passwd_list = []



    
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
    
    def passwd(self):
        current_time = os.stat('/etc/passwd').st_mtime
        if (S.passwd_time == None or current_time > S.passwd_time):
            self.parse_passwd()
            S.passwd_time = current_time
            
    def parse_passwd(self):

        f = open('/etc/passwd', 'r')
        lines = f.readlines()
        f.close()

        for line in lines:
            if '#' == line[0]:
                continue
            split = line.split(':')  
            split[6] = split[6][0:len(split[6]) - 1]
            S.passwd_list.append(split)
        return

    def parse_path(self, path):
        
        if path == '/users':
            return 'all'

        return

    def user_query(self, parameters):
        #implement afterwards
        for param in parameters:
            continue
        
        
        


        return

    def do_GET(self):

        option = self.parse_path(self.path)

        if option == 'all':
            self.passwd()
            self.user_query([])

        encoded_list = str(S.passwd_list).encode()
        self._set_headers()
        self.wfile.write(encoded_list)



        # l = []
        # l.append(10)
        # l.append(20)
        # l = str(l).encode()
        # self.wfile.write(l)

        # self.wfile.write("<html><body><h1>hi!</h1></body></html>".encode())
        
        
def run(server_class=HTTPServer, handler_class=S, port=80):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print('Starting httpd on port: ' + str(port))
    httpd.serve_forever()

if __name__ == "__main__":
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()