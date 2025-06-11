
get_month_name() {
  local month_num=$1
  if (( month_num >= 1 && month_num <= 12 )); then
    if [[ "$(uname)" == "Darwin" ]]; then
      month=$(date -j -f "%m" "$month_num" "+%B")
    else
      month=$(date -d "$month_num/1" '+%B')
    fi
    echo "$month"
  else
    echo "Invalid month number: $month_num" >&2
    exit 1
  fi
}
