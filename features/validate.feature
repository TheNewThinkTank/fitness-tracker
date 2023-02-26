Feature: Data validation
    For each recorded workout in the database,
    the data must conform to the pydantic Workout class validation structure

    Scenario: Data is correctly formatted
        Given A JSON file with test data
        When Reading the file content
        Then It should conform to the pydantic Workout class validation
