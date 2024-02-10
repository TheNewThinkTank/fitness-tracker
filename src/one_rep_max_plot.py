"""
Date: 2024-02-10
Author: Gustav Collin Rasmussen
Purpose: Plots of popular 1-repetition-maximum formulas
"""

import os
import sys

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

from src.one_rep_max_calc import epley, brzycki, epley_inverted, brzycki_inverted

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

fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(10, 8))

# Plot 1
sns.scatterplot(data=df1, x='weight', y='one_rep_max', hue='variable', palette=['darkred', 'steelblue'], ax=axes[0, 0])
axes[0, 0].set_title('Constant reps (5)')
axes[0, 0].set_xlabel('Weight')
axes[0, 0].set_ylabel('One Rep Max')
axes[0, 0].legend(title='Variable')

# Plot 2
sns.scatterplot(data=df2, x='reps', y='one_rep_max', hue='variable', palette=['darkred', 'steelblue'], ax=axes[0, 1])
axes[0, 1].set_title('Constant weight (70 kg)')
axes[0, 1].set_xlabel('Reps')
axes[0, 1].set_ylabel('One Rep Max')
axes[0, 1].legend(title='Variable')

# Plot 3
sns.scatterplot(data=df3, x='weight', y='inverse_one_rep_max', hue='variable', palette=['darkred', 'steelblue'], ax=axes[1, 0])
axes[1, 0].set_title('Constant reps (5)')
axes[1, 0].set_xlabel('Weight')
axes[1, 0].set_ylabel('Inverse One Rep Max')
axes[1, 0].legend(title='Variable')

# Plot 4
sns.scatterplot(data=df4, x='reps', y='inverse_one_rep_max', hue='variable', palette=['darkred', 'steelblue'], ax=axes[1, 1])
axes[1, 1].set_title('Constant weight (70 kg)')
axes[1, 1].set_xlabel('Reps')
axes[1, 1].set_ylabel('Inverse One Rep Max')
axes[1, 1].legend(title='Variable')

plt.tight_layout()
plt.show()
