# Simulations

Gallery of visualization types based on simulated workout data is shown below.
Source code can be found [here](https://github.com/TheNewThinkTank/fitness-tracker/blob/main/src/combined_metrics/plot_frequency.py)

## Frequency plots

| <img src="https://lh3.googleusercontent.com/d/10Vgt1_9Xxz7ZuSAcw0WpMCQdSGwNy-Dj"> | <img src="https://lh3.googleusercontent.com/d/10f6Gcmk1GOsa0KKjeSEYO3tLpKXLv2uk"> |
| :----------: | :------: |
| <img src="https://lh3.googleusercontent.com/d/10WKxWKbUfcc5F_FQbHSU4v1qsR90dNWm"> | <img src="https://lh3.googleusercontent.com/d/10uxjAmzZiWqYQk7elRf5KFVjd6grCw6C"> |
| <img src="https://lh3.googleusercontent.com/d/10qkAYNAakLhHswMSA9gFjfOoiDcyae_U"> | <img src="https://lh3.googleusercontent.com/d/110nNpFue725Cly-ncgdnzPgZiZTskNFJ"> |
| <img src="https://lh3.googleusercontent.com/d/10wBQjymFBu70_NroHXcx8uJphKcztLjy"> | <img src="https://lh3.googleusercontent.com/d/110A1CifISsNpI0N0PmU9OhhxlBUHT_Zn"> |

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
