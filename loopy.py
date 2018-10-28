from math import floor
import sys
import time

a = "a"
b = "b"


filename1 = sys.argv[1]
filename2 = sys.argv[2]
df = int(sys.argv[3])
ineq = sys.argv[4] # values are lt and leq
outputfilename = sys.argv[5]

#aut transitions are in the form aut[src][alpha][wt] = destinationList
def parse(filename):
    f = open(filename)
    initial = f.readline()
    blank = f.readline()
    aut = {}
    line = f.readline()

    while(line!="" and line!="\n"):
        #print line
        l = line.strip().split(",")
        #print l
        alpha, statestr, wt = l[0], l[1],int(l[2])
        s = statestr.split("->")
        src, dest = int(s[0]), int(s[1])
        #print src, alpha, wt, dest
        try:
            k = aut[src]
        except KeyError,e:
            aut[src] = {}

        try:
            k = aut[src][alpha]
        except KeyError, e:
            aut[src][alpha] = {}

        try:
            if dest not in aut[src][alpha][wt]:
                aut[src][alpha][wt].append(dest)
        except KeyError, e:
            aut[src][alpha][wt] = [dest]
            
        line = f.readline()

        #print aut
    
    #print aut
    f.close()
    return aut

aut1 = parse(filename1)
aut2 = parse(filename2)


#global values

maxWt = 4
#df = 3
threshold = int( floor(float(maxWt)/(df-1))) + 1
print maxWt, df, threshold
#state tuple size
tuplesize = 4
accept = "Accept"
reject = "Reject"
#transition function on RHS Q, since subset transition function is invoked multiple times
transq = {}
#storage for opt state transitions on alpha and weight
transopt = {}

#Reach function to check if a state has been reached or not
reach = {}
#State is on stack, currently
stacked = {}


#Write auxilary functions here

sep1 = "_"
sep2 = "&"
sep3 = ","
sep4 = "$"
#state: [state in second comaparator, (state set in p, index of current run),  [state set in q], {dictionary over \mu and state set in q}]
def stringifyopt(opt):
    state3str = ""
    for k in opt.keys():
        temp = str(k)+sep2 + sep1.join([str(el) for el in opt[k]])
        state3str += temp + sep4
    #print "STRINGIFY", opt, state3str
    return state3str

def stringify(stateSet):
    state0 = stateSet[0]
    state1 = stateSet[1]
    state2 = stateSet[2]
    state3 = stateSet[3]
    #print state0, state1, state2, state3, stateSet

    state0str = str(state0)
    state1str = sep1.join([str(temp) for temp in state1[0]]) + sep2 + str(state1[1])
    state2str = sep1.join([str(temp) for temp in state2])
    state3str = stringifyopt(state3)

    return state0str + sep3 + state1str + sep3 + state2str + sep3 + state3str

#check if a valid state has been reached already
def access(state):
    try:
        present = reach[state]
        return present
    except KeyError, e:
        return False

def loop(state):
    try:
        onstack = stacked[state]
        return onstack
    except KeyError, e:
        return False

def nextword(alpha):
    if alpha == a:
        return b
    if alpha == b:
        return "NA"


