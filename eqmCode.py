

import numpy as np
import random
import pandas as pd

#####################################################################################################################################
# input from the user
eq= ["+","r","sd","t","=","1*","(","-","C","*","U","*","inv","(","C",")","-","V",")","r","fd","t","+","(","-","C","*","U","*","inv","(","C",")","*","V","+","C","*","L",")","*","r"]

r1=["r","p","s","x","lambda"]  # differential variables
r2= ["L","V","U","C"] # Matrices
r3=["+","-","*"] # Operators
r4= ["inv","tp"] # Matrix unary operators
r5= ["fd","sd"] # differential operators
r6= ["2*","3*"] # Coefficients
r7 = [""]
budget= 50  # budget to generate k equations
brc = ["(", ")", "[", "]", "{", "}", "t","M","="] # ignore brackets and terms of this form
n=20 # number of iterations to search for possible manipulatedequations
p= 8 # length of edit sequence specified by user
k=10 # number of equations needed
manipulatedequations = {} # dictionary with manipulatedequations and their corr. costs

#define costs
editoperatorcost= {"r1":1,"r2":1,"r3":1,"r4":1,"r5":1,"r6":1,"r7":1} # Costs of editing every character in the equation defined by the user for diff equations
#####################################################################################################################################

####################################################################################################################################
# #input from the user
# eq= ["llap","=","-","0.5*","*","{","N","*","[","1","+","log","(","2*","pi",")","+","log","(","sigmahat","^2",")","]","+","M","*","logmod","(","D",")","+","BigSigma_1M","log","[","G","(","beta","D","yi",")","]","}"]
#
# r1=["sigma","sigmahat","N","M","yi","beta","y","lla","llap"]  # differential variables
# r2= ["D"] # Matrices
# r3=["+","-","*","/","^"] # Operators
# r4= ["inv","tp","logmod"] # Matrix unary operators
# r5= ["mod","log","logmod","G","g","gdd","f"] # functions
# r6= ["2*","0.5*"] # Coefficients
# r7= [""] # functions
# budget= 50 # budget to generate k equations
# brc = ["(", ")", "[", "]", "{", "}","BigSigma_1M","=","pi"] # ignore brackets and any other terms of this form
# n=20 # number of iterations to search for possible manipulatedequations
# p= 8 # length of edit sequence specified by user
# k= 10 # number of equations needed
# manipulatedequations = {} # dictionary with manipulatedequations and their corr. costs
#  # either removing the inve(",, ")rse or adding the inverse has the same costs
#
# #define costs
# editoperatorcost= {"r1":1,"r2":1,"r3":1,"r4":1,"r5":1,"r6":1} # Costs of editing every character in the equation defined by the user for diff equations
# #####################################################################################################################################
# eq= ["1*","(","tp","(","mu","fpd","beta",")",")","*","inv","(","V",")","*","1*","(","1*","y","-","1*","mu",")","=","0"]
# r1 = ["mu","y","beta"] # differential variables
# r2 = ["V"] # Matrices
# r3=["+","-","*"] # Operators
# r4= ["inv","tp"] # Matrix unary operators
# r5= ["fpd"] # differential operators
# r6= ["2*","3*"] # Coefficients
# r7= ["mod","^2","^3"] # functions
#
# budget= 50 # budget to generate k equations
# brc = ["(", ")", "[", "]", "{", "}","BigSigma_1M","="] # ignore brackets and any other terms of this form
# identifiers = ["(", "[", "{"]
# n=25 # number of iterations to search for possible manipulatedequations
# p= 8 # length of edit sequence specified by user
# k= 10 # number of equations needed
# manipulatedequations = {} # dictionary with manipulatedequations and their corr. costs
#  # either removing the inverse or adding the inverse has the same costs
# #
# #define costs
# editoperatorcost= {"r1":1,"r2":1,"r3":1,"r4":1,"r5":1,"r6":1,"r7":1}
# # differential operator check nr and dr
# # functions- ability to be added anywhere
#####################################################
#####################################################################################################################################
# eq= ["Sigma","t","=","1*","C","*","tp","(","C",")","+","1*","B","Sigma","t-1","tp","(","B",")","+","1*","A","*","e","t-1","*","tp","(","e","t-1",")","tp","(","A",")"]
# r1 = ["mu","y","beta"] # differential variables
# r2 = ["V"] # Matrices
# r3=["+","-","*"] # Operators
# r4= ["inv","tp"] # Matrix unary operators
# r5= ["fpd"] # differential operators
# r6= ["2*","3*"] # Coefficients
# r7= ["mod","^2","^3"] # functions
#
# budget= 50 # budget to generate k equations
# brc = ["(", ")", "[", "]", "{", "}","BigSigma_1M","="] # ignore brackets and any other terms of this form
# identifiers = ["(", "[", "{"]
# n=25 # number of iterations to search for possible manipulatedequations
# p= 8 # length of edit sequence specified by user
# k= 10 # number of equations needed
# manipulatedequations = {} # dictionary with manipulatedequations and their corr. costs
#  # either removing the inverse or adding the inverse has the same costs
#
# #define costs
# editoperatorcost= {"r1":1,"r2":1,"r3":1,"r4":1,"r5":1,"r6":1,"r7":1}
# # differential operator check nr and dr
# # functions- ability to be added anywhere
# #####################################################
#####################################################################################################################################
# eq= ["(","lambda",")","^2","=","-","4*","(","1*","sin2","(","0.5*","kx","*","delx",")","/","delx2","+","1*","sin2","(","0.5*","ky","*","dely",")","/","dely2","+","1*","sin2","(","0.5*","kz","*","delz",")","/","delz2",")"]
# r1 = ["kx","ky","kz","delx","dely","delz",] # differential variables
# r2 = [""] # Matrices
# r3=["+","-","*","/"] # Operators
# r4= ["inv","tp"] # Matrix unary operators
# r5= [""] # differential operators
# r6= ["2*","3*","0.5*","0.33*","0.20*","5*","4*"] # Coefficients
# r7= ["sin2","sin","sininv"] # functions
#
# budget= 50 # budget to generate k equations
# brc = ["(", ")", "[", "]", "{", "}","lambda","="] # ignore brackets and any other terms of this form
# identifiers = ["(", "[", "{"]
# n=25 # number of iterations to search for possible manipulatedequations
# p= 8 # length of edit sequence specified by user
# k= 10 # number of equations needed
# manipulatedequations = {} # dictionary with manipulatedequations and their corr. costs
#  # either removing the inverse or adding the inverse has the same costs
#
# #define costs
# editoperatorcost= {"r1":1,"r2":1,"r3":1,"r4":1,"r5":1,"r6":1,"r7":1}
# # differential operator check nr and dr= done
# # functions- ability to be added anywhere= to be discussed
# # separate set for exponents= to be done
#####################################################
###### Main function kind of ####

