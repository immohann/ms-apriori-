# -*- coding: utf-8 -*-


import csv
import itertools
from collections import defaultdict, OrderedDict

# custom 
def readInput(inputfile):
    "read inputfile"
    data = []
    with open(inputfile) as myfile:
      inp = []
      csv_records = csv.reader(myfile)
      for row in csv_records:
        new_list = [int(item) for item in row]
        data.append(new_list)
    # print(data)
    return data

# custom 
def readParam(paramFile):
    "Read the parameter file"

    param = {}
    sdc = 0

    data = readInput("input-data.txt")
    uniq_vals = set(itertools.chain.from_iterable(data))

    file_iter = open("parameter-file.txt", 'r')
    for line in file_iter:
        line = line.replace(" ", "")
        line = line.strip()
        if 'MIS' in line:
            key = line[line.find("(") + 1:line.find(")")]
            val = line[line.find("=") + 1:]
            param[key] = float(val)
            
        elif 'SDC' in line:
            sdc = float(line[line.find("=") + 1:])

    # set rest value to te rest of the elements
    rest = []
    for key,vals in param.items():
      if key == "rest":
        r = vals
      else:
        rest.append(int(key))

    for i in uniq_vals:
      if i not in rest:
        param[str(i)] = r
    
    if 'rest' in param.keys():
        del param['rest']

    param = {int(k):float(v) for k,v in param.items()}
    param = OrderedDict(sorted(param.items()))

    return param, sdc

# custom x modified
def getItemSetTransactionList(data_iterator):
    "returns transactionList, 1-itemSet"

    transactionList = []
    itemSet = set()
    for record in data_iterator:
        transaction = set(record)
        transactionList.append(transaction)
        for item in transaction:
            itemSet.add(item)              
            # Generate 1-itemSets
    # print(itemSet)
    # print(transactionList)
    return itemSet, transactionList

# custom x modified
def joinSet(itemSet, length):
    """Join a set with itself and returns the n-element itemsets"""
    return set([i.union(j) for i in itemSet for j in itemSet if len(i.union(j)) == length])

# to-be modified
def level2_cand_gen(FF, param, sdc, count, maxMIS, transSize):
    "generate cadidates for the 2-itemset"
    s = set(frozenset([w]) for w in FF)
    s2 = joinSet(s, 2)

    Cand = []
    for e in s2:
        minSup = 1
        maxSup = 0

        for r in e:
            if count[r]/float(transSize) < minSup:
                minSup = count[r]/float(transSize)
            if count[r]/float(transSize) > maxSup:
                maxSup = count[r]/float(transSize)

        if maxSup-minSup <= sdc:
            Cand.append(e)

    ## get the lowest MIS (done)
    minMIS = dict()

    for i in Cand:
        min = 1
        max = 0
        maxMISItem = 0
        for j in i:
            if param[j] < min:
                min = param[j]
            if param[j] > max:
                max = param[j]
                maxMISItem = count[j]
        minMIS[i] = min
        maxMIS[i] = maxMISItem
    return Cand, minMIS

# to-be modified
def level_k_cand_gen(L, param, sdc, k, count, maxMIS):
    s2 = joinSet(L, k)

    Cand = []
    for e in s2:
        minSup = 1
        maxSup = 0
        for r in e:
            if param[r] < minSup:
                minSup = param[r]
            if param[r] > maxSup:
                maxSup = param[r]
        if maxSup-minSup <= sdc:
            Cand.append(e)


    ## get the lowest MIS
    minMIS = dict()
    for i in Cand:
        min = 1
        max = 0
        maxMISItem = 0
        for j in i:
            if param[j] < min:
                min = param[j]
            if param[j] > max:
                max = param[j]
                maxMISItem = count[j]
        minMIS[i] = min
        maxMIS[i] = maxMISItem
    
    return Cand, minMIS


def writeOutputFile(outputFile, F, count, maxMIS):
    "Save output in the same format as requested"
    with open(outputFile, 'w') as f:
        k = []
        for key in F:
            k.append(key)
        k = sorted(k)
        for i in k:
            f.write("(Length-%d %d\n\n" % (i,len(F[i])))
            
            for j in F[i]:
                print(len(j))
                if i == 1:
                    tmp = next(iter(j))
                    f.write("\t(%s) \n" % ( tuple(list(j))))
                else:
                    s = []
                    f.write("")
                    st = ""
                    for i in set(j):
                        st+=str(i)
                        st+=" "
                    
                    f.write("\t("+st[:-1]+")\n")

                    
                    # f.write("\t(%s %s) \n" % (tuple(list(set(j)))))
                    

            # f.write("\n\tTotal number of frequent %d-itemsets = %d \n" % (i, len(F[i])))
            f.write(")\n")
            
# to-be modified
def MSA (fileData, parameters, sdc):
    "MSApriori algorithm"
    one, trans = getItemSetTransactionList(fileData)
    # print(parameters.items())
    
    sorted_items = [(k, v) for k, v in sorted(parameters.items(), key=lambda item: item[1])]
    
    
    # sorted_items = sorted(parameters.items(), key=operator.itemgetter(1))
    transSize = len(trans)

    print("Working on 1 itemset ......")
    ## construct the M
    M =[]
    for i in (sorted_items):
        M.append(i[0])
    print("M",M)
    ## get the count
    count=defaultdict(int)
    for item in M:
        for transaction in trans:
            m={item}
            if m.issubset(transaction):
                count[item] += 1

    # print(count)
    ## Initial pass
    L=[]
    start = 0
    pivot = 0
    for i in M:
        print(i,count[i],parameters[i],pivot)
        if count[i]/float(len(trans)) >= parameters[i] and start == 0:
            L.append(i)
            start = 1
            pivot = parameters[i]
        elif count[i]/float(len(trans))  >= pivot and start == 1:
            L.append(i)

    # print(L)

    ## select the 1-frequentset
    F = dict()
    F_local = []
    for i in L:
        if count[i] / float(len(trans))  >= parameters[i]:
            F_local.append({i})
    ### Check constrains
   
    F[1] = F_local


    ### for the rest of set-size
    k = 2
    maxMIS = dict()
    while(len(F[k-1]) != 0):
        print("Working on",k,"itemset ......")
        if(k==2):
            C, minMIS = level2_cand_gen(L, parameters, sdc, count, maxMIS, transSize)
        else:
            C, minMIS = level_k_cand_gen(F[k - 1], parameters, sdc, k, count, maxMIS)

        ## Get the count
        for item in C:
            for transaction in trans:
                if item.issubset(transaction):
                    count[item] += 1

        ## Select the items fro the k-frequent itemset
        F_local = []
        for item in C:
            if count[item] / float(len(trans))  >= minMIS[item]:#parameters[list(item)[0]]:
                F_local.append(item)

        ##### Check constrains
       
        F[k] = F_local

        k+=1
    del(F[k-1])
    return F, count, maxMIS

if __name__ == "__main__":

    fileData = readInput("input-data.txt")
    parameters, sdc = readParam("parameter-file.txt")

    F, count, maxMIS = MSA(fileData, parameters, sdc)

    ### Create the outputfile
    writeOutputFile("outFile.txt", F, count, maxMIS)
    print("\n DONE \n")
