import BaseHTTPServer
import sys
import settings
import pickle
import HTML
from ConfigParser import ConfigParser
from threading import Thread

class SampleHttpWebServerHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_HEAD(self):
        """
        Response Handling
        """
        self.send_response(200)
        self.send_header("Content-type", "text/html")        
        self.end_headers()

    def do_GET(self):
        """
        Respond to a GET request.
        """
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

        html_head  = """<html><head><title>Website Monitor Status</title>
        		<meta http-equiv="refresh" content="5">
                <script type="text/javascript">
                </script>
                </head>
               """
        body_text = ""
        data = dict()
        with open(settings.storage_db_file, 'rb') as handle:
    		data = pickle.load(handle)
        
        resultColors = {'UP':'lime', 'DOWN':'red'}
        string = ''
        t = HTML.Table(header_row=['TIME', 'Web Page URL', 'STATUS', 'CONTENT FOUND', 'URL RESPONSE TIME'])    
        for url_key, infos in data.iteritems():
        	color = resultColors[infos[0]]
        	status = HTML.TableCell(infos[0],bgcolor=color)
        	content_found = HTML.TableCell(infos[1],bgcolor=color)
        	elapsed_time = HTML.TableCell(infos[2],bgcolor=color)
        	at_time = HTML.TableCell(infos[3])
        	t.rows.append([at_time, url_key, status, content_found, elapsed_time])
        self.wfile.write(html_head)
        self.wfile.write(t)      

def start_web_server(host_name, port_no):
    """
    Runs HTTP WebServer & Shows Website page on a local host   
    """
    try:
        cfg = ConfigParser()
        cfg.read(settings.config_file)
        HOST_NAME   = host_name
        PORT_NUMBER = port_no

        server_class = BaseHTTPServer.HTTPServer
        http_server  = server_class((HOST_NAME, PORT_NUMBER), SampleHttpWebServerHandler)    
        print "Web Server Started - %s:%s"%(HOST_NAME, PORT_NUMBER)
        t = Thread(target = http_server.serve_forever())
        t.daemon = True  
        try:
            t.start()
        except KeyboardInterrupt:
            print "KeyBoard Interrupted - Closing Server Socket at Port No:%s"%PORT_NUMBER
            http_server.socket.close()
        http_server.server_close()
        print "Web Server Stopped - %s:%s" % (HOST_NAME, PORT_NUMBER)
        
    except ValueError, e:
        print "Server Failed to Start, Improper Values configured in config file. Error: %s" %e
    except:
        e = sys.exc_info()[0]        
        print "Server Stopped to Start - Caught Exception, Error : %s"%str(e)

if __name__ == '__main__':
    cfg = ConfigParser()
    cfg.read(settings.config_file)
    host_name   = cfg.get('SERVER', 'host', 0)
    port_no = int(cfg.get('SERVER', 'port', 0))
    import webbrowser
    webbrowser.open_new("http://%s:%s/"%(hostname, port))
    start_web_server(host_name, port_no)
    