#def Gmain():

    # read csv of input equations, constraints, budget
    # assign it to lists as above
    #  call the function passing the above as arguments
#


 # input variable return var + coeff
def gencoeff(ch):
    coeff= r6[random.randint(0,len(r6)-1)]
    if coeff != "1":
        return coeff+"*"+ch
    else:
        return ch


#converting original equation to string
eqn_orig = ""
for c in eq:
    eqn_orig = eqn_orig +c

eqns_modified = []


### Begin generate n equations and compute their cost.
for j in range(1,n):
    eq1= eq.copy()
    #print(eq)
    eqn_mod = ''

    editcost=0
    cleanterm= []
    xy= []

    #ignoring brackets from equation and generating random terms for manipulation
    nums= list(range(0, len(eq)-1))
    indices = [i for i, x in enumerate(eq) if x in brc]
    # print(indices)
    nobracketseq = [x for x in nums if x not in indices]
    ling=random.sample(nobracketseq,p)
    #print(ling)

    editsequence = ""

    editcost = 0
#for every term perform an edit and compute the cost of the edit
    for i in ling:
        # print(eq[i])
        #check for unary operators
        term = eq[i]

#Case- Variables that are  differentiable
        if term in r1:
            eq1[i] = r1[random.randint(0,len(r1)-1)]
            #Checking for numerator and denominator of a differential. OR. left and right of a binary operator
            #The same code also works for any function that has 2 variables such as integral with limits
            if((eq1[i+1] in r5) or (eq1[i+1] in r3)): #differentiable function or binary operator lies to the right of the variable
                while(eq1[i+2] == eq1[i]): #If they are same, then we generate new variable until they are not equal
                    eq1[i] = r1[random.randint(0,len(r1)-1)]
            elif((eq1[i-1] in r5) or (eq1[i-1] in r3)): # function is to its left
                while(eq1[i-2] == eq1[i]):
                    eq1[i] = r1[random.randint(0,len(r1)-1)]
            #Increment edit cost only if the variable changes
            if(term != eq1[i]):
                editcost= editcost + editoperatorcost["r1"]

