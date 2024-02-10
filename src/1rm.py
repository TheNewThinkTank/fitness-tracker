"""
Date: 2024-02-10
Author: Gustav Collin Rasmussen
Purpose: Definition and exploration of popular 1-repetition-maximum formulas
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


def epley(w, r):
    """_summary_

    :param w: _description_
    :type w: _type_
    :param r: _description_
    :type r: _type_
    :return: _description_
    :rtype: _type_
    """

    # results = []
    # for r in reps_range:
    #     assert r > 1
    #     results.append(w * (1 + r / 30))
    # return results

    assert r > 1
    return w * (1 + r / 30)



def brzycki(w, r):
    return w * 36 / (37 - r)


def epley_inverted(one_rm, r, progression):
    assert r > 1
    return np.log10(progression) * one_rm / (1 + r / 30)


def brzycki_inverted(one_rm, r, progression):
    return np.log10(progression) * one_rm * (37 - r) / 36


###### evaluate 1rm formulas at 5 reps for varying weights ######
weight = range(10, 60, 10)

one_rm_constant_reps_df = pd.DataFrame(
    {
        "weight": weight,
        "epley_1rm": epley(weight, 5),
        "brzycki_1rm": brzycki(weight, 5)
     }
)

df1 = one_rm_constant_reps_df[['weight', 'epley_1rm', 'brzycki_1rm']]
df1 = df1.melt(id_vars='weight', var_name='variable', value_name='one_rep_max')

###### evaluate 1rm formulas at weight: 70 kg for varying reps ######
reps = range(2, 10)

one_rm_constant_weight_df = pd.DataFrame(
    {
        "reps": reps,
        "epley_1rm": epley(70, reps),
        "brzycki_1rm": brzycki(70, reps)
    }
)

df2 = one_rm_constant_weight_df[['reps', 'epley_1rm', 'brzycki_1rm']]
df2 = df2.melt(id_vars='reps', var_name='variable', value_name='one_rep_max')

###### evaluate inverse 1rm formulas at 5 reps for varying weights ######
inverse_one_rm_constant_reps_df = pd.DataFrame(
    {
        "weight": weight,
        "epley_inverted": epley_inverted(weight, 5, 10),
        "brzycki_inverted": brzycki_inverted(weight, 5, 10)
    }
)

df3 = inverse_one_rm_constant_reps_df[['weight', 'epley_inverted', 'brzycki_inverted']]
df3 = df3.melt(id_vars='weight', var_name='variable', value_name='inverse_one_rep_max')

###### evaluate inverse 1rm formulas at weight: 70 kg for varying reps ######
inverse_one_rm_constant_weight_df = pd.DataFrame(
    {
        "reps": reps,
        "epley_inverted": epley_inverted(70, reps, 10),
        "brzycki_inverted": brzycki_inverted(70, reps, 10)
    }
)

df4 = inverse_one_rm_constant_weight_df[['reps', 'epley_inverted', 'brzycki_inverted']]
df4 = df4.melt(id_vars='reps', var_name='variable', value_name='inverse_one_rep_max')

################## plots ##################

plt.figure(figsize=(10, 8))
sns.scatterplot(data=df1, x='weight', y='one_rep_max', hue='variable', palette=['darkred', 'steelblue'])
plt.title('Constant reps (5)')
plt.xlabel('Weight')
plt.ylabel('One Rep Max')
plt.legend(title='Variable')
plt.show()

# Plot 2
plt.figure(figsize=(10, 8))
sns.scatterplot(data=df2, x='reps', y='one_rep_max', hue='variable', palette=['darkred', 'steelblue'])
plt.title('Constant weight (70 kg)')
plt.xlabel('Reps')
plt.ylabel('One Rep Max')
plt.legend(title='Variable')
plt.show()

# Plot 3
plt.figure(figsize=(10, 8))
sns.scatterplot(data=df3, x='weight', y='inverse_one_rep_max', hue='variable', palette=['darkred', 'steelblue'])
plt.title('Constant reps (5)')
plt.xlabel('Weight')
plt.ylabel('Inverse One Rep Max')
plt.legend(title='Variable')
plt.show()

# Plot 4
plt.figure(figsize=(10, 8))
sns.scatterplot(data=df4, x='reps', y='inverse_one_rep_max', hue='variable', palette=['darkred', 'steelblue'])
plt.title('Constant weight (70 kg)')
plt.xlabel('Reps')
plt.ylabel('Inverse One Rep Max')
plt.legend(title='Variable')
plt.show()
