"""
Date: 2021-12-21
Author: Gustav Collin Rasmussen
Purpose: Train a linear-regression model on simulated weight-training data,
using the Scikit Learn library
"""

# TODO: Add sim data to sim_db.json with TinyDB
# TODO: load sim data into X and y
# TODO: print coefficients
# TODO: plot data and fit together in same figure

from sklearn import linear_model

reg = linear_model.LinearRegression()

X, y = [[0, 0], [1, 1], [2, 2]], [0, 1, 2]
reg.fit(X, y)

print(reg.coef_)