#Case Matrices
        if term in r2:
            eq1[i] = r2[random.randint(0,len(r2)-1)]
            #Increment edit cost only if the variable changes
            if(term != eq1[i]):
                editcost= editcost + editoperatorcost["r2"]

#Case Operators # if + or - replace only with + or -; if * or / replace with anything
        if term in r3:
            if term == "+" or term == "-":
                eq1[i]=r3[random.randint(0,1)] #if it is + or - then only + or - is picked which are at the indices 0 and 1
            else:
                eq1[i]=r3[random.randint(0,len(r3)-1)]
            #Increment edit cost only if the variable changes
            if(term != eq1[i]):
                editcost= editcost + editoperatorcost["r3"]
#Case Matrix unary operators
        if term in r4:
            ran4 = random.randint(0,len(r4))
            if(ran4 == len(r4)):
                eq1[i] = ""
            else:
                eq1[i] = r4[ran4]
            #Increment edit cost for any edit or delete
            if(term != eq1[i]):
                editcost= editcost + editoperatorcost["r4"]

#Case differential operators
        if term in r5:
            ran5 = random.randint(0,len(r5)-1)
            eq1[i] = r5[ran5]
            #Increment edit cost for any edit or delete
            if(term != eq1[i]):
                editcost= editcost + editoperatorcost["r5"]

#Case Coefficients
        if term in r6:
            ran6 = random.randint(0,len(r6))
            if(ran6 == len(r6)):
                eq1[i] = ""
            else:
                eq1[i] = r6[ran6]
            #Increment edit cost for any edit or delete
            if(term != eq1[i]):
                editcost= editcost + editoperatorcost["r6"]

        if term == "1*":
            ran6 = random.randint(0,len(r6))
            if(ran6 == len(r6)):
                eq1[i] = "1*"
            else:
                eq1[i] = r6[ran6]
            #Increment edit cost for any edit or delete
            if(term != eq1[i]):
                editcost= editcost + editoperatorcost["r6"]

#Case functions
        if term in r7:
            ran7 = random.randint(0,len(r7))
            if(ran7 == len(r7)):
                eq1[i] = ""
            else:
                eq1[i] = r7[ran7]
            #Increment edit cost for any edit or delete
            if(term != eq1[i]):
                editcost= editcost + editoperatorcost["r7"]


        #code to get the edit editsequence
        count=0
        for o in range(0,i+1): # find the occurance of the term
            if eq[o]== eq[i]:
                count= count+1

        if eq1[i] != eq[i]:
            editsequence = editsequence +" ("+ eq[i] + " -> " + str(count) + " -> "+ eq1[i] + ")"

    #generate new term- cost is computed in the newterm function and added
    #addlterm= gennewterm()
    #eq1.append(addlterm[0])
    #editcost= editcost+ addlterm[1]

    #converting list to string
    eqn_mod = ""
    for c2 in eq1:
        eqn_mod = eqn_mod + c2

    if(eqn_orig == eqn_mod):
        print("No change")
    else:
        #store modified equations in a list
        print(eqn_mod)
        # print("cost=" + str(editcost))
        manipulatedequations[eqn_mod]= [editcost, editsequence]

####################### end of for loop #######################

meqdf= pd.DataFrame.from_dict(manipulatedequations,orient='index')
meqdf["equation"] = meqdf.index
meqdf.columns=["cost","editsequence", "equation"]
meqdf = meqdf[["equation", "cost", "editsequence"]]
meqdf = meqdf.reset_index(drop= True)
#meqdf.columns  = [["equation", "cost", "editsequence"]]
meqdf=meqdf.sort_values(by=['cost'])
meqdf = meqdf.reset_index(drop= True)
meqdf.to_csv("diffeq1_real.csv",index= True)
print(meqdf)

# Algorithm 1 starts: Check for budget
costincurred =0
for j in range(0,k):
    costincurred= costincurred + meqdf.iloc[j,1]
    if costincurred > budget:
        print("budget insufficient")
print("costincurred= " + str(costincurred))


