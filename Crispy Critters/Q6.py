# -*- coding: utf-8 -*-
"""
Created on Tue Nov 14 12:48:48 2023

@author: pauls
"""
### Packages
import gurobipy as gp
from gurobipy import GRB
import numpy as np
import pandas as pd

m = gp.Model("Profits Maximization")
m.ModelSense = GRB.MAXIMIZE
  
### Variables

NumVars = 4
VarNames = ['A1','A2','B1','B2']
Cost = np.array([18, 12.5, 18, 12.5]) 
Profit = 100 - Cost

x = m.addMVar(NumVars, obj=Profit, name=VarNames)

# Add two more binary variables harvest & baking
h = m.addVar(name="h")
b = m.addVar(name="b")

# define A & B
A = m.addVar(name="A")
B = m.addVar(name="B")
# A1 + A2 = 0.44 * A_total
m.addConstr(x[0] + x[1] == 0.44 * A, "A_proportion")
m.addConstr(x[2] + x[3] == 0.72 * B, "B_proportion")

# Add binary variable y1
y1 = m.addVar(vtype=GRB.BINARY, name="y1")

m.addConstr(A + B >= 1000+h * y1, "lower_bound_y1")
m.addConstr(A + B <= 1400+h* y1, "upper_bound_y1")
new_term1 = (A + B -1000-h) * y1 * 4


# Add binary variable y2
y2 = m.addVar(vtype=GRB.BINARY, name="y2")

m.addConstr(x[0] + x[1] + x[2] + x[3] >= 800+b * y2, "lower_bound_y2")
m.addConstr(x[0] + x[1] + x[2] + x[3] <= 1100+b * y2, "upper_bound_y2")
new_term2 = (x[0] + x[1] + x[2] + x[3] - 800-b) * y2 * 6.5


m.update()





# Objective function
m.setObjective(x @ Profit -30*h -20*b - new_term1 - new_term2 -11*A -17.5*B, GRB.MAXIMIZE)

###
### Constraints
###


A = np.array([
    [1,0,2,-1],
    [2, 1, -3, 1] 
     ])
rhs =np.array([0, 0]) 
m.addMConstr(A , x, '>', rhs, name='at least')


m.update()


m.optimize()


for v in m.getVars():
    print(f'{v.varName}, {v.x}')


print('Obj:', m.objVal)