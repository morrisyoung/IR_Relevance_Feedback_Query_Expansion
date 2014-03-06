#!/usr/bin/python
# Filename: RSVScoring.py
# Function: We use this class to calculate the RSV score of each word in the querid objects. 
# And then return the highest socred terms with previous one in a order of decreasing RSV score. 
# The ordering method will be implemented in this class.
# Reference Paper:
# Examining and improving the effectiveness of relevance feedback for retrieval of scanned text documents, 
# Adenike M. Lam-Adesina, Gareth J.F. Jones, June 2005
# RSVExpansion(self,num,query,CoreInputs,option)-- implement the RSV scoring algorithm; 
#						-- num: # of new query terms added; 1 or 2; manually set this 
#							parameter because I think there is no appropriate mechanism 
#							to automatically set this parameter
#						-- query: old query string list
#						-- CoreInputs: a list of N CoreInput object; default N=10
#						-- option: used to indicate the feature space combined; 
#							1/2/3 combination of title space, summary space and text space

from Interface import *
from Vectorization import *
import math

class RSVScoring:

	def __init__(self):
		self.RSVScores={}#directory of scores, key-value: term-score
		self.RSVOrdered=[]#a list of tuples (term, score), ordered by the score decreasingly
		self.WholeS=[]#a array of string list; the space of combination of 1, 2 or 3 of 3 kinds of spaces
		self.WholeV=[]#a array of N hashtables (directories) for whole space of the CoreInput class. 
				#Key-value is term-localfrequency
		return

	def RSVCal(self,CoreInputs,option):
		vectorization=Vectorization()
		(self.WholeS,self.WholeV)=vectorization.VectorBuilding(CoreInputs,option)
		"""detailed RSV calculation formula:
		The formula is :
		TF   : term frequency, actually no help in our global environment
		DF   : document frequency
		DFR  : ducoment frequency in relevant documents
		num  : total number of documents
		numR : number of relevant documents
		RW(word) = log( ( (DFR + 0.5) * (num - DF - numR + DFR + 0.5) )
				/ ( (DF - DFR + 0.5) * (numR - DFR + 0.5) ) )
		RSV(word) = RW(word) * DFR

		Then we choose the word (or words) who has the highest RSV to be the next keyword.
		"""
		for t in self.WholeS:
			DF=0
			DFR=0
			num=10
			numR=0
			self.RSVScores[t]=0
			for i in range(len(self.WholeV)):
				if CoreInputs[i].relevant==True:
					numR=numR+1
					if self.WholeV[i][t]>0:
						DF=DF+1
						DFR=DFR+1
				else:
					if self.WholeV[i][t]>0:
						DF=DF+1
			if DFR==0:
				self.RSVScores[t]=0
			else:
				self.RSVScores[t]=DFR*math.log((DFR+0.5)*(num-DF-numR+DFR+0.5)/((DF-DFR+0.5)*(numR-DFR+0.5)))
		return

	def RSVOrder(self):
		d=self.RSVScores
		d_sorted=sorted(d.items(), key=lambda d:d[1])
		self.RSVOrdered=d_sorted.reverse()#a list of tuples
		return

	def RSVExpansion(self,num,query,CoreInputs,option):
		self.RSVCal(CoreInputs,option)
		self.RSVOrder()
		n=0
		for t in self.RSVOrdered:
			if t[0] in query:
				continue
			else:
				query.append(t[0])
				n=n+1
				if n==num:
					break
		#now the query list is added another one term, we need to order all the terms
		h_t={}
		for t in query:
			if t in self.RSVScores:
				h_t[t]=self.RSVScores[t]
			else:
				h_t[t]=0
		d=h_t
		d_sorted=sorted(d.items(), key=lambda d:d[1])
		d_sorted.reverse()#a list of tuples
		l=[]
		for t in d_sorted:
			l.append(t[0])
		return l

## End of RSVScoring.py