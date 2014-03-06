#!/usr/bin/python
# Filename: Rocchio.py
# Function: We use this class to implement the Rocchio algorithm. And then return the highest socred terms 
# with previous one in a order of decreasing score. The Vectorization class will be used in this class 
# to get the weighted vector of each document. The ordering method will be implemented in this class.
# ChangeCoefficient(self,alpha,beta,gamma)           -- change the Rocchio coefficients;
#                            -- all parameters are numbers
# RocchioExpansion(self,num,query,RFType,CoreInputs,option) -- implement the Rocchio algorithm; 
#                            -- num: # of new query terms added; 1 or 2; manually set this 
#                                parameter because I think there is no appropriate mechanism 
#                                to automatically set this parameter
#                            -- query: old query string list
#                            -- RFType: 1/2/3 indicating whole Rocchio/positive RF only
#                                        /positive with a dominant negative RF
#                                    in which RF means relevance feedback
#                            -- CoreInputs: a list of N CoreInput object; default N = 10
#                            -- option: used to indicate the feature space combined; 
#                                1/2/3 combination of title space, summary space and text space

from Interface import *
from Vectorization import *
import math


class Rocchio:

    def __init__(self):
        self.Rocchio = {}  # directory of Rocchio query vector, key-value: term-weight
        self.RocchioOrdered = []  # a list of tuples (term, score), ordered by the score decreasingly, 
                      # to select the most dominant features in the renewed query vector
        self.WholeS = []  # a array of string list; the space of combination of 1, 2 or 3 of 3 kinds of spaces; 
                  # initialized as empty
        self.WeightV = []  # a array of N hashtables (directories) for whole space of the CoreInput class. 
                  # Key-value is term-normalized-weight
        self.alpha = 1
        self.beta = 0.75
        self.gamma = 0.15
        return

    def ChangeCoefficient(self, alpha, beta, gamma):
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
        return

    def RocchioCal(self, query, RFType, CoreInputs, option):
        # RFType: 1:full Rocchio algorithm; 2:positive feedback only;
        # 3:positive feedback plus a dominant negative feedback
        vectorization = Vectorization()
        (self.WholeS, self.WeightV) = vectorization.WeightVector(CoreInputs, option)

        for t in query:  # because the query list was added later, I should renew the whole space
                # in case that previous space constructed from title, summary and text doesn't
                # include the features in the query list; here the query list is the last query request
            if t in self.WholeS:
                continue
            else:
                (self.WholeS).append(t)
                for i in range(len(self.WeightV)):
                    self.WeightV[i][t] = 0
        #------------------Rocchio parameters preparation----------------------------------------
        NR = 0
        NUR = 0
        for i in range(len(CoreInputs)):
            if CoreInputs[i].relevant is True:
                NR += 1
            else:
                NUR += 1
        alpha = self.alpha
        beta = self.beta/NR  # as there are at most 9 relevant document, at least 1 relevant document,
                #I don't deal with the zero denominator problem.
        if RFType == 1:
            gamma = self.gamma/NUR
        elif RFType == 2:
            gamma = 0
        else:  # RFType == 3
            gamma = self.gamma

        #-------------------to build the initial query vector and normalize it-------------------
        sum = 0
        for t in self.WholeS:
            if t in query:
                self.Rocchio[t] = 1
                sum += 1
            else:
                self.Rocchio[t] = 0
        sum = math.sqrt(sum)
        for t in self.WholeS:
            self.Rocchio[t] /= sum

        #DEBUG
        #print self.Rocchio

        #-------------------to process the remove list l for RFType = 3----------------------------
        l = []
        if RFType == 3:
            for i in range(len(CoreInputs)):
                if ~CoreInputs[i].relevant:
                    l.append(i)
            #process the l to make it eliminate the non-most dominant negative document
            h = {}
            for i in l:
                h[i] = self.CosineCal(self.Rocchio, self.WeightV[i])
                # TODO should we use the initial query vector to calculate the most dominant
                # negative document??? or use the center of the relevant document???
            d = h
            d_sorted = sorted(d.items(), key=lambda d: d[1])  # in a increasing order for the value
            l = []
            for t in d_sorted:
                l.append(t[0])
            l.remove(l[0])

        #------------------Rocchio algorithm-----------------------------------------------------
        #DEBUG
        #print self.WholeS
        #DEBUG
        for t in self.WholeS:
            #if t == u'gates':
            #    for i in range(len(CoreInputs)):
            #            print self.WeightV[i][t]  # all zero??!!
            self.Rocchio[t] *= alpha
            for i in range(len(CoreInputs)):
                if CoreInputs[i].relevant:
                    self.Rocchio[t] += beta*self.WeightV[i][t]
                else:
                    if RFType == 3:
                        if i not in l:
                            self.Rocchio[t] *= gamma*self.WeightV[i][t]
                    else:  # for RFType = 1 or 2
                        self.Rocchio[t] -= gamma*self.WeightV[i][t]
	
        #print self.Rocchio
        return

    def CosineCal(self, h1, h2):
        sum = 0
        s1 = 0
        s2 = 0
        for t in h1:
            sum += h1[t]*h2[t]
            s1 += math.pow(h1[t],2)
            s2 += math.pow(h2[t],2)
        s1 = math.sqrt(s1)
        s2 = math.sqrt(s2)
        value = sum/(s1*s2)
        return value

    def RocchioOrder(self):
        d = self.Rocchio
        d_sorted = sorted(d.items(), key=lambda d: d[1], reverse=True)
        self.RocchioOrdered = d_sorted
        return

    def RocchioExpansion(self, num, query, RFType, CoreInputs, option):
        self.RocchioCal(query, RFType, CoreInputs, option)
        self.RocchioOrder()

        n = 0
        for t in self.RocchioOrdered:
            if t[0] in query:
                continue
            else:
                query.append(t[0])
                n += 1
                if n == num:
                    break
        # now the query list is added another one term, we need to order all the terms
        h_t = {}
        for t in query:
            if t in self.Rocchio:  # actually this is unnecessary, for t is always in the self.WholeS then self.Rocchio
                h_t[t] = self.Rocchio[t]
            else:
                h_t[t] = 0
        d = h_t
        d_sorted = sorted(d.items(), key=lambda d: d[1], reverse=True)
        l = []
        for t in d_sorted:
            l.append(t[0])
	#now the list is sorted by weight from bigger to smaller, but we need some sorting to make the order more reasonable.
	#we have decided to use title and summary only
	l_full=[]
	hash_score={}
	N=len(CoreInputs)
	for i in range(N):#seperately deal with each title and summary; actually we double the score, but no problem.
		l_full=CoreInputs[i].title
		n=0
		N1=len(l_full)
		for t in l_full:
			n=n+1
			if t in l:
				#DEBUG
				#print t

				l_l=l[:]
				l_l.remove(t)
				for t1 in l_l:
					if n!=N1:
						if l_full[n]==t1:
							if (t,t1) in hash_score:
								hash_score[(t,t1)]+=1
								#DEBUG
								#print (t,t1)
							else:
								hash_score[(t,t1)]=1
								#DEBUG
								#print (t,t1)
					if n!=1:
						if l_full[n-2]==t1:
							if (t1,t) in hash_score:
								hash_score[(t1,t)]+=1
								#DEBUG
								#print (t1,t)
							else:
								hash_score[(t1,t)]=1
								#DEBUG
								#print (t1,t)
		l_full=CoreInputs[i].summary
		n=0
		N1=len(l_full)
		for t in l_full:
			n=n+1
			if t in l:
				#DEBUG
				#print t

				l_l=l[:]
				l_l.remove(t)
				for t1 in l_l:
					if n!=N1:
						if l_full[n]==t1:
							if (t,t1) in hash_score:
								hash_score[(t,t1)]+=1
								#DEBUG
								#print (t,t1)
							else:
								hash_score[(t,t1)]=1
								#DEBUG
								#print (t,t1)
					if n!=1:
						if l_full[n-2]==t1:
							if (t1,t) in hash_score:
								hash_score[(t1,t)]+=1
								#DEBUG
								#print (t1,t)
							else:
								hash_score[(t1,t)]=1
								#DEBUG
								#print (t1,t)
	#DEBUG
	#print hash_score
	if len(hash_score)!=0:
		n=0
		for t in hash_score:
			n=n+1
			if n==1:
				bi=t
			if hash_score[t]>=hash_score[bi]:
				bi=t
		#now we get the bi-gram as a tuple
		if len(l)>=3:
			l1=[]#store the non-bi-gram terms
			for t in l:
				if t not in bi:
					l1.append(t)
			hash_result={}
			hash_result[bi]=(self.Rocchio[bi[0]]+self.Rocchio[bi[1]])/2
			#DEBUG
			#print bi
			#print self.Rocchio[bi[0]]
			#print self.Rocchio[bi[1]]
			
			for t in l1:
				hash_result[t]=self.Rocchio[t]
			#DEBUG
			#print hash_result

			d=hash_result
			d_sorted=sorted(d.items(), key=lambda d: d[1], reverse=True)
			#DEBUG
			#print d_sorted

			l_final=[]
			for t in d_sorted:
				if t[0]==bi:
					#DEBUG
					#print t[0]
					l_final.append(bi[0])
					l_final.append(bi[1])
				else:
					l_final.append(t[0])
			#DEBUG
			#print l_final

			l=l_final
		else:
			l=[bi[0],bi[1]]
        return l

## End of Rocchio.py
