
parse_arguments() {
  while getopts ":d:f:c:h" opt; do
    case ${opt} in
      d )
        WORKOUT_DATE=$OPTARG
        WORKOUT_DATES=("$WORKOUT_DATE")  # Initialize WORKOUT_DATES with the provided date
        ;;
      f )
        FILE_FORMAT=$OPTARG
        ;;
      c )
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
