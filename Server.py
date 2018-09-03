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
    group_time = None
    group_list = []

    def _set_headers(self, response=200):
        self.send_response(response)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
    
    def parse_path(self, path):
        if path == '/users' or path == '/users/':
            return 'all'
        elif '/users/query' in path:
            return ('user query', self.parse_query_parameters(path, '/users/query?'))

        elif '/users' in path:
            if '/groups' in path:
                return
            else:
                path = path.replace('/users/', '')
                query_fields = []
                query_fields.append((1, path))
                return ('user query', query_fields)

        elif path == '/groups' or path == '/groups/':
            return 'all groups'

        elif '/groups/query' in path:
            return ('group query', self.parse_query_parameters(path, '/groups/query?'))

        elif '/groups' in path:
            path = path.replace('/groups/', '')
            query_fields = []
            query_fields.append((1, path))
            return ('group query', query_fields)

    def parse_file(self, file=None):
        if file == 'passwd':
            current_time = os.stat(passwd_file).st_mtime
            if (S.passwd_time == None or current_time > S.passwd_time):
                self.parse_passwd()
                S.passwd_time = current_time
        elif file == 'group':
            current_time = os.stat(group_file).st_mtime
            if (S.group_time == None or current_time > S.group_time):
                self.parse_group()
                S.group_time = current_time

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

    def parse_group(self):
        f = open(group_file, 'r')
        lines = f.readlines()
        f.close()

        for line in lines:
            if '#' == line[0]:
                continue
            split = line.split(':')
            split.pop(1)
            if len(split[2]) > 0:                
                if split[2][-1] == '\n':
                    split[2] = split[2][0:len(split[2]) - 1]
                split[2] = str(split[2].split(','))
            else:
                split[2] = str([])
            S.group_list.append(split)
        return
    
    def parse_query_parameters(self, path, initial_query):
        # remove /users/query
        # will take out the initial ? as well
        query_type = 'passwd' if 'user' in path else 'group'

        path = path.replace(initial_query, '')
        # revert URL-Encoded slash to normal slash
        path = path.replace('%2F', '/')
        path = path.replace('%26', '&')
        query_fields = path.split('&')

        if query_type == 'passwd':
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
        else: # parsing the query parameters for group
            for index, field in enumerate(query_fields):
                field = field.split('=')
                if field[0] == 'name':
                    field[0] = 0
                elif field[0] == 'gid':
                    field[0] = 1
                elif field[0] == 'member':
                    field[0] = 2
                query_fields[index] = tuple(field)

        return query_fields

    def user_query(self, query_fields):
        # implement afterwards
        if len(query_fields) == 0:
            extract = S.passwd_list
        else:
            extract = []
            for row in S.passwd_list:
                flag = True
                for index, query in query_fields:
                    if row[index] != query:
                        flag = False
                        break
                if flag == True:
                    extract.append(row)

        layout = ['name: ', 'uid: ', 'gid: ', 'comment: ', 'home: ', 'shell: ']
        encoded_list = []
        for row in extract:
            result = []
            for index, elem in enumerate(row):
                result.append(layout[index] + elem)
            encoded_list.append(result)
        return encoded_list
    
    def group_query(self, query_fields):
        # implement afterwards
        if len(query_fields) == 0:
            extract = S.group_list
        else:
            extract = []
            for row in S.group_list:
                flag = True
                for index, query in query_fields:
                    if index == 0 or index == 1:
                        if row[index] != query:
                            flag = False
                            break
                    elif query not in row[index]: # member check for members
                        flag = False
                        break
                if flag == True:
                    extract.append(row)

        layout = ['name: ', 'gid: ', 'members: ']
        encoded_list = []
        for row in extract:
            result = []
            for index, elem in enumerate(row):
                result.append(layout[index] + elem)
            encoded_list.append(result)
        return encoded_list

    def do_GET(self):

        option = self.parse_path(self.path)
        encoded_list = None
        if option == 'all':
            self.parse_file('passwd')
            encoded_list = str(self.user_query([])).encode()
            self._set_headers(200)
            self.wfile.write(encoded_list)
        elif option[0] == 'user query':
            self.parse_file('passwd')
            query = self.user_query(option[1])
            if len(query) == 0:
                self._set_headers(response=404)
            else:
                self._set_headers()
                encoded_list = str(query).encode()
                self.wfile.write(encoded_list)
        elif option == 'all groups':
            self.parse_file('group')
            encoded_list = str(self.group_query([])).encode()
            self._set_headers(200)
            self.wfile.write(encoded_list)            
        elif option[0] == 'group query':
            self.parse_file('group')
            query = self.group_query(option[1])
            if len(query) == 0:
                self._set_headers(response=404)
            else:
                self._set_headers()
                encoded_list = str(query).encode()
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
