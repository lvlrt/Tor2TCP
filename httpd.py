import time
import BaseHTTPServer
import base64
import socket
import httplib

#PARSER
import argparse

parser = argparse.ArgumentParser(description='Server side program to work over http proxies; \nFor tunneling TCP you need the client: \nURL: "http://<server-url>/randomstring(for anti-caching)/CLIENT(EXE)" returns the client in a download; \nURL: "http://<server-url>/randomstring(anti-caching)/FORWARD/<port>/<path>/" forwards http request to another server on the local machine') 
parser.add_argument('-p','--port', help='Port to run the http server on ex. 8000', required=True)
parser.add_argument('-t','--targetport', help='TCP port to forward to on localhost ex. 2022', required=True)
args = vars(parser.parse_args())

HOST_NAME = '0.0.0.0' #LISTEN TO ALL
PORT_NUMBER = int(args["port"])

##TCP CLIENT 
#TODO PARS
TCP_IP = '127.0.0.1'
TCP_PORT = int(args["targetport"])
BUFFER_SIZE = 1024*50 #2 is ook goed#SPEED???? *50

ID_dict=dict()

class MyHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_HEAD(s):
        s.send_response(200)
        s.send_header("Content-type", "text/html")
        s.end_headers()
    def do_GET(s): #IF MESSAGE, THIS WILL TRIGGER, but what if multiple responses,, loop until buffersize?:w
	print "GET REQUEST"
	splitted_path = s.path.split("/",4)
	#DIFFERENT CASES
	print splitted_path
	if len(splitted_path) > 2:
		if splitted_path[2] == "ID" and len(splitted_path) > 3: #A PACKET WITH IDENTIFIER
			#IF NEW ID
			#TODO IDS en connections in DIC
			if splitted_path[3] not in ID_dict:
				print "created connection"
				ID_dict[splitted_path[3]] = "" #add obecht here later 
				global tcpsocket
				tcpsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				tcpsocket.connect((TCP_IP, TCP_PORT))
			message = ""
			try: #if base64 command fails
				#if there is a message present to send
				if len(splitted_path[4]) > 0:
					print "received and send"
					message=base64.b64decode(splitted_path[4]) #this contains a base64 string in url
					tcpsocket.send(message) #send to tcp server
			except:
				pass
			response= ""
			tcpsocket.settimeout(0.6)
			try:
				response = tcpsocket.recv(BUFFER_SIZE) #return
				print "Got back response"
			except:
				pass
			#response = message
			if response != "":
				encoded = base64.b64encode(response)
			else:
				encoded = ""
			#Respond to a GET request
        		s.send_response(200)
        		s.send_header("Content-type", "text/html")
        		s.end_headers()
        		s.wfile.write("<html><head><title>"+encoded+"</title></head>")#REPSONSE here
        		s.wfile.write("<body><p></p>")
        		s.wfile.write("</body></html>")
		elif splitted_path[2] == "CLIENT": #return the newest client (from this folder,TODO if not found? -> use raw github??
			#URL: /randomstring/CLIENT -> returns the client to do tcp forwarding
        		s.send_response(200)
        		s.send_header("content-type", "application/octet-stream")
        		s.end_headers()
			f = open('tcphttp.py', 'r')
        		s.wfile.write(f.read())#repsonse here
		elif splitted_path[2] == "CLIENTEXE": #return the newest client (from this folder,TODO if not found? -> use raw github??
			#URL: /randomstring/CLIENT -> returns the client to do tcp forwarding
        		s.send_response(200)
        		s.send_header("content-type", "application/octet-stream")
        		s.end_headers()
			f = open('tcphttp.exe', 'r')
        		s.wfile.write(f.read())#repsonse here
		elif splitted_path[2] == "FORWARD": #forward to another port http server request
        		#URL: /randomstring/FORWARD/<PORT>/<PATH>
			if len(splitted_path) > 4:
				http_conn = httplib.HTTPConnection('127.0.0.1',splitted_path[3])
				
				#CHECK IF there are enoug arguments TODO
            			#SEND HTTP REQUEST BACK
            			http_conn.request("GET", "/"+splitted_path[4])
            			#RETRIEVE DATA
            			r1 = http_conn.getresponse()
            			data1 = r1.read()#data1 is the full html page
				

				s.send_response(200)
				for header in r1.getheaders():
					s.send_header(header[0], header[1])
        			s.end_headers()
        			s.wfile.write(data1)#repsonse here
if __name__ == '__main__':
    server_class = BaseHTTPServer.HTTPServer
    httpd = server_class((HOST_NAME, PORT_NUMBER), MyHandler)
    print time.asctime(), "Server Starts - %s:%s" % (HOST_NAME, PORT_NUMBER)
    try:
                httpd.serve_forever()
    except KeyboardInterrupt:
                pass
    httpd.server_close()
    print time.asctime(), "Server Stops - %s:%s" % (HOST_NAME, PORT_NUMBER)


#for tcp
tcpsocket.close()
