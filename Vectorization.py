#!/usr/bin/python
# Filename: Vectorization.py
# Function: We use this class to vectorize the queried targets. I use this Vectorization other than a 
#    inverted-indexing because I think we will not use the position information, so I drop them.
# VectorBuilding(self,CoreInputs,option)-- return (self.WholeS,self.WholeV) which can then be used by 
#                        other RF method in need of tf,df... here the WholeS means 
#                        whole space, combined by 1/2/3 different kinds of space 
#                        (title,summary,text); the WholeV means whole vector, the 
#                        corresponding local term frequency vector
#                    -- CoreInputs: a list of N CoreInput object; default N=10
#                    -- option: used to indicate the feature space combined; 
#                        1/2/3 combination of title space, summary space and text space
#                        defined as followed:
#                        -- option=1: Title space
#                        -- option=2: Summary space
#                        -- option=3: Text space
#                        -- option=12: combined Title space and Summary space
#                        -- option=23: combined Summary space and Text space
#                        -- option=13: combined Title space and Text space
#                        -- otherwise: combined three kinds of space
# WeightVector(self,CoreInputs,option)     -- return the weighted vector for each ducoment, 
#                    which can be further used by Rocchio algorithm.
#                    -- formula used: w_ij=tf_ij*log(N/df_i) for term i in document j
#                        -- tf_ij: term frequency for term i in ducoment j
#                        -- N: # of all documents
#                        -- df_i: document frequency for term i
#                    -- CoreInputs: a list of N CoreInput object; default N=10
#                    -- option: used to indicate the feature space combined; 
#                        1/2/3 combination of title space, summary space and text space
#                        defined as followed:
#                        -- option=1: Title space
#                        -- option=2: Summary space
#                        -- option=3: Text space
#                        -- option=12: combined Title space and Summary space
#                        -- option=23: combined Summary space and Text space
#                        -- option=13: combined Title space and Text space
#                        -- otherwise: combined three kinds of space

from Interface import *
import math

class Vectorization:

    def __init__(self):
        self.TitleS = []  # A array of string list; the space of all titles
        self.TitleV = []  # A array of N hashtables (directories) for Title space of the CoreInput class
        self.SummaryS = []  # Summary space
        self.SummaryV = []  # Summary vector
        self.TextS = []  # Text space
        self.TextV = []  # Text vector
        self.WholeS = []  # A array of string list; the space of combination of 1, 2 or 3 of 3 kinds of spaces
        self.WholeV = []  # A array of N hashtables (directories), each of which is a term frequency vector for whole space
        self.WeightV = []  # A array of N hashtables (directories), each of which is a weight vector for d_j
        return

    def VectorTitle(self, CoreInputs):
        """the structure of the CoreInput class:
        self.title = []  # array of string, title of returned file
        self.summary = []  # array of string, summary of returned file
        self.text = []  # array of string, text of returned file, may be empty
        self.url = ""  # string, URL of returned file
        self.relevant = True  # this search research is relevant or not
        """
        space = []
        for i in range(len(CoreInputs)):  # space building
            title = CoreInputs[i].title
            for t in title:
                if t not in space:
                    space.append(t)
        for i in range(len(CoreInputs)):  # vector building, list of hashtables, key-value: term-wordfrequency
            title = CoreInputs[i].title
            self.TitleV.append({})
            for t in space:
                self.TitleV[i][t] = 0
            for t in title:
                self.TitleV[i][t] += 1
        self.TitleS = space
        return

    def VectorSummary(self, CoreInputs):
        space = []
        for i in range(len(CoreInputs)):  # space building
            summary = CoreInputs[i].summary
            for t in summary:
                if t not in space:
                    space.append(t)
        for i in range(len(CoreInputs)):  # vector building, list of hashtables, key-value: term-wordfrequency
            summary = CoreInputs[i].summary
            self.SummaryV.append({})
            for t in space:
                self.SummaryV[i][t] = 0
            for t in summary:
                self.SummaryV[i][t] += 1
        self.SummaryS = space
        return

    def VectorText(self, CoreInputs):
        space = []
        for i in range(len(CoreInputs)):  # space building
            text = CoreInputs[i].text
            for t in text:
                if t not in space:
                    space.append(t)
        for i in range(len(CoreInputs)):  # vector building, list of hashtables, key-value: term-wordfrequency
            text = CoreInputs[i].text
            self.TextV.append({})
            for t in space:
                self.TextV[i][t] = 0
            for t in text:
                self.TextV[i][t] += 1
        self.TextS = space
        return

    def VectorCombine(self, S1, V1, S2, V2, totalAns):
        space = []
        for t in S1:
            if t not in space:
                space.append(t)
        for t in S2:
            if t not in space:
                space.append(t)
        for i in range(totalAns):  # vector building, list of hashtables, key-value: term-wordfrequency
            self.WholeV.append({})
            for t in space:
                val1 = 0
                val2 = 0
                if t in V1[i].keys():
                    val1 = V1[i][t]
                if t in V2[i].keys():
                    val2 = V2[i][t]
                self.WholeV[i][t] = val1 + val2
        self.WholeS = space
        return

    def VectorBuilding(self, CoreInputs, option):
        self.VectorTitle(CoreInputs)
        self.VectorSummary(CoreInputs)
        self.VectorText(CoreInputs)
        if option == 1:
            self.WholeS=self.TitleS
            self.WholeV=self.TitleV
            return (self.WholeS, self.WholeV)
        elif option == 2:
            self.WholeS=self.SummaryS
            self.WholeV=self.SummaryV
            return (self.WholeS, self.WholeV)
        elif option == 3:
            self.WholeS=self.TextS
            self.WholeV=self.TextV
            return (self.WholeS, self.WholeV)
        elif option == 12:
            self.VectorCombine(self.TitleS, self.TitleV, self.SummaryS, self.SummaryV, len(CoreInputs))
            return  (self.WholeS, self.WholeV)
        elif option == 23:
            self.VectorCombine(self.SummaryS, self.SummaryV, self.TextS, self.TextV,len(CoreInputs))
            return  (self.WholeS, self.WholeV)
        elif option == 13:
            self.VectorCombine(self.TitleS, self.TitleV, self.TextS, self.TextV, len(CoreInputs))
            return  (self.WholeS, self.WholeV)
        else:#combine three spaces
            self.VectorCombine(self.TitleS, self.TitleV, self.SummaryS, self.SummaryV, len(CoreInputs))
            self.VectorCombine(self.WholeS, self.WholeV, self.TextS, self.TextV, len(CoreInputs))
            return (self.WholeS, self.WholeV)

    def WeightVector(self, CoreInputs, option):
        self.VectorBuilding(CoreInputs, option)
        N = len(CoreInputs)
        # here are some bugs!!!-> if a word appear in every document, its score will be zero!!! so no bug!!
        for i in range(N):
            self.WeightV.append({})
            sum = 0
            for t in self.WholeS:
                if self.WholeV[i][t] == 0:
                    self.WeightV[i][t] = 0
                else:
                    tf = self.WholeV[i][t]
                    df = 0
                    for j in range(N):
                        if self.WholeV[j][t] > 0:
                            df += 1
                    d = float(N)/float(df)
                    self.WeightV[i][t] = tf * (math.log(d))
                sum += math.pow(self.WeightV[i][t], 2)
            sum = math.sqrt(sum)
            for t in self.WholeS:
                self.WholeV[i][t] /= sum
        return (self.WholeS, self.WeightV)

## End of Vectorization.py
