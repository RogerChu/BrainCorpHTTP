import httplib
import sys

#  get the http server ip

http_server = sys.argv[1]

connection = httplib.HTTPConnection(http_server)

while True:
    command = raw_input('input command (ex. GET index.html): ')
    command = command.split()

    if command[0] == 'exit': # type exit to end it
        break
    
    connection.request(command[0], command[1])

    response = connection.getresponse()

    print(response.status, response.reason)  
    data_received = response.read()  
    print(data_received) 

connection.close()

    