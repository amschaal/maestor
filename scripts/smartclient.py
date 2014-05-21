#!/usr/bin/env python

import urllib
import urllib2
import subprocess

URL = 'http://bowie.genomecenter.ucdavis.edu:8000/api/smart_report/'
SERVER = 'bowie.genomecenter.ucdavis.edu'
# SERVER = 'athena.genomecenter.ucdavis.edu'

def main():
    disks = get_disks()
    for disk in disks:
        run_smartctl(disk)

def get_disks():
    cmd = ['smartctl', '--scan']
    process = subprocess.Popen(cmd,
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.PIPE)
    # wait for the process to terminate
    out, err = process.communicate()
    errcode = process.returncode
    return [device.split()[0] for device in out.splitlines()]

def run_smartctl(disk):
    cmd = ['smartctl', '-a', disk]
    print cmd
    process = subprocess.Popen(cmd,
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.PIPE)
    # wait for the process to terminate
    out, err = process.communicate()
    errcode = process.returncode
#     if errcode == 64:
    post_result(disk,out)

def post_result(disk, body):
    values = {'server' : SERVER,'unix_device':disk, 'body' : body }
    data = urllib.urlencode(values)
    req = urllib2.Request(URL, data)
    response = urllib2.urlopen(req)
    print response.read()
    
if __name__ == "__main__":
    main()
