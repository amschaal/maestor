import re
SMART_CTL = {
    '6.2':
    {
        'INFO':
        {
            'START':r'.*INFORMATION SECTION.*',
            'END':'',
            'REGEX':
            [
                r'Serial Number:\s+(?P<serial>\w+)',
                r'Device Model:\s+(?P<model>\w+)',
                r'Firmware Version:\s+(?P<firmware>\w+)',
                r'Model Family:\s+(?P<family>.+)',
                r'User Capacity:\s+(?P<capacity>.+)',
                r'Rotation Rate:\s+(?P<rpm>.+)',
            ]
         },
         'ATTRS':
         {
            'START':r'ID#\s+ATTRIBUTE_NAME\s+FLAG\s+VALUE\s+WORST\s+THRESH\s+TYPE\s+UPDATED\s+WHEN_FAILED\s+RAW_VALUE',
            'END':r'',
            'REGEX': #Last regex has priority, and will overwrite attr data!!
            [
                r'\s*(?P<id>\d+)\s+(?P<name>\w+)\s+[0-9xa-f]{6}\s+(?P<value>\d+)\s+(?P<worst>\d+)\s+(?P<thresh>\d+)\s+(?P<type>[-\w]+)\s+(?P<updated>\w+)\s+(?P<failed>[-\w]+)\s+(?P<raw_value>\d+)\s*.*'
            ]
          }
    }      
}


class SmartParse(object):
    
    def __init__(self,text,version):
        self.text = text
        self.version = version
        self.info = {}
        self.attrs = []
        self.parse()
    def parse(self):
        lines = self.text.splitlines()
        for index, line in enumerate(lines):
            if re.match(SMART_CTL[self.version]['INFO']['START'],line) is not None:
                self.parse_info(lines[index+1:])
            if re.match(SMART_CTL[self.version]['ATTRS']['START'],line) is not None:
                self.parse_attrs(lines[index+1:])
    def parse_info(self,lines):
        for index,line in enumerate(lines):
            if line == '':
                return index
            for regex in SMART_CTL[self.version]['INFO']['REGEX']:
                matches = re.match(regex,line)
                if matches is not None:
                    try:
                        self.info.update(matches.groupdict())
                    except:
                        print 'No update'
    def parse_attrs(self,lines):
        for index,line in enumerate(lines):
            if line == '':
                return
            attr = None
            #Last regex has priority, and will overwrite attr data!!
            for regex in SMART_CTL[self.version]['ATTRS']['REGEX']:
                matches = re.match(regex,line)
                if matches is not None:
                    attr = matches.groupdict()
            if attr is not None:
                self.attrs.append(attr)
    def get_pk(self):
        return '%s:%s'%(self.info['model'],self.info['serial'])
    