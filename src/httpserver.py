'''
Created on 7. okt. 2011

@author: Eier
'''
import cgi
import base64;
from BaseHTTPServer import BaseHTTPRequestHandler
from BaseHTTPServer import HTTPServer
from os import curdir, path


class GridCell():
    x = 0
    y = 0
    v = 0
    def __init__(self,x,y,v):
        self.x = x
        self.y = y
        self.v = v #value

class Grid():
    sizeX = 0
    sizeY = 0
    
    def __init__(self,sizeX,sizeY,values1d):
        self.sizeX = sizeX
        self.sizeY = sizeY
        
        v = 0
        self.cells = []
        for x in range(sizeX):
            self.cells.append([])
            for y in range(sizeY):
#                print x,sizeX,y,sizeY,v,len(values1d)
                self.cells[x].append(GridCell(x, y, ord(values1d[v])));
                v += 1
class HttpRequestHandlerWrapper:
    
    def __init__(self):
        HttpRequestHandlerWrapper.old_fire = None
        server = HTTPServer(('127.0.0.1', 8000), self.HttpRequestHandler)
        server.serve_forever()
        print "Server started!"

    class HttpRequestHandler(BaseHTTPRequestHandler):
        
        def do_GET(self):
            try:
                print 'Request: ' + self.path
                
                if self.path == '/':
                    fpath = path.abspath(curdir + '/../gui/simulation.html')
                else:
                    fpath = path.abspath(curdir + '/../gui' + self.path)
                
                print 'Path: '+fpath;
                
                f = open(fpath,'rb')
                
                if fpath.endswith('.css'):
                    mime = 'text/css'
                elif fpath.endswith('.html'):
                    mime = 'text/html'
                elif fpath.endswith('.gif'):
                    mime = 'image/gif'  
                elif fpath.endswith('.png'):
                    mime = 'image/png'
                elif fpath.endswith('.jpg'):
                    mime = 'image/jpeg'
                elif fpath.endswith('.js'):
                    mime = 'text/javascript'
                else:
                    mime = 'text/plain'
                    
                self.send_response(200)
                self.send_header('Content-type',mime)
                self.end_headers()
    
                self.wfile.write(f.read())
                f.close()
                return
            except IOError:
                self.send_error(404,'File Not Found: %s' % fpath)
         
        def do_POST(self):
            try:
                ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    postvars = cgi.parse_multipart(self.rfile, pdict)
                elif ctype == 'application/x-www-form-urlencoded':
                    length = int(self.headers.getheader('content-length'))
                    postvars = cgi.parse_qs(self.rfile.read(length), keep_blank_values=1)
                else:
                    postvars = {}
            except IOError:
                self.send_error(404,'File not found!')
                
            self.send_response(200)
            self.send_header('Content-type','text/plain')
            self.end_headers()
            cells = []
            for key,value in postvars.items():
                if key == 'sizeX':
                    sizeX = int(value[0])
                elif key == 'sizeY':
                    sizeY = int(value[0])
                elif key=='cells':
                    for char in base64.b64decode(value[0]):
                        cells.append(char)
            
            grid = Grid(sizeX,sizeY,cells)

            
            from analyze.Analyzer import GPR_d
            from analyze.Analyzer import GPR_Controller
            import time
            
            
            t = time.time()
            gpr_controller = GPR_Controller(grid,HttpRequestHandlerWrapper.old_fire)
            grid = gpr_controller.grid
            
            
            
            large_string = gpr_controller.large_string
            HttpRequestHandlerWrapper.old_fire = gpr_controller.old_fire
    #        large_string = ""
    #        for cell in grid.cells:
    #            for row in cell:
    #                large_string += chr(row.v)
            
            
            self.wfile.write(base64.b64encode(large_string))
    
            
            t2 = time.time() -t
            print t2
            
            
            
            return
    
if __name__ == '__main__':
    HttpRequestHandlerWrapper()
    pass