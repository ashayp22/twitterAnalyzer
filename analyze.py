# Copyright (c) 2018 Ashay Parikh
import json
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import re
import json
import nltk
import pprint
import operator

word = "trump"

#path
tweets_data_path = r"" #set text file path

tweets_data = []
tweets_file = open(tweets_data_path, "r")

#adds each tweet to array
for line in tweets_file:
    try:
        tweet = json.loads(line)
        tweets_data.append(tweet)
    except:
        continue


print(len(tweets_data))

#-------------------------------------------------------------------------

#only gets the coordinate part of the JSON, including coordinate and type
coor = []
string = ""

def setCoor():
    for i in range(0, len(tweets_data)):
        if(tweets_data[i]["coordinates"] is not None):
		          coor.append(tweets_data[i]["coordinates"])

def addToString():
    for k in range(0, len(coor)):
	       string += str(coor[k]["coordinates"])
	       string += ","

    string = string[:-1]


def text():
    f = open(outputfilename, 'w')
    f.write(string)

def csv():
    df = pd.DataFrame(coor)
    df.to_csv(outputfilename)

def doCoor():
    setCoor();
    addToString();
    #text();
    #csv();


#doCoor();


#-------------------------------------------------------------------------
#KEYWORD CODE

#returns true if word is found in text, else false
def word_in_text(word, text):
    word = word.lower()
    text = text.lower()
    match = re.search(word, text)
    if match:
        return True
    return False

def getRelevantTweets(keyword): #gets all the relevant tweets
    tweets = pd.DataFrame() #makes a data frame
    tweets['text'] = list(map(lambda tweet: tweet['text'], tweets_data)) #adds the text of all tweets to the data frame
    #makes two columns or rows(don't know but not important) and sets it to True or False depending on if the words are found
    tweets[keyword] = tweets['text'].apply(lambda tweet: word_in_text(keyword, tweet))
    #loop check if each tweet is True for positive and negative, adding it to the corresponding array only if its language is English
    passed = []
    for j in range(0, len(tweets[keyword])):
        if(tweets[keyword][j] == True and tweets_data[j]["lang"] == "en"):
            passed.append(filterText(tweets_data[j]["text"]))
    return passed


def filterText(string): #filters the tweets so it can be analyzed without unnecessary parts
	newString = ""

    #gets rids of retweet
	if(string[0:2] == "RT"):
		newString = string[3:]
    #gets rid of # and @
	newString = " ".join(filter(lambda x:x[0]!='@', newString.split()))
	newString = " ".join(filter(lambda x:x[0]!='#', newString.split()))

	if(newString == ""): #in case it was already good, "" won't be returned
		newString = string

	return newString


def pos(document): #returns a tweet POS tagged
	sentences = nltk.sent_tokenize(document)
	sentences = [nltk.word_tokenize(sent) for sent in sentences]
	sentences = [nltk.pos_tag(sent) for sent in sentences]
	return sentences[0]

def getImportant(chunked): #returns the chunked part/part that matched
	chunkOfImportant = []
	for subtree in chunked.subtrees(filter=lambda t: t.label() == 'Chunk'): #if it's label is Chunk, it returns
		chunkOfImportant.append(subtree)
	return chunkOfImportant

def getPhrase(chunk): #gets the phrase
	fullText = ""
    #splits up the tuples/list structure its in, and returns only the string/text
	for i in range(0, len(chunk)):
		fullText += chunk[i][0]
		fullText += " "
	return fullText[:-1]

def evalTweet(string): #chunks the tweet
    tag = pos(string)
    #gram
    #chunkGram = "Chunk: {<DT>?<JJ>*<NN>*<NNP>*}" #includes nouns and proper nouns
    #chunkGram = "Chunk: {<JJ>*<NNP>*}" #includes proper nouns
    chunkGram = "Chunk: {<NNP>*}"
    chunkParser = nltk.RegexpParser(chunkGram)
    chunked = chunkParser.parse(tag)
    importantChunked = getImportant(chunked) #gets the important parts
    allText = []

    for i in range(0, len(importantChunked)):
        allText.append(getPhrase(importantChunked[i])) #gets the phrase from the important parts

    return allText #returns array of all text from tweet

