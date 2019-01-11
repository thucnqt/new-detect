from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import SocketServer
import json
import cgi
import os
from multiprocessing import Process
import sqlalchemy as db
class Server(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
    def do_HEAD(self):
        self._set_headers()
        
    # GET sends back a Hello world message
    def do_GET(self):
        self._set_headers()
        self.wfile.write(json.dumps({'hello': 'world', 'received': 'ok'}))
        
    # POST echoes the message adding a JSON field
    def do_POST(self):
        ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
        
        # refuse to receive non-json content
        if ctype != 'application/json':
            self.send_response(400)
            self.end_headers()
            return
            
        # read the message and convert it into a python dictionary
        length = int(self.headers.getheader('content-length'))
        message = json.loads(self.rfile.read(length))
        print message
        database = 'object_detection'
        table = 'detect'
        user = 'root'
        password = 'anhthuc1996'
        host = '127.0.0.1'
        port = '3306'
        connect_db = 'mysql://'+  user + ':' + password + '@'+ host + ':' + port + '/' + database 
        #connect_db = MySQLdb.connect(host="localhost", user = "root", passwd = "anhthuc1996", db = "object_detection", use_unicode=True, charset="utf8")
        #print connect_db        
        engine = db.create_engine(connect_db)
        connection = engine.connect()
        metadata = db.MetaData()
        table = db.Table(table, metadata, autoload=True, autoload_with=engine)
        pol = Process(target= insert_data, args=(connection, message, table))
        pol.start()
        pol.join()
           
        # add a property to the object, just to mess with data

        #with open("logs.txt", "a+") as file: # wrrite to file
         #   json.dump(message, file)
         #   file.write("\r\n")
        #file.close()
        # send the message back
        self._set_headers()
       # self.wfile.write(json.dumps(message))

def insert_data(connection, data, table):
    query = db.insert(table).values(data)
    connection.execute(query)
    print "Insert success"

def run(server_class=HTTPServer, handler_class=Server, port=8008):
    #### Database 
    
    #####**********************************######
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    
    print 'Starting httpd on port %d...' % port
    httpd.serve_forever()
    
if __name__ == "__main__":
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()   
