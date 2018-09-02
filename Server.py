#!/usr/bin/env python3
"""
Very simple HTTP server in python.
Usage::
    ./Server.py [<port>]
Send a GET request::
    curl http://localhost
"""
from http.server import BaseHTTPRequestHandler, HTTPServer
import os.path
import time

print("Enter passwd_file:")
passwd_file = input()
if passwd_file == '':
    passwd_file = '/etc/passwd'
print("Enter group_file:")
group_file = input()
if group_file == '':
    group_file = '/etc/group'

class S(BaseHTTPRequestHandler):

    passwd_time = None
    passwd_list = []
    

    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def passwd(self):
        current_time = os.stat(passwd_file).st_mtime
        if (S.passwd_time == None or current_time > S.passwd_time):
            self.parse_passwd()
            S.passwd_time = current_time

    def parse_passwd(self):

        f = open(passwd_file, 'r')
        lines = f.readlines()
        f.close()

        for line in lines:
            if '#' == line[0]:
                continue
            split = line.split(':')
            split.pop(1)
            if split[5][-1] == '\n':
                split[5] = split[5][0:len(split[5]) - 1]
            S.passwd_list.append(split)
        return

    def parse_path(self, path):
        if path == '/users' or path == '/users/':
            return 'all'
        elif '/users/query' in path:
            return ('user query', self.parse_query_parameters(path, '/users/query?'))

        return

    def parse_query_parameters(self, path, initial_query):
        # remove /users/query
        # will take out the initial ? as well
        path = path.replace(initial_query, '')
        # revert URL-Encoded slash to normal slash
        path = path.replace('%2F', '/')
        query_fields = path.split('&')
        for index, field in enumerate(query_fields):
            field = field.split('=')
            if field[0] == 'name':
                field[0] = 0
            elif field[0] == 'uid':
                field[0] = 1
            elif field[0] == 'gid':
                field[0] = 2
            elif field[0] == 'comment':
                field[0] = 3
            elif field[0] == 'home':
                field[0] = 4
            elif field[0] == 'shell':
                field[0] = 5
            query_fields[index] = tuple(field)

        return query_fields

    def user_query(self, query_fields):
        # implement afterwards
        if len(query_fields) == 0:
            passwd_list_extract = S.passwd_list
        else:
            passwd_list_extract = []
            for row in S.passwd_list:
                flag = True
                for index, query in query_fields:
                    if row[index] != query:
                        flag = False
                        break
                if flag == True:
                    passwd_list_extract.append(row)                   

        layout = ['name: ', 'uid: ', 'gid: ', 'comment: ', 'home: ', 'shell: ']
        encoded_list = []
        for row in passwd_list_extract:
            result = []
            for index, elem in enumerate(row):
                result.append(layout[index] + elem)
            encoded_list.append(result)
        return encoded_list

    def do_GET(self):

        option = self.parse_path(self.path)

        encoded_list = None
        if option == 'all':
            self.passwd()
            encoded_list = str(self.user_query([])).encode()
        elif option[0] == 'user query':
            self.passwd()
            encoded_list = str(self.user_query(option[1])).encode()

        self._set_headers()
        self.wfile.write(encoded_list)


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
