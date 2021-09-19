#  coding: utf-8 
import socketserver
import mimetypes
import pathlib
import os

# Copyright 2013 Jawad Hossain, Abram Hindle, Eddie Antonio Santos
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
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):
    baseDirectory = 'www'

    
    def handle(self):
        self.data = self.request.recv(1024).strip().decode('utf-8').split(' ')[0:2]

        if (len(self.data) == 2):
            # extract mehthod and path
            self.method = self.data[0]
            self.path = self.data[1]

            print (f"Got a request of: {self.method} {self.path}\n")
            self.updatePath()

            if (self.method == 'GET'):
                # Method accepted

                print(self.path)
                print(self.pathExists())

                if (self.pathSafe()):
                    # Check if path exists
                        if self.pathExists():
                            self.handleFileOpen()
                        elif ( pathlib.Path(self.path + '/').is_dir() ):
                            # Directory exists. Send 301 Moved Permanently and redirect
                            self.handleFileOpen(True)
                        else:
                            # Send 404 File Not Found
                            self.handleStatus404()
                else:
                    # Send 404 File Not Found
                    self.handleStatus404()


            else:
                # Send 405 Method Not Allowed
                self.handleStatus405()

    '''
        Make path absolute and add index.html if path ends in '/' 
    '''
    def updatePath(self):
        # add index.html if path ends in '/'
        if self.path and self.path[-1] == '/':
            self.path += 'index.html'

        self.path = f"{pathlib.Path().parent.resolve()}/{self.baseDirectory}{self.path}"

    '''
        Check if path exists
    '''
    def pathExists(self):
        file = pathlib.Path(self.path)

        return file.is_file()

    '''
        Check if paths is safe
        ref: https://security.openstack.org/guidelines/dg_using-file-paths.html
    '''
    def pathSafe(self):
        basedir = f"{pathlib.Path().parent.resolve()}/{self.baseDirectory}"
        return basedir == os.path.commonpath((basedir, self.path))

    '''
        If redirect not set send status 200 OK and resource
        ref: https://www.tutorialspoint.com/How-to-find-the-mime-type-of-a-file-in-Python
    '''
    def handleFileOpen(self, redirect=False):
        if (redirect):
            self.request.sendall(bytearray(f"HTTP/1.1 301 Moved Permanently\r\nLocation: {self.data[1] + '/'}",'utf-8'))
        else:
            try:
                # read file
                file = open(self.path)
                content = file.read()
                file.close()    

                # find mimetype
                mimeType = mimetypes.MimeTypes().guess_type(self.path)[0]
                self.request.sendall(bytearray(f"HTTP/1.1 200 OK\r\nContent-Type: {mimeType}\r\n\r\n{content}",'utf-8'))
            except:
                self.request.sendall(bytearray(f"HTTP/1.1 500 Internal Server Error\n\n",'utf-8'))

    
    '''
        Send status 404 Not Found
    '''
    def handleStatus404(self):
        self.request.sendall(bytearray("HTTP/1.1 404 NOT FOUND\n\nFile Not Found",'utf-8'))
    
    '''
        Send status 405 Method Not Allowed
    '''
    def handleStatus405(self):
        self.request.sendall(bytearray("HTTP/1.1 405 Method Not Allowed\n\nMethod Not Allowed",'utf-8'))


if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
