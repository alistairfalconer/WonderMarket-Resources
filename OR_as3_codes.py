#The 3 communications are handled by the functions:
    #Communication 1: V_com1(f,m), solution given by V_com1(0,8)=[$1415.3, 3]
    #Communication 2: total_com2(t,s3), solution given by total_com2(0,[0,0,0])=$3091.2
    #Communication 3: V_com3(t,f,s,l), solution given by V_com3(0,0,[0,0,0],14)=[$2158.95, 6]

###############################################
#                   Communication 1: Optimising Display                             #
###############################################


#stages f represent which fridge we're currently considering
#state m represents no. display spots left
#action a represents how many fridges of type f to commit to display

F = ['Alaska','Elsa','Lumi']#Types of fridges

P = [142,	107,	102]#profit from sale of each type

Displayed = [
	[0.0,    1.9,	3.6,	4.6,	4.8],
	[0.0,	1.6,	3.5,	4.4,	4.8],
	[0.0,	0.0,	2.7,	3.8,	4.3],
            ]            #Displayed[f][n]=expected sales after displaying n fridges
            
Max_Spaces=8

def expected_profit(f,a):#expected profit from displaying a fridges of type f
    return P[f]*Displayed[f][a]
    

def V_com1(f,m):#value function
    if f == len(F):#out of fridge types
        return [0,0]
    val=0
    act=0
    for a in range(min(m+1,5)):#list of possible actions
        test = expected_profit(f,a)+V(f+1,m-a)[0]#short-term+long-term profit
        if test >= val:
            val = test
            act = a
    return [val,act]


###############################################
#                   Communication 2: Optimising Warehouse                       #
###############################################

#This is a basic dynamic programming problem, with the only complexity coming from handling the stochastic demand. 

#stages t represent which week we're considering
#state s,f represents the amount of fridges of type f in storage
# action a is the number of fridges if the considered type we order in the given week, we never want more than 6 fridges in storage

#The function V_com2(t,s,f) runs the optimisation for fridge type f {0,1,2} only, starting from week t {0,1,2,3} with s {0 <= s <= 6} in storage

# the function total_com2(t,s) runs V_com2(t,s,f) for each value f, and sums the profit, returning our optimal expected profit, note that 
# this s input is a 3-list, with each input the initial storage of each fridge-type 
# The answer to the communication is then given by total_com2(0,[0,0,0])=3091.2

F = ['Alaska','Elsa','Lumi']#Types of fridges



storage=30#cost to store a fridge for a week

Prob = [
        [0,0.00,	0.08	,0.24,	0.30	,0.26,	0.12],
         [0,0.11,	0.26	,0.31,	0.20	,0.12,	0.00],
         [0,0.12	,0.20,	0.36	,0.24,	0.08	,0.00]
         ]#Demand[f][n] returns the probability of selling n fridges of type f, starting from n=0
P = [142,	107,	102]#profit from sale of each type
D=len(Prob[0])
SC=30

_V_com2 = {}
def V_com2(t,s,f):
    if t == 4:
        return [0,0]
    buy = 0
    total = 0
    Profit = P[f] #profit per unit sold
    if (t,s,f) not in _V_com2:
        for a in range(D-s): #how many fridges ordered, never more than max demand in storage
                test = (-SC*(s+a))# storage cost
                test +=(sum(Prob[f][n]*(min(s+a,n)*Profit #Prob of demand * (No. sold * Profit per unit
                              +V_com2(t+1,s+a-min(s+a,n),f)[0]) #+long-term value)
                              for n in range(D))) # for each possible demand
                if test >= total:
                   total = test
                   buy = a
        _V_com2[t,s,f] = [total,buy]
    return _V_com2[t,s,f]

def total_com2(t,s3):
    total=0 
    init = [0]*len(s3)          #write copy of s3
    for i in range(len(s3)):   #''                    ''
        init[i]+=s3[i]              #''                    ''
    for f in range(len(s3)):   
        total+=V_com2(t,init[f],f)[0]   #sum expected profit from each fridge-type
    return total
    
    
###############################################
#                   Communication 3: Optimising Delivery                            #
###############################################
    
