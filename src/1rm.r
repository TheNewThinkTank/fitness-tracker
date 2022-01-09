# 1 repetition maximum formulas


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


df <- data.frame(weight = seq(10, 60, by=10),
                 reps = c(2, 2, 3, 3, 4, 4),
                 epley_1rm = c(epley(10, 2), epley(20, 2), epley(30, 3), epley(40, 3), epley(50, 4), epley(60, 4)),
                 brzycki_1rm = c(brzycki(10, 2), brzycki(20, 2), brzycki(30, 3), brzycki(40, 3), brzycki(50, 4), brzycki(60, 4)),
                 progressions = seq(10, 60, by=10),
                 epley_inverted = c(epley_inverted(60, 5, 10), epley_inverted(60, 5, 20), epley_inverted(60, 5, 30), epley_inverted(60, 5, 40), epley_inverted(60, 5, 50), epley_inverted(60, 5, 60)),
                 brzycki_inverted = c(brzycki_inverted(60, 5, 10), brzycki_inverted(60, 5, 20), brzycki_inverted(60, 5, 30), brzycki_inverted(60, 5, 40), brzycki_inverted(60, 5, 50), brzycki_inverted(60, 5, 60))
                )

print(df)

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
