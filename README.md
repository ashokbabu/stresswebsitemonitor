# stresswebsitemonitor

README : Load test tool

USAGE : python websitemonitor.py

- Reads Data from configuration file, can handle any number of urls say example, 
  Can be stress tested by adding more urls
- Periodically checks the statuses with timeout present in configuration file
- Runs local webserver after status check starts in the same Process, currently running in a seperate thread.
- Used 3rd party HTML.py module for html page generation, for look and feel.
- Used requests module instead of urllib/httplib modules as requests module is thread safe.

Contact: <Chiruvella Ashok Babu> chashokbabu@gmail.com

