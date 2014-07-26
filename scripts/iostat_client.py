#!/usr/bin/env python

import urllib
import urllib2
import json
import subprocess
import datetime

URL = 'http://bowie.genomecenter.ucdavis.edu:8000/api/io_report/'
SERVER = 'bowie.genomecenter.ucdavis.edu'
IOSTAT_INTERVAL = 60 #Run iostat every n seconds
POST_INTERVAL = 1 #Post every n times iostat runs
# SERVER = 'athena.genomecenter.ucdavis.edu'

def main():
    run_iostat()


def run_iostat():
    cmd = ['iostat', '-mx', str(IOSTAT_INTERVAL)]
    popen = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    reports = []
    disks={}
    headers = []
    for line in iter(popen.stdout.readline, ""):
        try:
            parts = line.split()
            if len(parts) > 0:
                if 'Device:' == parts[0]:
                    headers = parts[1:]
                    report={'timestamp':str(datetime.datetime.now()),'disks':disks}
                    reports.append(report)
                    if len(reports) >= POST_INTERVAL:
                        try:
                            send_reports(reports)
                            reports = []
                        except:
                            print 'Error sending iostat info to "%s"' % URL
                            pass
                    disks={}
                elif parts[0][0:2] == 'sd':
                    disks[parts[0]] = dict(zip(headers,[float(x) for x in parts[1:]]))
        except Exception, e:
            print 'Exception'
            print e
 
def send_reports(reports):
#     print reports
    data = {
            'server': SERVER,
            'data': reports,
    }
    
    req = urllib2.Request(URL)
    req.add_header('Content-Type', 'application/json')
#     print 'response'
    json.load(urllib2.urlopen(req, json.dumps(data)))
                    
def run_iostat_old():
    cmd = ['iostat', '-mx', '10']
    print cmd
    process = subprocess.Popen(cmd,
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.PIPE)
    # wait for the process to terminate
    out, err = process.communicate()
    errcode = process.returncode
#     if errcode == 64:
    post_result(out)

def post_result(body):
    values = {'server' : SERVER, 'body' : body }
    data = urllib.urlencode(values)
    req = urllib2.Request(URL, data)
    response = urllib2.urlopen(req)
    print response.read()
    
if __name__ == "__main__":
    main()
