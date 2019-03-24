#Python 3.0
import re
import os
import collections
import time
import math
import operator
from decimal import Decimal
from operator import add,sub # for the sake of elements add in two lists
from numpy import dot
from numpy.linalg import norm
#import other modules as needed

class index:
	def __init__(self,path):
		self.base_path = path
		self.termIndex = {} # key :: String, value : termId :: String
		self.termsFromDocId = {} # key :: String
		self.docIdToFileName = {} # key :: String
		self.docIndex = {}
		self.files = os.listdir(path)
		self.index = {} # key : termId :: String, value : [idf, (docId, wtd)]
	
	def cosine_similarity(self,v1,v2):
		sumxx, sumxy, sumyy = 0, 0, 0
		for i in range(len(v1)):
			x = v1[i]; y = v2[i]
			sumxx += x*x
			sumyy += y*y
			sumxy += x*y
		try: return sumxy/math.sqrt(sumxx*sumyy)
		except ZeroDivisionError: return 0
	@staticmethod
	def getQueryVector(self, query_terms, terms):
		ret = []
		for term in terms:
			if term in query_terms:
				try:
					termId = self.termIndex[term]
					idf = self.index[termId][0]
					ret.append(idf)
				except KeyError:
					ret.append(0)
			else:
				ret.append(0)
		return ret
		
	@staticmethod
	def getDocumentVector(self, docId, terms):
		d_vector = []
		for term in terms:
			if term in self.termsFromDocId[docId]:
				termId = self.termIndex[term]
				idf = self.index[termId][0]
				wtd = 0
				for i in range(1, len(self.index[termId])):
					if 'ID'+str(docId) == self.index[termId][i][0]:
						wtd = self.index[termId][i][1]
						break
				d_vector.append(idf * wtd)
			else :
					d_vector.append(0)
		return d_vector

	@staticmethod
	def getStopWords(self, fileName="TIME.STP"):
		cwd = os.getcwd()
		stopwords = open(cwd+"/time/"+fileName, "r").read().lower()
		return stopwords
	@staticmethod
	def getTermFrequency(self, arr, doc):
		frequency = {}
		for word in arr:
			if word in frequency:
				frequency[word] = frequency[word] + 1
			else :
				frequency[word] = 1
		return frequency
	@staticmethod
	def getDocsFromTerm(self, term):
		try:
			termId = self.termIndex[term]
			lst = self.index[termId]
			docs = []
			for i in range(1, len(lst)):
					docs.append(lst[i][0].replace('ID',''))
			return docs
		except KeyError:
			return []

	@staticmethod
	def printRankedScore(self, docsFromQuery, query_terms, k):
		q_vectors = {}
		d_vectors = {}
		stopwords = self.getStopWords(self)
		new_query_terms = [x for x in query_terms if x not in stopwords]
		for docId in docsFromQuery:
			terms = self.termsFromDocId[(str(docId))] + new_query_terms
			terms = list(set(terms))
			q_vectors[docId] = (self.getQueryVector(self, new_query_terms, terms))
			d_vectors[docId] = (self.getDocumentVector(self, str(docId), terms))
		score={}
		for key, value in d_vectors.items():
			score[key] = self.cosine_similarity(q_vectors[key], value)
		ranked_score = sorted(score.items(), key=operator.itemgetter(1),reverse=True)

		print("Query : " + str(query_terms))
		if (k > len(ranked_score)):
			for doc in ranked_score:
				print("docId : "+doc[0] + ",File Name : " + self.docIdToFileName[doc[0]] + ", Similarity : " + str(doc[1]))
		else :
			for i in range(0, k):
				print("docId: " + ranked_score[i][0] + ",File Name : " + self.docIdToFileName[ranked_score[i][0]] + ", Similarity : " + str(ranked_score[i][1]))
	def buildIndex(self):
		uniqueId = 0
		termId = 0
		fileName = 'TIME.ALL'
		idx = {}
		termIndex = self.termIndex
		docIndex = self.docIndex
		stopwords = self.getStopWords(self)
		initialTime = time.time()
		words = open(self.base_path+fileName, "r").read()
		fileNumber = re.findall('([*]TEXT \d{3})', words)

		docIdWithfileNumber = {} # Key :: Integer, Value :: String
		for f in fileNumber:
			docIdWithfileNumber[uniqueId] = f
			uniqueId+=1
		N = len(fileNumber)
		docs = re.split('[*]TEXT \d{3}[ ]+\d{2}[/]\d{2}[/ ]\d{2}[ ]+PAGE[ ]+\d{3}', words)
		# The second [/ ] expression is for capturing the TEXT 431
		del docs[0]
		docIdWithTerms = {}
		for key, _ in docIdWithfileNumber.items():
			docIdWithTerms[key] = docs[key].lower()
		for key, value in docIdWithTerms.items():
			arr = re.split('[\W]', value)
			newValue = list(set(arr))
			newValue = [ word for word in newValue if word not in stopwords and len(word) != 0]
			for word in newValue:
				if word not in docIndex:
					docIndex[word] = 1
				else:
					docIndex[word] += 1
		for key, value in docIdWithTerms.items():
			arr = re.split('[\W]', value)
			arr = [ x for x in arr if len(x) != 0]
			freqIndex = self.getTermFrequency(self, arr ,value)
			newValue = list(set(arr))
			newValue = [ word for word in newValue if word not in stopwords and len(word) != 0]
			self.termsFromDocId[str(key)] = newValue
			self.docIdToFileName[str(key)] = docIdWithfileNumber[key]
			for word in newValue:
				if word not in termIndex:
					termIndex[word] = termId
					termId+=1
				idf = math.log(float(N)/docIndex[word], 10)
				wtd = 1 + math.log(freqIndex[word], 10)
				pos = []
				if termIndex[word] in idx:
					idx[termIndex[word]].append( ('ID'+str(key), wtd, pos))
				else:
					idx[termIndex[word]] = [idf,('ID'+str(key), wtd, pos)]
		self.index = idx
		indexTime = time.time() - initialTime
		print("Index built in " + str(indexTime)+ " seconds")
		return self.index
	def rocchio(self, query_terms, pos_feedback, neg_feedback, alpha = 1, beta= 0.75, gamma = 0.15):
		def getQueryVectorAsDoc(query_terms, terms):
			ret = {}
			for term in terms:
					if term in query_terms:
							termId = self.termIndex[term]
							idf = self.index[termId][0]
							ret[term] = idf
					else:
							ret[term]= 0
			return ret
		def getDocumentVectorAsDoc(docId, terms):
			d_vector = {}
			for term in terms:
					if term in self.termsFromDocId[docId]:
							termId = self.termIndex[term]
							idf = self.index[termId][0]
							wtd = 0
							for i in range(1, len(self.index[termId])):
									if 'ID'+docId == self.index[termId][i][0]:
											wtd = self.index[termId][i][1]
											break
							d_vector[term] = idf * wtd
					else :
							d_vector[term]= 0
			return d_vector
		vector_space = []
		for docId in pos_feedback:
			vector_space += self.termsFromDocId[docId]
		for docId in neg_feedback:
			vector_space += self.termsFromDocId[docId]
		vector_space = list(set(vector_space))
		query_vector = getQueryVectorAsDoc(query_terms, vector_space)
		positive_vector ={}
		negative_vector = {}
		# sum up pos_feedback
		for term in vector_space:
			positive_vector[term] = 0
			negative_vector[term] = 0
		for docId in pos_feedback:
			d_vector = getDocumentVectorAsDoc(docId, vector_space)
			for term in vector_space:
				positive_vector[term] += d_vector[term]
		for docId in neg_feedback:
			d_vector = getDocumentVectorAsDoc(docId, vector_space)
			for term in vector_space:
				negative_vector[term] += d_vector[term]
		for term in vector_space:
			query_vector[term]  *= alpha
			positive_vector[term] *= (beta/len(pos_feedback))
			negative_vector[term] *= (gamma/len(neg_feedback))
		revised_vector = {}
		for term in vector_space:
			if (query_vector[term] + positive_vector[term] - negative_vector[term] > 0):
				revised_vector[term] = query_vector[term] + positive_vector[term] - negative_vector[term]
		return revised_vector
		# return revised_vector
	def query(self, query_terms, k=10):
		docsFromQuery = []
		stopwords = self.getStopWords(self)
		# stopwords = []
		new_query_terms = [ x for x in query_terms if x not in stopwords]
		for term in new_query_terms:
				docsFromQuery += self.getDocsFromTerm(self, term)
		# Make them union
		docsFromQuery = list(set(docsFromQuery))
		# add query terms into "terms"
		self.printRankedScore(self, docsFromQuery, query_terms ,k)
	#function for exact top K retrieval using cosine similarity
	#Returns at the minimum the document names of the top K documents ordered in decreasing order of similarity score
		return 0
	def print_dict(self):
    #function to print the terms and posting list in the index
		return 0
	def print_doc_list(self):
	# function to print the documents and their document id
		return 0

if __name__ == '__main__':
	a = index('./time/')
	a.buildIndex()
	# Query 1
	print("@Query:1")
	query1 = "KENNEDY ADMINISTRATION PRESSURE ON NGO DINH DIEM TO STOP SUPPRESSING THE BUDDHISTS"
	query1 = re.split(" ", query1.lower())
	print(query1)
	a.query(query1)
	# Query 6
	print("@Query:6")
	a.query(["ceremonial","cuicides","commited","by","some","buddhist","monks","in","south","viet","nam","and",
	"what","they","are","seeking","to","gain","by","such","acts"])
	# Query 12
	print("@Query:12")
	a.query(["controversy","betwwen","indonesia","and","malaya","on","the","proposed","pederation","of","malaysia",
	"which","would","unite","five","territories",])
	# Query 31
	print("@Query:31")
	a.query(["leaders","which","figure","in","discussions","of","the","future","of","the",
	"west","german","chancellorship"])