# Date: 2022-01-21
# Author: Gustav Collin Rasmussen
# Purpose: Definition and exploration of popular 1-repetition-maximum formulas

library(tidyverse)
library(cowplot)


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


###### evaluate 1rm formulas at 5 reps for varying weights ######
weight = seq(10, 60, by=10)

one_rm_constant_reps_df <- data.frame(weight = weight,
                        epley_1rm = epley(weight, 5),
                        brzycki_1rm = brzycki(weight, 5)
                        )

df1 <- one_rm_constant_reps_df %>%
  select(weight, epley_1rm, brzycki_1rm) %>%
  gather(key = "variable", value = "one_rep_max", -weight)

###### evaluate 1rm formulas at weight: 70 kg for varying reps ######
reps = 2:10
one_rm_constant_weight_df <- data.frame(reps = reps,
                                      epley_1rm = epley(70, reps),
                                      brzycki_1rm = brzycki(70, reps)
)

df2 <- one_rm_constant_weight_df %>%
  select(reps, epley_1rm, brzycki_1rm) %>%
  gather(key = "variable", value = "one_rep_max", -reps)

###### evaluate inverse 1rm formulas at 5 reps for varying weights ######
inverse_one_rm_constant_reps_df <- data.frame(weight = weight,
                        epley_inverted = epley_inverted(weight, 5, 10),
                        brzycki_inverted = brzycki_inverted(weight, 5, 10)
                        )

df3 <- inverse_one_rm_constant_reps_df %>%
  select(weight, epley_inverted, brzycki_inverted) %>%
  gather(key = "variable", value = "inverse_one_rep_max", -weight)

###### evaluate inverse 1rm formulas at weight: 70 kg for varying reps ######
inverse_one_rm_constant_weight_df <- data.frame(reps = reps,
                                      epley_inverted = epley_inverted(70, reps, 10),
                                      brzycki_inverted = brzycki_inverted(70, reps, 10)
)

df4 <- inverse_one_rm_constant_weight_df %>%
  select(reps, epley_inverted, brzycki_inverted) %>%
  gather(key = "variable", value = "inverse_one_rep_max", -reps)

################## prepare plots ##################
sp1 <- ggplot(df1, aes(x = weight, y = one_rep_max)) + 
  geom_point(aes(color = variable)) +
  scale_color_manual(values = c("darkred", "steelblue"))

sp2 <- ggplot(df2, aes(x = reps, y = one_rep_max)) + 
  geom_point(aes(color = variable)) +
  scale_color_manual(values = c("darkred", "steelblue"))

sp3 <- ggplot(df3, aes(x = weight, y = inverse_one_rep_max)) + 
  geom_point(aes(color = variable)) +
  scale_color_manual(values = c("darkred", "steelblue"))

sp4 <- ggplot(df4, aes(x = reps, y = inverse_one_rep_max)) + 
  geom_point(aes(color = variable)) +
  scale_color_manual(values = c("darkred", "steelblue"))

################## show figure ##################
plot_grid(sp1, sp2, sp3, sp4,
          labels = rep(c("constant reps (5)", "constant weight (70 kg)"), times=2),
          ncol = 2, nrow = 2)

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
