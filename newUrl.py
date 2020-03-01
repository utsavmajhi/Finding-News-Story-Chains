# -*- coding: utf-8 -*-

from pprint import pprint
import praw,sys,itertools,string,datetime,time
import os.path
import pickle
from textblob.sentiments import NaiveBayesAnalyzer
#from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk, string, newspaper
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from newspaper import Article
import re
from textblob import TextBlob
from math import log
from math import sqrt
from nltk import word_tokenize

mydfs = []
glob = 0
subCommentMap = {}
bucketDictionary = {}
sett = set()
stemmer = nltk.stem.porter.PorterStemmer()
remove_punctuation_map = dict((ord(char), None) for char in string.punctuation)


def dfs(comm):
	global glob
	global mydfs
	glob += 1
	if comm.author != None and comm.body != None :
		mydfs.append(comm)

	if comm.replies == None:
		return
	for com in comm.replies:
		dfs(com)

def getAllArticles():
	count=0
	dataFolderPath = 'D:\Academ\Fourth Sem\DATA SCI\Project'
	numFiles = len([f for f in os.listdir(dataFolderPath) if os.path.isfile(os.path.join(dataFolderPath, f))])
	
	for i in range(1,2):
	#for i in range(1,numFiles+1):
		print (i)
		path = 'D:\Academ\Fourth Sem\DATA SCI\Project\POST_'
		postNum = i
		path += str(postNum)
		path += '.pkl'
		
		with open(path, 'rb') as input:	

			list1 = pickle.load(input)
			submission = list1[0]
			url = submission.url
			#print url
			unabletoparse = 0
			unabletodown = 0
			retry = 1
			while(retry <= 3):
				article = Article(url)
				article.download()
				if article.html == '':
					print ('Didn\'t download html why??',i,url,'retrying',retry)
					retry += 1
					if retry == 4:
						sett.add(i)
						unabletodown += 1
				else:
					try:
						article.parse()
						if article.text == '':
							print ('Didnt get anything after parsing :( ')
							sett.add(i)
						else:
							subCommentMap[submission.id] = article
							count += 1
						break
					except:
						print ('Unable to parse retrying', retry)
						sett.add(i)
						unabletoparse += 1
						break
						
			
	print ('****************')
	print (numFiles)
	print (count)
	print (unabletoparse)
	print (unabletodown)


print ('Started Saving artricle')
print (datetime.datetime.fromtimestamp(time.time()).strftime('%c'))

print ('Startting newspaper code')
#getAllArticles()
print ('Got all articles')


#sid = SentimentIntensityAnalyzer()

dataFolderPath = 'D:\Academ\Fourth Sem\DATA SCI\Project' 
numFiles = len([f for f in os.listdir(dataFolderPath) if os.path.isfile(os.path.join(dataFolderPath, f))])

print ('Binning Comments')
print (datetime.datetime.fromtimestamp(time.time()).strftime('%c'))
bucketDictionary['1']=[]
bucketDictionary['2']=[]
bucketDictionary['3']=[]
#for i in range(1,numFiles+1):
for i in range(1,2):
	if i in sett:
		continue
	path = 'D:\Academ\Fourth Sem\DATA SCI\Project\POST_\POST_'
	postNum = i
	path += str(postNum)
	path += '.pkl'
	
	with open(path, 'rb') as input:	
		
		list1 = pickle.load(input)
		submission = list1[0]
		firstLevelComments = list1[1:]
		
		for comm in firstLevelComments:
			dfs(comm)
		for j in range(0,len(mydfs)):
			comm = mydfs[j]  #the actual comment is mydfs[i] , mydfs is the total number of comments
			
			if (len(comm.body)<140):
				bucketDictionary['1'].append(comm)
				
			elif (len(comm.body)>=140) and (len(comm.body)<300):
				bucketDictionary['2'].append(comm)
				
			else:
				bucketDictionary['3'].append(comm)
			#print bucketDictionary
			
						#print text2

	del mydfs[:]

totalcomm=0

binlist=['1','2','3']
for k in binlist:

	numOfComments = 0
	aLinks=0.0
	vLinks=0.0
	sdLinks=0.0
	LinksList=[]
	numOfComments=len(bucketDictionary[k])
	totalcomm += numOfComments
	print ("printing the comment of respective bins %s" %(k))
	print ("*************************************************************************************************************")
	for comm in bucketDictionary[k]:
		comment = u''.join(comm.body).encode('utf-8').strip()
		text2=str(''.join([m if ord(m) < 128 else ' ' for m in comment]))
		#print text2
		urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text2)

		aLinks += len(urls)
					
	aLinks /= numOfComments
	for comm in bucketDictionary[k]:
		comment = u''.join(comm.body).encode('utf-8').strip()
		text2=str(''.join([m if ord(m) < 128 else ' ' for m in comment]))
		#print text2
		urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text2)
		Links = len(urls)
		LinksList.append(Links)
		vLinks= (Links-aLinks)*(Links-aLinks)			
	vLinks /= numOfComments
	sdLinks= sqrt(vLinks)		
	
	print ("Total number of comments", numOfComments)
	print ("Average number of Links",aLinks)
	print ("Variance of number of Links", vLinks)
	print ("sd of number of Links", sdLinks)
	print ("Maximum value of number of url's", max(LinksList))
	print ("Minimum value of number of url's", min(LinksList))
	print ("*********************************************************************************************")
print ('Binning Done')
print (datetime.datetime.fromtimestamp(time.time()).strftime('%c'))
print (totalcomm)
print (datetime.datetime.fromtimestamp(time.time()).strftime('%c'))
