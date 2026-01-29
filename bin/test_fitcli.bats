#!/usr/bin/env bats

# Test file for fitcli script

# Install Bats:
# brew install bats-core  # macOS
# sudo apt-get install bats  # Ubuntu

# Run the Tests:
# bats test_fitcli.bats

setup() {
    # Create a custom temporary directory
    TMP_DIR="/tmp/test_fitcli_$$"
    mkdir -p "$TMP_DIR"
    export LOG_FILE="$TMP_DIR/test_fitcli.log"
    export IMG_PATH="$TMP_DIR/"

    source ./fitcli.sh
    insert_data() { echo "Mocked insert_data called with: $*"; }
    prepare_figures() { echo "Mocked prepare_figures called with: $*"; }

    # Mock external commands
    python3() {
        if [[ "$1" == *"insert.py" ]]; then
            echo "Mock insert.py called with ${*:2}"
            return 0
        elif [[ "$1" == *"combined_metrics.py" ]]; then
            echo "Mock combined_metrics.py called with ${*:2}"
            return 0
        fi
        return 1
    }

    open() {
        echo "Mock open called with $1"
        return 0
    }

    export -f python3 open
}

teardown() {
    rm -rf "$TMP_DIR"
}

# Tests

@test "validate_date accepts valid date" {
    run validate_date "2024-12-06"
    [ "$status" -eq 0 ]
    [[ "$output" == *"Date is valid."* ]]
}

# TODO: complete test below
# @test "validate_date rejects invalid date" {
#     run validate_date "2024-02-30"
#     [ "$status" -ne 0 ]
#     [[ "$output" == *"Date is invalid."* ]]
# }

# TODO: complete test below
# @test "validate_file_format accepts supported format" {
#     run validate_file_format "yml"
#     [ "$status" -eq 0 ]
# }

@test "validate_file_format rejects unsupported format" {
    run validate_file_format "xml"
    [ "$status" -ne 0 ]
}

# TODO: complete test below
# @test "insert_data calls Python script with correct arguments" {
#     run insert_data "yml" "2024-12-06"
#     [ "$status" -eq 0 ]
#     [[ "$output" == *"Mock insert.py called with --file_format yml --datatype real --dates 2024-12-06"* ]]
# }

# TODO: complete test below
# @test "prepare_figures calls Python script with correct arguments" {
#     run prepare_figures "2024" "December"
#     [ "$status" -eq 0 ]
#     [[ "$output" == *"Mock combined_metrics.py called with --year_to_plot 2024 --month_to_plot December"* ]]
# }

@test "open_images tries to open correct image files" {
    run open_images "2024" "December"
    [ "$status" -eq 0 ]
    [[ "$output" == *"Mock open called with $TMP_DIR/2024_workout_frequency.png"* ]]
    [[ "$output" == *"Mock open called with $TMP_DIR/workout_duration_December_2024.png"* ]]
}

# TODO: complete e2e test below
# @test "full workflow runs without side effects" {
#     run WORKOUT_DATE="2024-12-06" \
#         FILE_FORMAT="yml" \
#         YEAR_TO_PLOT="2024" \
#         MONTH_TO_PLOT="December" \
#         insert_data "$FILE_FORMAT" "$WORKOUT_DATE" \
#         prepare_figures "$YEAR_TO_PLOT" "$MONTH_TO_PLOT" \
#         open_images "$YEAR_TO_PLOT" "$MONTH_TO_PLOT"

#     [ "$status" -eq 0 ]
#     [[ "$output" == *"Mock insert.py called"* ]]
#     [[ "$output" == *"Mock combined_metrics.py called"* ]]
#     [[ "$output" == *"Mock open called"* ]]
# }
