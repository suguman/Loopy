#import statistics

OUTPUTDIR = "OUTPUT/"
FILES = "Data/"
timeout = 300

df = 3

#No. of states
beginStateNum = 25
endStateNum = 1500
intervalStateNum = 25

#Trans ratio
beginRatio = 25
endRatio = 36
intervalRatio = 5

#Wt values
beginWt = 4
endWt = 5
intervalWt = 1

#Mo of aut of each parameter
autNo = 50

ltTotal = {}
#ltRabit = {}
leqTotal = {}
#leqRabit = {}


for stateNum in range(beginStateNum, endStateNum, intervalStateNum):
    for ratio in range(beginRatio, endRatio, intervalRatio):
        for wtVal in range(beginWt,endWt, intervalWt):
            root = "_".join([str(k) for k in [stateNum, ratio, wtVal, df]])
            #print root
            ltTotal[root] = []
            #leqTotal[root] = []
            for i in range(autNo):
                for ineq in ["lt"]:
                    rootname = "_".join([str(k) for k in [stateNum, ratio, wtVal, i, df, ineq]])
                    #rootoutput = rootname + "_" + str(df) +"_" + ineq
                    outputfile = OUTPUTDIR + rootname + ".txt"
                    #print root, rootname, outputfile
                    fileOut = open(outputfile, "r")
                    #print "Opened file"
                    line = fileOut.readline()
                    time = float(line.strip().split(" ")[4])
                    #print line, first
                    print line, time
                ltTotal[root].append(time)
            print ltTotal
                    

def median(l, num):
    
    if (num%2 ==1):
        index = (num)//2
        return l[index]
    else:
        index1 = num//2
        index2 = index1-1
        return (l[index1]+l[index2])/2
        
for stateNum in range(beginStateNum, endStateNum, intervalStateNum):
    for ratio in range(beginRatio, endRatio, intervalRatio):
        for wtVal in range(beginWt,endWt, intervalWt):
            
            root = "_".join([str(k) for k in [stateNum, ratio, wtVal, df]])
            print root
            (ltTotal[root]).sort()
            #(leqTotal[root]).sort()

            print ltTotal[root], median(ltTotal[root], autNo)

            outfilename = "_".join([str(ratio), str(wtVal), str(df)])
            f1 = open(FILES + outfilename + ".txt", "a+")
            #f1.write("Hello\n")
            #ss = " ".join([str(stateNum), "lt", str(median(ltRabit[root], autNo)), str(median(ltTotal[root], autNo)), "leq", str(median(leqRabit[root], autNo)), str(median(leqTotal[root], autNo))])
            ss = " ".join([str(stateNum), "lt", str(median(ltTotal[root], autNo))])
            f1.write(ss + "\n")
