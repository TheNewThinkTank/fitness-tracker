Feature: Workout data
    For each musclegroup and exercise,
    sufficient training data must be available

    Scenario: Sufficient data is available
        Given A valid combination of musclegroup and exercise
        When Looking up in the db
        Then The resulting dataframe has more than 2 entries
