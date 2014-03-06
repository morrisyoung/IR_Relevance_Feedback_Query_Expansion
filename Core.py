from Interface import *
from Rocchio import *

class Core:

    query = []  # query sent to Search Engine last time
    stemming = False  # or False
    removeStopWords = True  # or False
    coreInputs = []

    def __init__(self):
        return

    # def input(self, CoreInputs):  # CoreInputs is an array of 10 CoreInput
    #     return

    def input(self, CoreInputs):  # CoreInputs is an array of 10 CoreInput

        self.coreInputs = CoreInputs

        # for i in range(CoreInputs.__len__()):
        #     print (CoreInputs[i].title)
        #     print (CoreInputs[i].summary)
        #     print (CoreInputs[i].text)
        #     print (CoreInputs[i].url.encode('utf-8'))
        #     print (CoreInputs[i].relevant)
        #     print ('-------------------------------------')

        return

    def getQuery(self):
        rocchio = Rocchio()
        num = 1  # each time we update only one new query word
        RFType = 1  # we decide to use full Rocchio algorithm to expand the query items
        option = 12  # we decide to use title and
        result = rocchio.RocchioExpansion(num, self.query, RFType, self.coreInputs, option)

        print result
        self.query = result
        final = ''
        for t in result:
            final = final + t + ' '
        final = final.strip()
        return final

