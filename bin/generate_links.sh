#!/usr/bin/env bash

# This script generates embeddable links for PNG files in a directory
# and saves them to a file.

# Prerequisites:
# 1. Install gdrive CLI:
# brew install gdrive

# Usage:
# 1. Set the IMG_DIR variable to the directory containing PNG files.
# 2. Run the script.

# Note:
# 1. The script will create a file named image_links.txt in the current directory.
# 2. The embeddable links are generated using Google Drive.
# 3. The PNG files are uploaded to Google Drive and shared publicly.
# 4. The embeddable links are generated using the file IDs.

# Manual example:
# https://drive.google.com/file/d/1TLjAUuiVDSg3Y6UHymzOW-j1p44CCujO/view?usp=sharing
# Embeddable link:
# https://drive.google.com/uc?export=view&id=1TLjAUuiVDSg3Y6UHymzOW-j1p44CCujO


# Directory containing PNG files
IMG_DIR="path/to/your/img"

# Function to get Google Drive file ID
get_file_id() {
  local file_path="$1"
  gdrive upload --share "$file_path" | grep 'https://drive.google.com/file/d/' | sed 's/.*file\/d\/\([^\/]*\).*/\1/'
}

# Function to generate embeddable link
generate_embeddable_link() {
  local file_id="$1"
  echo "https://drive.google.com/uc?export=view&id=${file_id}"
}

# Main script
main() {
  if [[ ! -d "$IMG_DIR" ]]; then
    echo "Directory $IMG_DIR does not exist."
    exit 1
  fi

  > image_links.txt  # Clear the file if it exists

  for img_file in "$IMG_DIR"/*.png; do
    if [[ -f "$img_file" ]]; then
      file_id=$(get_file_id "$img_file")
      embeddable_link=$(generate_embeddable_link "$file_id")
      echo "$embeddable_link" >> image_links.txt
    fi
  done

  echo "Embeddable links have been saved to image_links.txt"
}

main
