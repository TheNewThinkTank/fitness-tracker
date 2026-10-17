#!/usr/bin/env bats

# shellcheck disable=SC1091,SC2329

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

    source "$BATS_TEST_DIRNAME/fitcli.sh"
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

@test "validate_date rejects invalid date" {
    run validate_date "2024-02-30"
    [ "$status" -ne 0 ]
    [[ "$output" == *"Date is invalid."* ]]
}

@test "validate_file_format accepts supported format" {
    run validate_file_format "yml"
    [ "$status" -eq 0 ]
}

@test "validate_file_format rejects unsupported format" {
    run validate_file_format "xml"
    [ "$status" -ne 0 ]
}

@test "find_workout_files handles a missing archive directory" {
    run find_workout_files "$TMP_DIR/missing" "2026-09-14" "yml"
    [ "$status" -eq 0 ]
    [ -z "$output" ]
}

@test "log appends timestamped messages without rotating a small file" {
    log "Previous entry"
    run log "Current entry"
    [ "$status" -eq 0 ]
    [[ "$output" == *" - Current entry" ]]
    [ "$(wc -l < "$LOG_FILE")" -eq 2 ]
    [ ! -e "$TMP_DIR/archive" ]
    [[ "$output" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2} ]]
}

@test "log rotates ten MiB files into a dated gzip archive" {
    log "Previous entry"
    printf '%10485760s' '' >> "$LOG_FILE"
    printf '\n' >> "$LOG_FILE"
    original_size=$(wc -c < "$LOG_FILE")
    run log "First entry after rotation"
    [ "$status" -eq 0 ]
    [ "$(wc -l < "$LOG_FILE")" -eq 1 ]
    archive="$TMP_DIR/archive/$(date +%Y-%m)/test_fitcli.0001.log.gz"
    gzip -t "$archive"
    [ "$(gzip -dc "$archive" | wc -c)" -eq "$original_size" ]
}

@test "log rotates a small old file on the next invocation" {
    printf '%s\n' "2024-07-17 17:02:10 - Previous entry" > "$LOG_FILE"
    run log "Current entry"
    [ "$status" -eq 0 ]
    [ "$(wc -l < "$LOG_FILE")" -eq 1 ]
    [ "$(gzip -dc "$TMP_DIR/archive/2024-07/test_fitcli.0001.log.gz")" = "2024-07-17 17:02:10 - Previous entry" ]
}

@test "log stops without appending when rotation fails" {
    printf '%10485760s' '' > "$LOG_FILE"
    printf '%s\n' "Blocked archive directory" > "$TMP_DIR/archive"
    run log "Must not be appended"
    [ "$status" -eq 1 ]
    [ "$(wc -c < "$LOG_FILE")" -eq 10485760 ]
}

configure_workflow_fixture() {
    export FITNESS_TRACKER_LOG_DIR="$TMP_DIR/logs with spaces"
    FAILURE_STAGE="$1"
    REAL_PYTHON_BIN="$PYTHON_BIN"
    fixture_python() {
        if [[ "$1" == "-m" && "$2" == "src.utils.log_archive" ]]; then
            "$REAL_PYTHON_BIN" "$@"
        elif [[ "$1" == *"validate.py" ]]; then
            [[ "$FAILURE_STAGE" != "validation" ]]
        elif [[ "$1" == *"insert.py" ]]; then
            [[ "$FAILURE_STAGE" != "insertion" ]]
        else
            return 1
        fi
    }
    PYTHON_BIN=fixture_python
    load_env_variables() { export FITNESS_TRACKER_DATA_DIR="$TMP_DIR"; }
    validate_env_variables() { return 0; }
    load_config_variables() { return 0; }
    load_config() { return 0; }
    check_dependencies() { return 0; }
    find_workout_files() { printf '%s\0' "$TMP_DIR/fixture.yml"; }
    prepare_figures() { echo "Fixture figures prepared"; }
    open_figures() { return 0; }
}

@test "workflow reports validation failure without claiming success" {
    configure_workflow_fixture validation
    run main -d "2026-10-17"
    [ "$status" -eq 1 ]
    [[ "$output" == *"Validation failed"* ]]
    [[ "$output" == *"Workflow completed with errors"* ]]
    [[ "$output" != *"Workflow completed successfully"* ]]
    [[ "$output" != *"Fixture figures prepared"* ]]
}

@test "workflow reports insertion failure without claiming success" {
    configure_workflow_fixture insertion
    run main -d "2026-10-17"
    [ "$status" -eq 1 ]
    [[ "$output" == *"Failed to insert data"* ]]
    [[ "$output" == *"Workflow completed with errors"* ]]
    [[ "$output" != *"Workflow completed successfully"* ]]
    [[ "$output" != *"Fixture figures prepared"* ]]
}

@test "workflow honors a log directory with spaces from another working directory" {
    configure_workflow_fixture none
    cd "$TMP_DIR"
    run main -d "2026-10-17"
    [ "$status" -eq 0 ]
    [[ "$output" == *"Workflow completed successfully"* ]]
    [ -f "$FITNESS_TRACKER_LOG_DIR/fitcli.log" ]
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

@test "open_figures tries to open correct image files" {
    run open_figures "2024" "December"
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
