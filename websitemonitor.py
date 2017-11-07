from Queue import Queue
from datetime import datetime
from ConfigParser import ConfigParser
import threading
import time
import re
import os
import pickle

import requests
import requests.exceptions

from CustomLogger import CustomLogger
import settings
import webserver

NUM_WORKERS = 8


def normalize_url(url):
    '''If a url doesn't have a http/https prefix, add http://
       Urls are read from config file which has : as de-limiter, to overcome it 
    '''
    if not re.match('^http[s]?://', url):
        url = 'http://' + url
    return url

class WebSiteMonitor:
    def __init__(self, log, urldatadict, timeout=120):
        self.queue = Queue()
        self.urldata_dict = urldatadict
        self.log = log
        self.timeout = timeout
        for i in xrange(NUM_WORKERS):
            t = threading.Thread(target=self.worker)
            t.setDaemon(True)
            t.start()
    
    def worker(self):
        while 1:
            url, search_text, Q = self.queue.get()
            print("Requesting %s URL"%url)
            startTime = time.time()
            try:
                r = requests.get(url)
                r.raise_for_status()  # Raises a HTTPError if the status is 4xx, 5xxx
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
                Q.put(('DOWN', url, "CONCERR/TIMEOUT ERR", time.time()-startTime, str(datetime.now())))
            except requests.exceptions.HTTPError:
                Q.put(('DOWN', url, "CLIENT(4xx)/SERVER(5xx) ERR", time.time()-startTime, str(datetime.now())))
            else:
                response_time = time.time()-startTime
                search_text_found = "NO"                   
                if search_text in r.content:
                    search_text_found = "YES"
                Q.put(('UP', url, search_text_found, response_time, str(datetime.now())))
            
    def checkUrlStatus(self):
        Q = Queue() # Creating second queue so that worker threads can send the data back again
        for url, content in self.urldata_dict.iteritems():
            # Add the URLs in Queue to be downloaded asynchronously
            url = normalize_url(url.strip())
            self.queue.put((url, content, Q))

        urlStatusDict = dict()
        for i in xrange(len(self.urldata_dict.items())):
            # Get the data as it arrives, raise any exceptions if they occur
            status, url, content_found, elapsed_time, at_time = Q.get()
            msg_string = "URL: %s , STATUS:%s, CONTENT Found:%s, TimeTook : %s"%(url, status, content_found, elapsed_time)
            self.log.write_to_log(msg_string)
            urlStatusDict[url] = (status, content_found, elapsed_time, at_time)

        with open(settings.storage_db_file, 'wb') as handle:
            pickle.dump(urlStatusDict, handle, protocol=pickle.HIGHEST_PROTOCOL)
        # Check Interval to check statuses again after ? seconds
        threading.Timer(self.timeout, self.checkUrlStatus).start()

if __name__ == '__main__':
    try:
        log = CustomLogger()
        cfg = ConfigParser()
        cfg.read(settings.config_file)
        urlsContentDict = eval(cfg.get('URLS_CONTENT', 'testurls'))
        check_interval = int( cfg.get('TIME_INTERVAL', 'interval', 0) )
        st = WebSiteMonitor(log, urlsContentDict, check_interval)
        st.checkUrlStatus()
        # following opens the server interface which displays the weburl statuses
        hostname = cfg.get('SERVER', 'host', 0)
        port     = int(cfg.get('SERVER', 'port', 0))
        server_url = "http://%s:%s/"%(hostname, port)
        log.write_to_log("Visit the below rul to check the statuses:  %s"%server_url)
        import webbrowser
        webbrowser.open_new(server_url)
        webserver.start_web_server(hostname, port)
    except KeyboardInterrupt:
            print "Program exited because of keyboard interpurt"
            sys.exit(1)
