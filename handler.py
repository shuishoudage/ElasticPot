import regexPattern
import logging
import re
import json
from collections import OrderedDict
from urllib.parse import urlparse
from tabulate import tabulate
import random


class Handler:
    def __init__(self):
        pass

    def GET_handler(self, request):
        fakeBannerFilePath = './FakeData/FakeBanner/banner1.json'
        # when query root(/)
        if re.match(regexPattern.ROOT, request.path):
            fakeBanner = self.printFile(fakeBannerFilePath)
            if re.match(regexPattern.ROOT_PRETTY, request.path):
                return json.dumps(fakeBanner, indent=2) + '\n'
            else:
                return json.dumps(fakeBanner) + '\n'
        # when query indices
        elif regexPattern.INDICES in request.path:
            fakeIndices = './FakeData/FakeIndices/indices1.json'
            data = self.printFile(fakeIndices)
            if re.match(regexPattern.INDICES_PRETTY, request.path):
                result = tabulate(data['indices'], headers=data['header'],
                                  tablefmt="plain")
                return result
            else:
                result = tabulate(data['indices'], tablefmt="plain")
                return result
        # when query something not included will print error banner
        else:
            fakeError = './FakeData/FakeError/fakeError1.json'
            logging.info('\tfake error entered')
            r = self.printFile(fakeError)
            if re.match(regexPattern.ERROR_PRETTY, request.path):
                return json.dumps(r, indent=2) + '\n'
            else:
                return json.dumps(r) + '\n'

    def POST_handler(self, request):
        pass

    def PUT_handler(self, request):
        fakeDelAck = OrderedDict([('acknowledge', 'true')])
        fakeIndices = './FakeData/FakeIndices/indices1.json'
        indice = urlparse(request.path).path.split('/')[1]
        ranSize = self.randSize()
        newIndices = ['yellow', 'open', indice, '5', '1',
                      '0', '0', ranSize, ranSize]
        self.writeFile(fakeIndices, newIndices)
        logging.info('\twrote to file')
        if 'pretty' in request.path:
            return json.dumps(fakeDelAck, indent=2)
        else:
            return json.dumps(fakeDelAck)

    def DELETE_handler(self, request):
        fakeError = './FakeData/FakeError/fakeError1.json'
        fakeIndices = './FakeData/FakeIndices/indices1.json'
        fakeDelAck = OrderedDict([('acknowledge', 'true')])
        index = dict()
        requestedIndice = urlparse(request.path).path.split('/')[1]
        for i, c in enumerate(self.printFile(fakeIndices)['indices']):
            index[i] = c
        for k in index:
            if requestedIndice in index[k]:
                self.removeIndice(k, fakeIndices)
                return json.dumps(fakeDelAck)
        else:
            r = self.printFile(fakeError)
            indice = urlparse(request.path).path.split('/')[1]
            r['error']['root_cause'][0]['resource.id'] = indice
            r['error']['root_cause'][0]['index'] = indice
            r['error']['resource.id'] = indice
            r['error']['index'] = indice
            if 'pretty' in request.path:
                return json.dumps(r, indent=2) + '\n'
            else:
                return json.dumps(r)

    def printFile(self, filePath):
        try:
            with open(filePath, mode='r') as f:
                return json.load(f, object_pairs_hook=OrderedDict)
        except IOError as e:
            logging.error(e)

    def writeFile(self, filePath, newEntry):
        try:
            feeds = self.printFile(filePath)
            with open(filePath, mode='w') as f:
                feeds['indices'].append(newEntry)
                json.dump(feeds, f)
        except IOError as e:
            logging.error(e)

    def randSize(self):
        r = random.randint(200, 1000)
        return str(r)+'b'

    def removeIndice(self, k, filePath):
        r = self.printFile(filePath)
        r['indices'].pop(k)
        with open(filePath, mode='w') as f:
            json.dump(r, f)