#state: [state in second comaparator, [state in p],  [state set in q], {dictionary over \mu and state set in q}]
#state in p also stores the run no. 
def destination(stateSet, alpha, wtp, wtq): 
    state0 = stateSet[0]
    state1 = stateSet[1]
    state2 = stateSet[2]
    state3 = stateSet[3]
    #print state0, state1, state2, state3, stateSet

    destSet = []

    #Making comparator state for wtp - wtq
    if state0 == accept:
        dest0 = accept
    else:
        dest0temp = df*state0 + (wtp - wtq)
        if dest0temp <= (-1*threshold): #wtp - wtq is a bad prefix for wtp - wtq >= 0
            dest0 = []
        elif dest0temp >= threshold: #in this case, wtp-wtq > 0 is guaranteed 
            dest0 = accept
        else:
            dest0 = dest0temp
    destSet.append(dest0)

    #Make next state in aut1
    try:
        destp = (aut1[state1[0][state1[1]]][alpha][wtp],0)
    except KeyError, e:
        destp = []
    destSet.append(destp)

    #Make destq (destq0), and update transq
    destq = []
    srcstr = sep1.join([str(el) for el in state2])+sep2+alpha + sep2 + str(wtq)
    try:
        destq = transq[srcstr]
        #print "Accessing from trans", "_".join([str(el) for el in srcq0])+sep1+guess1
    except KeyError, e:
        destq = []
        for elem in state2:
            try:
                destElem = aut2[elem][alpha][wtq]
            except KeyError, e:
                destElem = []
            for dest in destElem:
                if dest not in destq:
                    destq.append(dest)
        destq.sort()
        transq[srcstr] = destq
    destSet.append(destq)

    #Making dictionary state, and updating transopt
    counter = False
    state3str = stringifyopt(state3)
    try:
        destopt = transopt[state3str+sep3+alpha+sep3+str(wtq)]
    except KeyError, e:
        #TODO
        tempdict = {}
        for k in state3.keys():
            #print "k val", k, state3[k]
            if counter == True:
                break   
            for i in range(maxWt+1):
                gap = k*df + (wtq - i)
                #print k, i, wtq, gap
                if gap >= threshold:
                    #Can we do nothing? Never have a state for accept
                    gap = accept
                    #tempdict[accept] = []
                elif gap <= (-1*threshold): #wtq is dominated by another run in Q
                    #If states from here are non-empty, counter example found.
                    #Else, false alarm
                    srcstr = sep1.join([str(el) for el in state3[k]])+sep2+alpha + sep2 + str(i)
                    try:
                        lc = transq[srcstr]
                    except KeyError, e:
                        destq = []
                        for elem in state3[k]:
                            try:
                                destElem = aut2[elem][alpha][i]
                            except KeyError, e:
                                destElem = []
                            for dest in destElem:
                                if dest not in destq:
                                    destq.append(dest)
                        destq.sort()
                        transq[srcstr] = destq
                        lc = transq[srcstr]
                    #print k,":", state3[k], alpha, wtq, i, gap, ":", lc
                    if lc!=[]:
                        #print "weight not correct"
                        counter = True
                        break
                else:    
                    srcstr = sep1.join([str(el) for el in state3[k]])+sep2+alpha + sep2 + str(i)
                    #print srcstr
                    #print transq
                    destq = []
                    try:
                        l = transq[srcstr]
                    except KeyError, e:
                        for elem in state3[k]:
                            try:
                                destElem = aut2[elem][alpha][i]
                                #print "destElem", destElem
                            except KeyError, e:
                                destElem = []
                            for dest in destElem:
                                if dest not in destq:
                                    destq.append(dest)
                        destq.sort()
                        transq[srcstr] = destq
                        l = transq[srcstr]
                    #print transq
                    #print transq[srcstr]
                    try:
                        dummy  = tempdict[gap]
                    except KeyError,e:
                        #assign a value only if the gap value in new dictrionay can be non-empty
                        if l!=[]:
                            tempdict[gap] = []
                    if l!=[]:
                        for elem in l:
                            if elem not in tempdict[gap]:
                                tempdict[gap].append(elem)
                    #print k,":", state3[k], alpha, wtq, i, gap, ":", l
                for key in tempdict.keys():
                    #print tempdict
                    tempdict[key].sort()

        if counter == False:
            transopt[state3str+sep3+alpha+sep3+str(wtq)] = tempdict
            destopt = tempdict
    if counter == True:
        destopt = []        
    destSet.append(destopt)
    
    return destSet