#Our general strategy is to use dual-staging, initially we stage with fridge-type f, however the end condition (f ==3) is to 
    #iterate stage t up by one, and reset f to zero. Essentially we have a 2-D stage-space with a winding path through it. 
    # I also prefer a more lengthy maximisation method, as this gives more flexibility to the function without relying unduly on 
    #external functions. 
    #We handle shipping by adding a quantity l to our consideration, this is the number of individual fridges we have left that week,
    #i.e. this is 14 at the start of the week, and every time we order a fridges l is decreased by a, to a minimum of 0. The shipping
    #cost is then determined by saying that the first fridge of each truckload is responsible for the cost of that entire truckload,
    #this is calculated using remainder division in the truck_cost function. 
    
    #stage t represents the week we're at; t in {0,1,2,3}
    #stage f represents which fridge -type we're considering; f in {0,1,2}
    #state s is a 3-list representing the number of fridges of each type currently in storage;  s in {[a,b,c]: 0 <= a,b,c <= 8 }
    #state l is the number of fridges that can still be delivered this week; l in {l: 0 <= l <= 14}, note that this refers to how many
        #individual fridges can be delivered, not the number of deliveries that can be made
    
    #Functions called: 
        #change_s(f,s,change): sets a value temp equal to the change added to the f'th element of s, returns temp,
        #   this is used input a changed state-vector s
        #truck_cost(l,a): indicates the cost of shipping a fridges given l many deliveries left this week
        
    #The answer to the communication is V_com3(0,0,[0,0,0],14)[0]=2158.95
    
F = ['Alaska','Elsa','Lumi']#Types of fridges
Profit = [142,	107,	102]#profit from sale of each type
MaxS=8  #max storage for fridges of each type
Storage_Cost=30 #Cost to store a fridge for a week
fpT=7   #Max no. fridges per truck
maxT=2 #Max no. trucks per week
TC=150 #Cost for each truck

Prob = [
        [0,0.00,	0.08,0.24,0.30,0.26,	0.12],
         [0,0.11,0.26,0.31,0.20,0.12,	0.00],
         [0,0.12	,0.20,0.36,0.24,0.08	,0.00]
         ] #Demand[f][n] returns the probability of selling n fridges of type f, starting from n=0
D=len(Prob[0]) #The number of possible demands
        

def change_s(f,s,change):
    temp=[0]*len(s)         #write a copy of s
    for i in range(len(s)):   #''                    ''
        temp[i]+=s[i]           #''                    ''
        if i == f:                  #find the value to change
            temp[i]+=change #change the value
    return temp                 #return changed list
#Note that we take special care to return a changed version of s without changing s itself, this is to make sure that that each calculated value is written 
    #to the right dictionary entry, as special care must be taken when using a list as a dictionary-index. 
    
def truck_cost(l,a):        #added cost of shipping a fridges, with l remaining in the week, this is used in com3 
    if a > l%fpT:               #l%fpT is remaining in current truckload, this tests if a new truck is required
        return TC*(1+int(a/fpT)) #If a new truck is required, return TC * no. trucks needed for this order a
    return 0                        #if no new trucks required, return 0

_V_com3 = {}
def V_com3(t,f,s,l):
    store=[0]*len(s)             #write a copy of s
    for i in range(len(s)):      #''                    ''
        store[i]+=s[i]              #''                    ''
    index=tuple([t,f]+store+[l])   #index of the relevant dictionary entry
    if (index) not in _V_com3:     #check if value isn't already known
        if f == len(F):                                         #if we're out of fridge-types to assign:
            return V_com3(t+1,0,store,fpT*maxT)         #increase time, consider first fridge-type again, pass s unchanged
        if t == 4:  #time-out stopping condition
            return [0,'time out']
        money = -9999   #initialise values for maximising calculation
        buy = -1            #initialise an action
        for a in range(1+min(l,MaxS-store[f])):  #Constrained by maximum storage and amount that can be delivered in a week
            test = -Storage_Cost*(store[f]+a)-truck_cost(l,a)  #storage and shipping cost
            test += (sum(Prob[f][n]*(min(store[f]+a,n)*Profit[f] #short-term value = prob of demand * No. Sold under that demand* Profit from each sale
            + V_com3(t,f+1,change_s(f,s,a-min(store[f]+a,n)),l-a)[0])  for n in range(D))) #long-term cost = prob of deman* recursion term under that demand       
                         #Note that the long-term value is included in the same summation as the short-term
            if test >= money: #test if we've beaten best value
                money = test  #if so, rewrite best value
                buy = a                     #save action
        _V_com3[index]= [money,buy]  #save best total value after maximisation into dictionary
    return _V_com3[index]            #return best value
    
#Again we take special care to work with a copy of s, store, rather than s itself. This is because early versions of this code had consistent errors concerning passing the value s between 
#   different recursion steps, where different evaluations would save to the same dictionary index as s was being varied within the code. 