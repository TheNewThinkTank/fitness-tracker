# Date: 2022-01-21
# Author: Gustav Collin Rasmussen
# Purpose: Definition and exploration of popular 1-repetition-maximum formulas

# library(tidyverse)
library(ggplot2)


epley <- function(w, r) {
    stopifnot(r > 1)
    return (w * (1 + r / 30))
}


brzycki <- function(w, r) {
    return (w * 36 / (37 - r))
}


epley_inverted <- function(one_rm, r, progression) {
    stopifnot(r > 1)
    return (log10(progression) * one_rm / (1 + r / 30))
}


brzycki_inverted <- function(one_rm, r, progression) {
    return (log10(progression) * one_rm * (37 - r) / 36)
}


weight = seq(10, 60, by=10)

# evaluate 1rm formulas at 5 reps for varying weights
one_rm_df <- data.frame(weight = weight,
                        epley_1rm = epley(weight, 5),
                        brzycki_1rm = brzycki(weight, 5)
                        )

# progressions = seq(10, 60, by=10),
# epley_inverted = c(epley_inverted(60, 5, 10), epley_inverted(60, 5, 20), epley_inverted(60, 5, 30), epley_inverted(60, 5, 40), epley_inverted(60, 5, 50), epley_inverted(60, 5, 60)),
# brzycki_inverted = c(brzycki_inverted(60, 5, 10), brzycki_inverted(60, 5, 20), brzycki_inverted(60, 5, 30), brzycki_inverted(60, 5, 40), brzycki_inverted(60, 5, 50), brzycki_inverted(60, 5, 60))
print(one_rm_df)

ggplot(data = one_rm_df, aes(x = weight, y = epley_1rm)) +
    geom_point()

# weights = c(10, 20, 30, 40, 50)
# weights = seq(10, 50, by=10)
# print(weights)
# reps = c(1, 2, 3, 4, 5)
# reps = 2:6
# print(reps)

# progressions = seq(10, 100, by=10)
# for (progression in progressions){
#     print(epley_inverted(58.33333, 5, progression))
# }

# for (rep in reps){
    # print(epley_inverted(58.33333, rep))
    # print(brzycki_inverted(56.25, rep))
# }

# epley_1rm = epley(50, 5)
# brzycki_1rm = brzycki(50, 5)
# print(epley_1rm)
# print(brzycki_1rm)

# epley_weight = epley_inverted(58.33333, 5)
# brzycki_weight = brzycki_inverted(56.25, 5)
# print(epley_weight)
# print(brzycki_weight)
