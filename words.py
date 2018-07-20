# -*- coding: utf-8 -*-
"""
Created on Sun Jan 21 13:24:01 2018

@author: Bucky
"""

import os
import sys
import re
import matplotlib.pyplot as plt
import datetime

#finds abspath of all text files in this directory (and subdirectories)
def getFiles():
    files = []
    for dirpath, dirnames, filenames in os.walk('.'):
        for s in filenames:
            if s.endswith('.txt'):
                files.append(os.path.join(os.path.abspath(dirpath),s))              
    return files

def getEpoch(absPath):
    return os.path.getctime(absPath)

#finds creation date of file
def getCDate(absPath):
    epoch = getEpoch(absPath)
    #date = time.strftime("%a, %d %b %Y %H:%M:%S %Z", time.localtime(epoch))
    date = datetime.datetime.fromtimestamp(epoch)
    return date
                    

def loadTxt(fileName):
    with open(fileName,'r',errors="ignore") as myFile:
        doc = myFile.read()#.replace('\n',' ')
    return doc

# turns document string into list of word strings
def tokenize(document):
    ret = document
    ret = re.sub(' +', ' ', ret) #remove extra whitespace
    ret = ret.strip().split()    #remove leading and trailing whitespace then split on space
    return ret
    
# metadata tag has to be on new line in all caps with a colon after it
# supports multiple of same data in each file (like if you watch multiple movies in one day)
def findMetadata(document):
    data = [] # list of tuples as (TAG, value)
    for line in document.split('\n'):
        t = line.split(':')
        if len(t) >= 2 and t[0].isupper():
            data.append((t[0],t[1]))
    return data

def generateAllMetadata():

    # dictionary where key is metadata tag
    # and value is tuple of two lists storing date and value (done to make plotting easier)    
    metadata = {}
    
    files = getFiles()
    
    numFiles = len(files)
    
    print("ANALYZING " + str(numFiles) + " files...")

    for i,file in enumerate(files):
        #date = str(getCDate(file)).split(' ')[0]
        date = getCDate(file)
        #date = getEpoch(file)
        
        doc = loadTxt(file)
        docmd = findMetadata(doc)
        
        for md in docmd:
            k = md[0]
            v = md[1].strip()
            n = v.split(' ')[0]
            if isNumber(n):
                v = n	#just save the number then for plotting
            if k in metadata:
                metadata[k].append((date,v))
            else:
                metadata[k] = [(date,v)]
                
        updt(numFiles, i+1)
                 
    print("DONE")    
    
    return metadata

"""
Displays or updates a console progress bar.
Original source: https://stackoverflow.com/a/15860757/1391441
"""
def updt(total, progress):
    barLength, status = 50, ""
    progress = float(progress) / float(total)
    if progress >= 1.:
        progress, status = 1, "\r\n"
    block = int(round(barLength * progress))
    text = "\r[{}] {:.0f}% {}".format(
        "#" * block + "-" * (barLength - block), round(progress * 100, 0),
        status)
    sys.stdout.write(text)
    sys.stdout.flush()


def isNumber(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


# checks if list is plottable (contains numbers)
def isPlottable(tagList):
    for t in tagList:
        if not isNumber(t[1]):
            return False
    return True

    
def plotTag(tags, metadata): #date value list

    plt.xkcd()
    
    errors = 0
    for tag in tags:        
        if tag not in metadata:
            print ("ERROR: Tag '"+tag+"' not found")
            errors+=1
            continue
        tagList = metadata[tag]
        if not isPlottable(tagList):
            print("ERROR: Tag '"+tag+"' contains non numeric values, cant plot")
            errors+=1
            continue
                 
        tagList.sort() #sorts by date
        
        # seperate tuple list into x and y lists
        xd = [t[0] for t in tagList]                
        yd = [t[1] for t in tagList]                
                    
        plt.plot(xd, yd, '-o', label=tag) #'ro'
    
    if errors >= len(tags):
        return
    
    plt.xlabel('Date')
    
    if len(tags)-errors <= 1:
        plt.ylabel(tag)
    else:
        plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
    
    #fig.autofmt_xdate()
    plt.xticks(rotation=25)
    plt.tight_layout()
    
    #import matplotlib.dates as mdates
    #myFmt = mdates.DateFormatter('%d:%H')
    #ax.xaxis.set_major_formatter(myFmt)
    
    plt.show()

def printHelp():
    print("list - lists the locations of all found files\n" 
          "plot <tag1> <tag2> ... - plots tag(s) over time\n" 
          "help - opens this page\n" 
          "quit/exit - exits program")

    
# this is the function that gets called when you run this python program
if __name__ == "__main__":
        
    print("Hello Mary, welcome to your DATA ANALYZER PROGRAM")

    metadata = generateAllMetadata()

	# TODO list
	# switch to only do when file is created or modified and save a .metadata
	# once above have web lookup for weather at time of file creation
    
    while True:
        inputs = input("Enter command: ").split(' ')
        cmd = inputs[0]
        
        if cmd == "list":
            files = getFiles()
            for file in files:
                print(file)
            
        elif cmd == "test":
            print("this is useless")
            
        elif cmd == "plot":
            if len(inputs) <= 1:
                print("ERROR: need to specify what tags you want to plot")
                continue
            
            plotTag(inputs[1:],metadata)
            
        elif cmd == "exit" or cmd == "quit":
            break
        elif cmd == "help":
            printHelp()
        else:
            print("Unknown command!")
            printHelp()
            
    
    