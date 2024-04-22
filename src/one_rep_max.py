

def epley(weight, reps):
    # Assert r is positive
    return weight * (1 + reps / 30)


def brzycki(weight, reps):
    # Assert r is within range 1 to 20
    return weight * 36 / (37 - reps)


def acsm(weight, reps):
    # Assert denominator is not zero
    # if ((100 - reps * 2.5) / 100) == 0:
    #     sys.exit("The denominator is Zero")
    return weight / ((100 - reps * 2.5) / 100)
