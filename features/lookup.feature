Feature: Lookup helper
    For each month of the year a correct integer representation must exist

    Scenario: Date-string leads to existing training log
        Given A valid workout-date as string
        When Extracting the year and month
        Then The corresponding training log exists

# Scenario: Integer representation leads to correct conversion from string names
#     Given A month as string
#     When Looking up the enum
#     Then The resulting integer without zero-padding must be returned

# Scenario: Month integer representation leads to existing training log
#     Given A month as integer
#     When Looking up the corresponding training log
#     Then The training log exists
