import csv
import regex as re
import json
import pandas as pd

def writeToFile(sloDat):
    #write to json file. indent is used for spacing
    with open("db.json", "w") as f:
        json.dump(sloDat, f, indent = 2)

def splitText(list, char):
    splitList = []

    #splits text on colons
    for dat in list:
        #splits on whatever character is passed in
        splitList.append(dat.split(char))
    
    return splitList

def createKeys(sloSplit, sloDict):
    for data in sloSplit:
        if re.search("^SLO", data[0]):
            #grabs the first and last characters in the string and concats to create slo key
            #eg if data[0] = SLO1, this line grabs S & 1, concats and creates S1
            sloKey=str(data[0][0] + data[0][-1])
        
            #creates a dictionary/object as the value for each key
            sloDict[sloKey] ={}
            sloDict[sloKey]["description"] = data[1]

def addMeasuresToDict(sloSplit, sloDict):
#Uses regular expression to search the measure description for specific keywords
    #Then makes the measure a value to an SLO based on those keywords
    for data in sloSplit:
        if re.search("Test|Problem", data[-1]):
            sloDict["S1"][data[0]] = {}
            sloDict["S1"][data[0]]["description"] = data[-1]
        
        elif re.search("Presentation|Writing|Grammar", data[-1]):
            sloDict["S2"][data[0]] = {}
            sloDict["S2"][data[0]]["description"] = data[-1]
        
        elif re.search("Evaluation|Partner", data[-1]):
            sloDict["S3"][data[0]] = {}
            sloDict["S3"][data[0]]["description"] = data[-1]

        elif re.search("Describe|Solutions", data[-1]):
            sloDict["S4"][data[0]] = {}
            sloDict["S4"][data[0]]["description"] = data[-1]

    #Should be added as a measure to each SLO  
    for key, val in sloDict.items():
        sloDict[key]["M14"]= {}
        sloDict[key]["M14"]["sescription"] = "Indirect Measures"

def addTargetsToDict(targetDat, sloDict):
    reg ='[A-Z][0-9]+'
    for data in targetDat:
        #splits "S1M1T1" based on regular expression which says to split on a letter (uppercase)
        #and one or more digit. This creates an array with 3 elements ['S1','M1','T1']
        target = re.findall(reg,data[0])

        #uses array values to create target keys which have a dictionary as the value
        sloDict[target[0]][target[1]][target[2]] = {}

        #HARD CODED AND NEEDS TO BE FIXED TO ACCOMODATE DATA WITH OTHER DATES
        #creates and initializes target subkey (which is the date)
        sloDict[target[0]][target[1]][target[2]]["17-18"] = {}

        #grabs digits
        trgt_1 = re.findall("\d+",data[3])
        trgt = int(trgt_1[0])
        print(trgt)

        #if statements chekc for empty strings
        if data[4] == "":
            percentMet = 0
        else:
            percent_Met = re.findall("\d+",data[4])
            print(percent_Met)
            percentMet = int(percent_Met[0])
    

        if data[2] == "":
            num_stud_met = 0
        else:
            num_stud_met = int(data[2])  

        #creates and initializes date subkeys
        sloDict[target[0]][target[1]][target[2]]["17-18"]["target"] = trgt
        sloDict[target[0]][target[1]][target[2]]["17-18"]["num_student"] = int(data[1])
        sloDict[target[0]][target[1]][target[2]]["17-18"]["num_student_met"] = num_stud_met
        sloDict[target[0]][target[1]][target[2]]["17-18"]["percentage"] = percentMet
        sloDict[target[0]][target[1]][target[2]]["17-18"]["description"] = data[5]


def createDict(sloList, targetList):
    #Calls all functions needed to populate the dictionary
    sloDict = {}
    createKeys(sloList, sloDict)
    addMeasuresToDict(sloList, sloDict)
    addTargetsToDict(targetList, sloDict)
    writeToFile(sloDict)

    return sloDict

def readData():
    """ I was trying out a dataframe which we might eventually need to use to access different cells"""
    #reads from SWEDatafile.csv
    # targets = pd.read_csv("SWEDatafile.csv", header = 0)
    # targets.reset_index().set_index('Measures')

    #line below cause program to throw a NoneType not subscriptable error
    # targets = targets.dropna(how = 'all', inplace = True)
    # print(targets)
    # row1 = [targets.iloc[1][:7]]



    #Reads from SLOmtarix file
    with open("SLOsMatrix.csv") as f:
        #converts to a list
        data = list(csv.reader(f))

    #grabs data from first row and stores in data variable
    data = data[1:]

    #gets the slo1 index 
    sloInfoIndex = data[0].index('SLO1: Program Development')

    #List comprehension to get all the data in the sloInfoIndex column
    sloInfo = [row[sloInfoIndex] for row in data]
    sloInfoSplit = splitText(sloInfo, ":")

    #reads from SWEDatafile.csv
    with open("SWEDatafile.csv","r") as f:
        tData = list(csv.reader(f))

    #grabs data from first row and stores in data variable
    targetDat = tData[1:]

    return sloInfoSplit, targetDat

if __name__ == "__main__":
    sloData, targetData = readData()
    sloDict = createDict(sloData, targetData)


