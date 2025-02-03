## Frequency

Below: Annual weekly workout frequency.<br>
Each figure displays week vs number of workouts during that week.

| <img src="https://lh3.googleusercontent.com/d/1TLjAUuiVDSg3Y6UHymzOW-j1p44CCujO"> | <img src="https://lh3.googleusercontent.com/d/1p28Q5yvAytWRclEq3rUmbhl5PHOAWinp"> |
| :----------: | :------: |
| <img src="https://lh3.googleusercontent.com/d/1XKjCcHD9DlI-fmAWdqjn6GJutRM-nbr0"> | <img src="https://lh3.googleusercontent.com/d/1SGSjctH8RhJXrjuI6TTdrj7BRVyGwTO1"> |
| <img src="https://lh3.googleusercontent.com/d/1CshUp9CxLIW3ddMAU7FZDAO2odNpZfnm"> | |

<script>
  // Add a timestamp to all image URLs that use Google Drive links
  document.querySelectorAll('img').forEach((img) => {
    const src = img.src;

    // Check if the src is a Google Drive image URL
    if (src.includes('lh3.googleusercontent.com')) {
      const timestampedSrc = `${src}?t=${Date.now()}`;
      img.src = timestampedSrc; // Update the src attribute with a timestamp
    }
  });
</script>
