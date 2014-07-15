import re

class IOParse(object):
    HEADER_REGEX= r'Device:\wtps\wkB_read/s    kB_wrtn/s    kB_read    kB_wrtn'
    def __init__(self,text,version="None"):
        self.text = text
        self.version = version
        self.disk_stats = {}
#         self.parse()
        
    def parse(self):
        lines = self.text.splitlines()
        for index, line in enumerate(lines):
            parts = line.split()
            if len(parts) > 0:
                if 'Device:' == parts[0]:
                    return self.parse_stats(lines[index+1:],parts[1:])
    def parse_stats(self,lines,headers):
        for line in lines:
            parts = line.split()
            if len(parts) > 1:
                if parts[0][0:2] =='sd':
                    self.disk_stats[parts[0]]={}
                    for index,part in enumerate(parts[1:]):
                        self.disk_stats[parts[0]][headers[index]]=part
        return self.disk_stats
    