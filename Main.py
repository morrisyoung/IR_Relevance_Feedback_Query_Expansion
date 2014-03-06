import sys
import os
import urllib
import urllib2
import json
import re

from stemming.porter2 import stem
from Core import *
from Clear import *


class Main:

    def __init__(self):
        self.core = Core()
        self.query = ""
        self.searchKey = "8YBQXoDFDGn672pz6V9N0Y2ZFTf6GS5agARpCvr2sXU="
        self.goal = 0.9
        self.stopWords = ['a', 'able', 'about', 'across', 'after', 'all', 'almost', 'also', 'am', 'among', 'an',
                          'and', 'any', 'are', 'as', 'at', 'be', 'because', 'been', 'but', 'by', 'can', 'cannot',
                          'could', 'dear', 'did', 'do', 'does', 'either', 'else', 'ever', 'every', 'for', 'from',
                          'get', 'got', 'had', 'has', 'have', 'he', 'her', 'hers', 'him', 'his', 'how', 'however',
                          'i', 'if', 'in', 'into', 'is', 'it', 'its', 'just', 'least', 'let', 'like', 'likely', 'may',
                          'me', 'might', 'most', 'must', 'my', 'neither', 'no', 'nor', 'not', 'of', 'off', 'often',
                          'on', 'only', 'or', 'other', 'our', 'own', 'rather', 'said', 'say', 'says', 'she', 'should',
                          'since', 'so', 'some', 'than', 'that', 'the', 'their', 'them', 'then', 'there', 'these',
                          'they', 'this', 'tis', 'to', 'too', 'twas', 'us', 'wants', 'was', 'we', 'were', 'what',
                          'when', 'where', 'which', 'while', 'who', 'whom', 'why', 'will', 'with', 'would', 'yet',
                          'you', 'your']
        self.stopWords = set(self.stopWords)
        return

    def execute(self):
        """
        Receive query from user,
        Get results from Bing.com,
        Let the user to judge relevance,
        Give processed results to Core,
        Get new query from Core,
        Continue to get results from Bing.com
        """
        print("Please input query")
        self.query = raw_input()
        # to make all the contents encoded uniform
        # self.query=self.query.decode('utf-8')
        self.core.query = self.query.split()
        print("Please input target precision")
        try:
            self.goal = float(raw_input())
        except Exception:
            print("Input is not a valid float number, program will exit!")
            return


        totalAns = 10.0
        correctAns = 0.0
        totalLoop = 1
        while True:  # main loop, keeping getting new queries from Core and post to Bing
            query = urllib.quote(self.query)
            credentials = (':%s' % self.searchKey).encode('base64')[:-1]
            auth = 'Basic %s' % credentials
            url = 'https://api.datamarket.azure.com/Data.ashx/Bing/Search/' \
                + 'Web?Query=%27' + query + '%27&$top=10&$format=json'
            request = urllib2.Request(url)
            request.add_header('Authorization', auth)
            request.add_header('User-agent', 'Mozilla/5.0')
            request_opener = urllib2.build_opener()
            response = request_opener.open(request)
            response_data = response.read()
            json_result = json.loads(response_data)
            result_list = json_result['d']['results']

            # ----------------------------answers of given query got from Bing--------------------------------

            if result_list.__len__() < 10:  # check if there are enough results
                print("No enough results get from Bing, program will exit.")
                return

            CoreInputs = []  # exactly 10 results to be given to Core
            for i in range(result_list.__len__()):  # Let user to judge all 10 results
                title = result_list[i]['Title']
                summary = result_list[i]['Description']
                text = ""
                url = result_list[i]['DisplayUrl']
                print ("-------------------------------------------------------------------")
                print ("Title:   "),
                print (title.encode('utf-8'))
                print ("Summary: "),
                print (summary.encode('utf-8'))
                print ("URL:     "),
                print (url.encode('utf-8'))

                # -----------------------------Try to get text from web page---------------------------------
                # description = None
                # keywords = None
                # try:
                #     if url.find('http') is -1:
                #         webContent = urllib2.urlopen('http://' + url).read()
                #     else:
                #         webContent = urllib2.urlopen(url).read()
                #     webContent = webContent.lower()
                #     description, keywords = self.getInformationFromHTML(webContent)
                # except Exception:
                #     doNothing = 1
                #
                # if description is not None:
                #     text = text + ' ' + description
                # if keywords is not None:
                #     text = text + ' ' + keywords
                #
                #print text
                # -----------------------------Webpage got---------------------------------

                newInput = CoreInput()  # input processed results to Core
                newInput.title = self.removePunc(title).split()
                newInput.summary = self.removePunc(summary).split()
                newInput.text = self.removePunc(text).split()
                newInput.url = url
                userAns = 'None'

                if self.core.removeStopWords is True:  # remove stop words
                    newInput.title = self.removeStopWords(newInput.title)
                    newInput.summary = self.removeStopWords(newInput.summary)
                    newInput.text = self.removeStopWords(newInput.text)

                if self.core.stemming is True:  # stemming words
                    newInput.title = self.stemming(newInput.title)
                    newInput.summary = self.stemming(newInput.summary)
                    newInput.text = self.stemming(newInput.text)

                # ----------------------------Original string processed--------------------------------

                while userAns != 'Y' and userAns != 'y' and userAns != 'N' and userAns != 'n':
                    userAns = raw_input("Is this result relevant or not? Please input Y/N\n")
                    if userAns == 'Y' or userAns == 'y':
                        newInput.relevant = True
                        correctAns += 1
                        break
                    elif userAns == 'N' or userAns == 'n':
                        newInput.relevant = False
                        break
                    else:
                        print('Please input Y or N !')
                CoreInputs.append(newInput)
            print("\n-------------------------------------------------------------------\n")

            # ----------------------------10 results judged by user--------------------------------

            if correctAns / totalAns > self.goal - 1e-6:  # goal achieved, exit program
                print("Precision goal achieved, %d loop(s) used, program will exit." % totalLoop)
                return
            elif correctAns / totalAns < 1e-6:  # precision is 0, exit program
                print("Precision goal is 0, program will exit.")
                return
            else:  # goal not achieved, give information to Core and refine the query
                totalLoop += 1
                correctAns = 0.0
                self.core.input(CoreInputs)
                self.query = self.core.getQuery()
                print("New query is %s, another 10 answer will be shown" % self.query)

        return

    def removePunc(self, str):
        """
        remove punctuations in the title or summary
        """
        newStr = re.sub(ur"[\,\|\-\?\[\]\{\}\(\)\"\:\;\!\@\#\$\%\^\&\*\>\<]|(\.$)|(\.\.\.)", ' ', str)
        newStr = newStr.lower()
        return newStr

    def removeStopWords(self, wordsList):
        """
        remove stop words from title and summary
        """
        newWordList = []
        for eachWord in wordsList:
            if eachWord not in self.stopWords:
                newWordList.append(eachWord)
        return newWordList

    def stemming(self, wordList):
        """
        stem title and summary
        """
        newWordList = []
        for eachWord in wordList:
            newWordList.append(stem(eachWord))
        return newWordList

    def getInformationFromHTML(self, content):
        """
        get some useful information from HTML file besides Bing result
        """
        description = None
        keywords = None
        result = re.findall(ur"<meta.*?\/>", content, re.UNICODE)
        for eachRes in result:
            if eachRes.find('name="description"') is not -1:
                description = re.search(ur"content=\".*?\"", eachRes)
                if description is not None:
                    description = description.group()
                    description = description[9:-1]
            if eachRes.find('name="keywords"') is not -1:
                keywords = re.search(ur"content=\".*?\"", eachRes)
                if keywords is not None:
                    keywords = keywords.group()
                    keywords = keywords[9:-1]
        return description, keywords



main = Main()
main.execute()
# remove all the intermediate files generated by the running program (Feb.13)
predir = os.getcwd()
clear = Clear()
l = clear.clear(predir)
for f in l:
    os.remove(f)