def getAllText(tweets): #evaluates its tweet
	arr = []
	for i in range(0, len(tweets)):
		arr.append(evalTweet(tweets[i]))
	return arr #returns array of all the tweet's keywords


def ridDuplicates(array): #gets rid of duplicates from array
	newArray = []
	for i in range(0, len(array)):
		Bool = False
		for j in range(0, len(newArray)):
			if(array[i] == newArray[j]): #checks to see if it already is in array
				Bool = True
		if(not Bool): #if it is new, it appends it to array
			newArray.append(array[i])
	return newArray

def removeIrr(array): #removes irrelevant tweets after chunking and extracting
    newArray = []
    for i in range(0, len(array)):
        keep = True
        for j in range(0, len(array[i])):
            if(array[i][j] == "/"): #removes /
                keep = False
            if(array[i][j] == "@"): #removes @
                keep = False
            val = ord(array[i][j])
            if(not(val == 32 or (val >= 65 and val <= 90) or (val >= 97 and val <= 122))): #removes anything that isn't part of the alphabet
                keep = False

        #removes if it contains the following words
        if(word_in_text(word, array[i])):
            keep = False
        if(word_in_text("’", array[i])):
            keep = False
        if(word_in_text("http", array[i])):
            keep = False
        if(len(array[i]) == 1):
            keep = False
        if(keep): #if nothing set it to False, it appends it
            newArray.append(array[i])
    return newArray

def checkInArr(arr, char): #check if value is in array, self-explanatory
	for i in range(0, len(arr)):
		if(arr[i] == char):
			return True
	return False



def checkForRepeats(array): #checks for repeats in an array, adding the words that repeat a numerous amount of times
	repeating = []
	temp = []
	for i in range(0, len(array)):
		times = 0
		for j in range(0, len(temp)):
			if(array[i] == temp[j] and not checkInArr(repeating, array[i])):
				times += 1
				if(times == 20): #number of times it has to repeat
					repeating.append(array[i])
					break
		temp.append(array[i])
	return repeating #returns the repeats

def sortKeys(arr): #sorts the keys based on how many times it repeated
    dict = {} #dictionary of the keywords and how many times they repeat
    for i in range(0, len(arr)):
        keys = list(dict)

        if(arr[i] in keys):
            dict[arr[i]] += 1
        else:
            dict[arr[i]] = 1

    sortedV = sorted(dict.items(), key=operator.itemgetter(1)) #returns tuple

    return sortedV


def plotPie(x, labels, title):
    colors = ["red", "orange", "yellow", "green", "blue", "purple", "indigo", "pink"]
    plt.pie(x, explode=None, labels=labels, colors=colors)
    plt.title(title)
    plt.show()


def analyzeKeyword(): #main function, calls everything else
    wordText = getRelevantTweets(word) #text of relevant tweets for the word

    #gets rid of duplicate tweets
    wordText = ridDuplicates(wordText)

    #gets all the text, but in two dimensional form with each row representing one tweet
    temp1 = getAllText(wordText)

    posKey = []

    #adds the text to an array of all tweets
    for i in range(0, len(temp1)):
        for j in range(0, len(temp1[i])):
            posKey.append(temp1[i][j])


    wordKey = removeIrr(posKey) #removes irrelevant tweets



    #sorts the tweets
    sortedWord = sortKeys(posKey)

    #print(sortedPos)
    #print(sortedNeg)

    for z in range(1, 11):
        print(sortedWord[len(sortedWord)-z])
	
    label = [];
    values = [];

    for z in range(1, 21):
        label.append(sortedPos[len(sortedPos)-z][0])
        values.append(sortedPos[len(sortedPos)-z][1])

    print(label);
    print(values);

    plotPie(values, label, "Keywords Associated with " + word);

    print("done")



analyzeKeyword()
