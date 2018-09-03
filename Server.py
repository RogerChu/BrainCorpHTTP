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


class S(BaseHTTPRequestHandler):

    passwd_time = None  # stores the time of the /etc/passwd file or user specified passwd
    passwd_list = []  # list that stores all the info for the passwd file
    group_time = None  # stores the time of the /etc/group file or user specified group
    group_list = []  # list that stores all the info for the group

    # function that sets the basic headers for the http response
    def _set_headers(self, response=200):
        self.send_response(response)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    # responsible for parsing the GET request path
    def parse_path(self, path):
        # gets all users in passwd
        if path == '/users' or path == '/users/':
            return 'all'
        # gets users in passwd with a specific query
        elif '/users/query' in path:
            return ('user query', self.parse_query_parameters(path, '/users/query?'))

        elif '/users' in path:
            # checks for uid in passwd and finds the associated name in members of group
            if '/groups' in path:
                path = path.replace('/users/', '')
                path = path.replace('/groups', '')
                query_fields = []
                query_fields.append((1, path))
                return ('user-group query', query_fields)
            else:
                # user query with specified uid to find in passwd
                path = path.replace('/users/', '')
                query_fields = []
                query_fields.append((1, path))
                return ('user query', query_fields)

        # gets all groups in /etc/group
        elif path == '/groups' or path == '/groups/':
            return 'all groups'

        # gets groups with query
        elif '/groups/query' in path:
            return ('group query', self.parse_query_parameters(path, '/groups/query?'))

        # group query with specified gid
        elif '/groups' in path:
            path = path.replace('/groups/', '')
            query_fields = []
            query_fields.append((1, path))
            return ('group query', query_fields)

    # parses the /passwd or the /group file accoirdingly
    # only when the corresponding files havent been previously parsed 
    # or files have been updated when the next GET request comes, it will update then.
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

    # parses the passwd file and accounts for end of line character
    def parse_passwd(self):
        f = open(passwd_file, 'r')
        lines = f.readlines()
        f.close()

        for line in lines:
            if '#' == line[0]:
                continue
            split = line.split(':')
            split.pop(1) # removes password field
            if split[5][-1] == '\n':
                split[5] = split[5][0:len(split[5]) - 1]
            S.passwd_list.append(split)
        return

    # same as parse_passwd but for the group file
    def parse_group(self):
        f = open(group_file, 'r')
        lines = f.readlines()
        f.close()

        for line in lines:
            if '#' == line[0]:
                continue
            split = line.split(':')
            split.pop(1) # removes the password field
            if len(split[2]) > 0:
                if split[2][-1] == '\n':
                    split[2] = split[2][0:len(split[2]) - 1]
                split[2] = str(split[2].split(','))
            else:
                split[2] = str([])
            S.group_list.append(split)
        return

    # When a query is provided, it parses the parameters
    # Point of Note: '/' = '%2F' and '&' = '%26' in URL-Encoding
    # Also matches Query Fields with associated indices in List for Instant Look-Up
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
        else:  # parsing the query parameters for group
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

    # with the query fields, extracts out the requried user query and formats
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

    # with the query fields, extracts out the requried group query and formats
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
                    elif query not in row[index]:  # member check for members
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

    # Since only GET needed to be supported, hence this function
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
        elif option[0] == 'user-group query':
            self.parse_file('passwd')
            self.parse_file('group')
            not_encoded_list = self.user_query(option[1])
            if len(not_encoded_list) == 0:
                self._set_headers(response=404)
            else:
                # this gets the name associated with uid
                name = not_encoded_list[0][0].split(':')[1].lstrip()
                query_fields = []
                query_fields.append((2, name))
                query = self.group_query(query_fields)
                if len(query) == 0:
                    self._set_headers(response=404)
                else:
                    self._set_headers()
                    encoded_list = str(query).encode()
                    self.wfile.write(encoded_list)


print("Enter passwd_file:")
passwd_file = input()
if passwd_file == '':
    passwd_file = '/etc/passwd'
print("Enter group_file:")
group_file = input()
if group_file == '':
    group_file = '/etc/group'


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
