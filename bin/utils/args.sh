#!/usr/bin/env bash

parse_arguments() {
  while getopts ":d:f:c:h" opt; do
    case ${opt} in
      d )
        WORKOUT_DATE=$OPTARG
        # shellcheck disable=SC2034
        WORKOUT_DATES=("$WORKOUT_DATE")
        ;;
      f )
        # shellcheck disable=SC2034
        FILE_FORMAT=$OPTARG
        ;;
      c )
        # shellcheck disable=SC2034
        CONFIG_FILE=$OPTARG
        ;;
      h )
        echo "Usage: $0 [-d WORKOUT_DATE] [-f FILE_FORMAT] [-c CONFIG_FILE]"
        exit 0
        ;;
      \? )
        echo "Invalid option: $OPTARG" 1>&2
        exit 1
        ;;
      : )
        echo "Invalid option: $OPTARG requires an argument" 1>&2
        exit 1
        ;;
    esac
  done
  shift $((OPTIND -1))
}
