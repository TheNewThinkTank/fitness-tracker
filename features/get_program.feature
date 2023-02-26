Feature: get_program helper
    For a given workout-date the corresponding program-name must be returned

    Scenario: workout-date leads to correct program-name
        Given A valid workout-date string
        When Fetching the program name
        Then The program name must have the right value