#main program here
def main():
    startTime = time.time()
    #initstate = [0, ([1],0),[1],{0:[0]}]
    initstate = [0,([0],0), [0],{0:[0]}]
    firstword = a
    firstweight = 0

    stateStack = []
    wordStack = []
    weight1Stack = []
    weight2Stack = []

    stateStr = stringify(initstate)
    reach[stateStr] = True
    stateStack.append(initstate)
    stacked[stateStr] = True
    wordStack.append(firstword)
    weight1Stack.append(firstweight)
    weight2Stack.append(firstweight)

    print "Aux dictionaries"
    print reach
    print stacked
    print transopt
    print "work stacks"
    print stateStack
    print wordStack
    print weight1Stack
    print weight2Stack
     
    flagOver = False
    numloop = 0
    while(stateStack!=[]):
        #Get top most element without removeing element
        numloop +=1
        #print numloop
        
        state = stateStack.pop()
        stateStack.append(state)
        word = wordStack.pop()
        wordStack.append(word)
        guess1 = weight1Stack.pop()
        weight1Stack.append(guess1)
        guess2 = weight2Stack.pop()
        weight2Stack.append(guess2)

        #print "Aux dictionaries"
        #print reach
        #print stacked
        #print transopt
        #print "work stacks"
        #print stateStack
        #print wordStack
        #print weight1Stack
        #print weight2Stack
    
        newstate = destination(state, word, guess1, guess2)
        print state, word, guess1, guess2, newstate
        #print transopt
        
        #Returns tuplesize if [] is not in the newstate, else returns index of first occurence of [] in tuple
        try:
            emptyat = newstate.index([])
        except ValueError, e:
            emptyat = tuplesize
        reachable = False

        print emptyat
        #print newstate
        if emptyat == tuplesize: #valid state
            newstateStr = stringify(newstate)
            if loop(newstateStr): #if state is already on the stack,
                if (ineq == "lt"): # counter example found
                    #print "Counter example found"
                    flagOver = True
                if (ineq == "leq"):
                    #Check if state in first comparator is accepting. if yes, we are done, else we need to extend the same word and weight sequences more (only change run in P)
                    if newstate[0] == accept: #found counterexample
                        flagOver = True
                    else:
                        emptyat = 1 #Chagne run in P
                        
            elif loop(newstateStr) == False and access(newstateStr):
                #not on stack, but has been visited previously
                #this state is not useful -> change the transition
                emptyat = 2 
                reachable = True
                #print "State been visited before, not on loop"
                
            else: #Valid, and state hasn't been visited before. Enter state to the stack.
                stateStack.append(newstate)
                wordStack.append(firstword)
                weight1Stack.append(firstweight)
                weight2Stack.append(firstweight)
                reach[newstateStr] = True
                stacked[newstateStr] = True
                #print "valid new state"
            
        if emptyat == 3:
            #weight2 of word in Q, has found another weight sequence weight' in Q on same word s.t. weight2 < weight'. So, weight2 is not the maximal.
            #increase weight2
            #if weight2 cannot be increased, change weight in P (go to 0) ---> directly change word in P.  (current word in Q is dominated. Need to change word in Q. Must change word in P. Non-optimal solution, change weight in P.
            #False --- No need to do to optimize. Since, if a state is reached that has been visited previously, the reachabiity clause does not continue computation
            #If weigt2 cannot be incresed, w_max is not optimal in Q. Therefore, w_0 is not maximal either. Might as well look at new word in P. So, we look at next word in P.

            print "Inside 3"
            guess2 = guess2 + 1
            if guess2 > maxWt:
                emptyat = -1
            else:
                weight2Stack.pop()
                weight2Stack.append(guess2)

        if emptyat == 2:
            #there is no transition in Q on (word, weight2)
            #increase weight2
            #if weight2 cannot be increased, change weight in P
            #False -- No need to do to optimize. Since, if a state is reached that has been visited previously, the reachabiity clause does not continue computation
            #If weigt2 cannot be incresed: There is no sequence of word with weight2, if weight2 cannot change, we need to change word in Q. So, change word in P. 

            print "Inside 2"
            guess2 = guess2 + 1
            #print guess2, maxWt
            if guess2 > maxWt:
                if reachable == True:
                    emptyat = 1 
                else:
                    emptyat = -1
            else:
                weight2Stack.pop()
                weight2Stack.append(guess2)

       
        
        if emptyat == 1:
            #change run in P
            #if run cannot change, change weight in P
            print "Inside 1"
            stateTemp = state
            #print runPstateset, runPindex
            while(reach[stringify(stateTemp)] == True):
                runPstateset, runPindex = state[1]
                runPindex += 1
                #print runPstateset, runPindex
                if (runPstateset >= len(runPstateset)):
                    emptyat = 0
                    break
                else:
                    stateTemp = [state[0]]+[(runPstateset, runPindex)]  + state[2:]
            if emptyat == 1:
                stateStack.pop()
                stacked[stringify(state)] = False
                stateStack.append(stateTemp)
                stacked[stringify(stateTemp)] = True
                                  
        if emptyat == 0:
            #weight1 - weight2 < 0: There is a run of word on weight sequence weight1 in P s.t. a word with weight sequence weight2 in Q has greater weight.
            #No extension of (word, weight1) will become a counterexample
            #So, find the next weight1
            #If next weight1 doesnt exist, find next word in P. 

            print "Inside 0"
            #print state, newstate
            guess1 = guess1 + 1
            #print guess1, maxWt
            if guess1>maxWt:
                emptyat = -1 #need to change the word
            else:
                weight1Stack.pop()
                weight2Stack.pop()
                stateStack.pop()
                stacked[stringify(state)] = False

               
                weight1Stack.append(guess1)
                weight2Stack.append(firstweight)
                runPstateset, runPindex = state[1]
                stateTemp = [state[0]] + [(runPstateset, 0)] + state[2:]
                stateStack.append(stateTemp)
                stacked[stringify(stateTemp)] = True
                #Can be optimized to check if the state has been visited already, in which case it can look at the next state.
                #if eventually, a new next state cannot be found, emptyat = 0
            
        if emptyat == -1:

            print "Inside -1"
            word = nextword(word)
            if word =="NA":
                wordStack.pop()
                weight1Stack.pop()
                weight2Stack.pop()
                stateStack.pop()
                stacked[stringify(state)] = False
            else:
                wordStack.pop()
                weight1Stack.pop()
                weight2Stack.pop()
                stateStack.pop()
                stacked[stringify(state)] = False
                
                wordStack.append(word)
                weight1Stack.append(firstweight)
                weight2Stack.append(firstweight)
                runPstateset, runPindex = state[1]
                stateTemp = [state[0]] + [(runPstateset, 0)] + state[2:]
                stateStack.append(stateTemp)
                stacked[stringify(stateTemp)] = True
                
        if flagOver == True:
            break

        print "Aux dictionaries"
        print reach
        print stacked
        print transopt
        print "work stacks"
        print stateStack
        print wordStack
        print weight1Stack
        print weight2Stack
        
    endTime = time.time()
    if flagOver == True:
        sol =  "Counterexample found" + " " + str(numloop) + " "+ str(len(reach)) + " " + str(endTime-startTime)
    else:
        sol =  "No Counterexample" + " " + str(numloop) + " "+ str(len(reach)) + " " + str(endTime-startTime)

    return sol

ans = main()
outf = open(outputfilename, "w")
outf.write(ans + "\n")
outf.close()
