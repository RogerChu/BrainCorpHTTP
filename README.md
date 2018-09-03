# BrainCorpHTTP


This is my implementation of the Passwd as Service Challenge. 

This implementation works using Python3.

In order to run the server: 

Type: **python3 Server.py** 


This will initiate two inputs:

**Enter passwd_file:**
and 
**Enter group_file:**

If you simply want to use the default **/etc/passwd** and **/etc/group** press enter without typing anything. 
If you have a particular files in mind: type the file names accoringly. An exception will be raised if the
file does not exist.

As per the requirement, only **GET** is supported.


### Testing

curl was used in order to send GET requests to the Server.

Inside the specifications, were couple examples for each of the requests.
In order to try out the sample set: use passwd.txt and group.txt files provided in the directory,
when starting the server.

#### GET /users
Example:
curl -v http://localhost/users

#### GET /users/query

Key thing to note for query:
'/' is represented as '%2F'
and 
'&' is represented as '%26'

as seen from: http://www.blooberry.com/indexdot/html/topics/urlencoding.htm


Example:

curl -v http://localhost/users/query?shell=%2Fbin%2Ffalse%26name=dwoodlins




#### GET /users/uid

Example: 

curl -v http://localhost/users/1001



#### GET /users/uid/groups

Example: 

curl -v http://localhost/users/1001/groups

This will return a 404 error for the sample set. 
Based on the example provided in the Specification, 
dwoodlins has a uid of 1001 but the gid = 1002 is shown in sample output which created some confusion.
However, for curl -v http://localhost/users/0/groups should work for default /etc/passwd and /etc/group
and for others appropriately. 

  
#### GET /groups

Example: 

curl -v http://localhost/groups


#### GET /groups/query

Same thing to remember as GET /users/query with '/' and '&'

Example: 

curl -v http://localhost/groups/query?member=_analyticsd%26member=_networkd

#### GET /groups/gid

Example:

curl -v http://localhost/groups/1002



### Assumption

The test files will be properly formatted as the default /etc/passwd and /etc/group










