# -*- coding: utf-8 -*-
"""
Created on Tue Nov 14 15:16:59 2023

@author: pauls
"""

import gurobipy as gp
from gurobipy import GRB
import numpy as np
import pandas as pd


m = gp.Model("Profits Maximization")
m.ModelSense = GRB.MAXIMIZE
  
### Variables

NumVars = 4
VarNames = ['A1','A2','B1','B2']
Profit = np.array([82, 87.5, 82, 87.5]) 


x = m.addMVar(NumVars, obj=Profit, name=VarNames)

# define A & B
A = m.addVar(name="A")
B = m.addVar(name="B")
# A1 + A2 = 0.44 * A_total
m.addConstr(x[0] + x[1] == 0.44 * A , "A_proportion")
m.addConstr(x[2] + x[3] == 0.72 * B , "B_proportion")

# Add binary variable y1
y1 = m.addVar(vtype=GRB.BINARY, name="y1")

m.addConstr(A + B >= 1000 * y1, "lower_bound_y1")
m.addConstr(A + B <= 1400 * y1, "upper_bound_y1")

new_term1 = (A + B -1000) * y1 * 4


# Add binary variable y2
y2 = m.addVar(vtype=GRB.BINARY, name="y2")

m.addConstr(x[0] + x[1] + x[2] + x[3] >= 800 * y2, "lower_bound_y2")
m.addConstr(x[0] + x[1] + x[2] + x[3] <= 1100 * y2, "upper_bound_y2")
new_term2 = (x[0] + x[1] + x[2] + x[3] - 800) * y2 * 6.5


m.update()

# Objective function
m.setObjective(x @ Profit - new_term1 - new_term2 - 11 * A - 17.5 * B, GRB.MAXIMIZE)

### Constraints

### Constraints

limits = np.array([0.4,-0.07])
num_constrs = limits.size

which_loans = np.zeros([num_constrs, 4])
which_loans[0,0]=0.5
which_loans[0,1]=0.4
which_loans[0,2]=0.6
which_loans[0,3]=0.3

which_loans[1,0]=-0.05
which_loans[1,1]=-0.06
which_loans[1,2]=-0.1
which_loans[1,3]=-0.06



A = np.zeros([num_constrs, NumVars])
for i in range(num_constrs):
    for j in range(NumVars):
        A[i,j]=which_loans[i,j]-limits[i]

rhs = np.zeros([num_constrs])

m.addMConstr(A , x, '>', rhs, name="Limits")

m.optimize()
m.update()

if m.status == GRB.OPTIMAL:
    profit = m.objVal
    print('Obj: {:.2f}'.format(profit))  
else:
    profit = None  
