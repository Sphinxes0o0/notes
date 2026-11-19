#!/bin/bash
# Crawl CSAPP3e Solutions site

BASE_URL="https://dreamanddead.github.io/CSAPP-3e-Solutions"
DEST_DIR="/Users/sphinx.shi/workspace/wiki/pyramid/raw/bookmarks/ebooks/csapp3e"
IMAGES_DIR="$DEST_DIR/images"

mkdir -p "$DEST_DIR" "$IMAGES_DIR"

# Crawl homepage first
echo "Crawling homepage..."
curl -sL "$BASE_URL/" -o "$DEST_DIR/homepage.html"

# Function to extract content from HTML and download images
extract_and_save() {
  local url="$1"
  local output_file="$2"
  local chapter_slug="$3"
  local problem_num="$4"

  echo "  Fetching: $url"

  # Fetch the page
  local html=$(curl -sL "$url")

  # Extract title
  local title=$(echo "$html" | grep -o '<title>[^<]*</title>' | sed 's/<[^>]*>//g')

  # Extract main content (between #body-inner and disqus_thread)
  local content=$(echo "$html" | sed -n '/<div id="body-inner">/,/<div id="disqus_thread">/p' | sed '$d')

  # Remove navigation elements
  content=$(echo "$content" | sed -n '/<div id="chapter">/,/<\/div>/p')

  # Remove scripts and styles
  content=$(echo "$content" | sed 's/<script[^>]*>.*<\/script>//g')
  content=$(echo "$content" | sed 's/<style[^>]*>.*<\/style>//g')
  content=$(echo "$content" | sed 's/<link[^>]*>//g')

  # Remove header/nav elements
  content=$(echo "$content" | sed 's/<nav[^>]*>.*<\/nav>//g')
  content=$(echo "$content" | sed 's/<div id="sidebar-toggle[^>]*>.*<\/div>//g')

  # Download and replace local images (max 8 per page)
  local img_counter=0
  local img_urls=$(echo "$content" | grep -o 'src="[^"]*\.\.\/images[^"]*"' | sed 's/src="//;s/"$//')
  for img_rel_url in $img_urls; do
    if [ $img_counter -ge 8 ]; then
      echo "    Max images reached, skipping..."
      break
    fi
    img_url="${img_rel_url/..\/images/$BASE_URL/images}"
    if [ -n "$img_url" ]; then
      img_counter=$((img_counter + 1))
      local ext="${img_url##*.}"
      local img_name="${chapter_slug}-${problem_num}-${img_counter}.${ext}"
      echo "    Downloading image: $img_name"
      curl -sL "$img_url" -o "$IMAGES_DIR/$img_name" 2>/dev/null
      content=$(echo "$content" | sed "s|$img_url|$img_name|g")
      content=$(echo "$content" | sed "s|$img_rel_url|$img_name|g")
    fi
  done

  # Convert relative image paths
  content=$(echo "$content" | sed "s|src=\".\/images|src=\"images|g")

  # Convert HTML to basic markdown
  content=$(echo "$content" | sed 's/<pre><code class="c">/\n```c\n/g')
  content=$(echo "$content" | sed 's/<pre><code>/\n```\n/g')
  content=$(echo "$content" | sed 's/<\/code><\/pre>/\n```\n/g')

  # Code
  content=$(echo "$content" | sed 's/<code>/`/g;s/<\/code>/`/g')

  # Bold
  content=$(echo "$content" | sed 's/<strong>/**/g;s/<\/strong>/**/g')

  # Emphasis
  content=$(echo "$content" | sed 's/<em>/*/g;s/<\/em>/*/g')

  # Headers
  content=$(echo "$content" | sed 's/<h1 id=[^>]*>/# /g;s/<\/h1>//g')
  content=$(echo "$content" | sed 's/<h2 id=[^>]*>/## /g;s/<\/h2>//g')
  content=$(echo "$content" | sed 's/<h3 id=[^>]*>/### /g;s/<\/h3>//g')

  # Paragraphs and breaks
  content=$(echo "$content" | sed 's/<br\s*\/?>/\n/g')
  content=$(echo "$content" | sed 's/<p>/\n/g;s/<\/p>/\n/g')

  # Lists
  content=$(echo "$content" | sed 's/<ul>/\n/g;s/<\/ul>/\n/g')
  content=$(echo "$content" | sed 's/<ol>/\n/g;s/<\/ol>/\n/g')
  content=$(echo "$content" | sed 's/<li>/- /g;s/<\/li>/\n/g')

  # Tables
  content=$(echo "$content" | sed 's/<table>/\n<table>/g;s/<\/table>/<\/table>\n/g')
  content=$(echo "$content" | sed 's/<thead>/:::\n/g;s/<\/thead>/\n:::/g')
  content=$(echo "$content" | sed 's/<tbody>/:::\n/g;s/<\/tbody>/\n:::/g')

  # Remove remaining HTML tags
  content=$(echo "$content" | sed 's/<[^>]*>//g')

  # Clean up
  content=$(echo "$content" | sed 's/^[[:space:]]*//g;s/[[:space:]]*$//g')
  while echo "$content" | grep -q '^[[:space:]]*$'; do
    content=$(echo "$content" | sed '/^[[:space:]]*$/d')
  done

  # Write output
  echo "$content" > "$output_file"
}

# Chapter definitions
declare -a CHAPTERS=(
  "1|A Tour of Computer Systems|"
  "2|Representing and Manipulating Information|2.55 2.56 2.57 2.58 2.59 2.60 2.61 2.62 2.63 2.64 2.65 2.66 2.67 2.68 2.69 2.70 2.71 2.72 2.73 2.74 2.75 2.76 2.77 2.78 2.79 2.80 2.81 2.82 2.83 2.84 2.85 2.86 2.87 2.88 2.89 2.90 2.91 2.92 2.93 2.94 2.95 2.96 2.97"
  "3|Machine-Level Representation of Programs|3.58 3.59 3.60 3.61 3.62 3.63 3.64 3.65 3.66 3.67 3.68 3.69 3.70 3.71 3.72 3.73 3.74 3.75"
  "4|Processor Architecture|4.45 4.46 4.47 4.48 4.49 4.50 4.51 4.52 4.53 4.54 4.55 4.56 4.57 4.58 4.59"
  "5|Optimizing Program Performance|5.13 5.14 5.15 5.16 5.17 5.18 5.19"
  "6|The Memory Hierarchy|6.22 6.23 6.24 6.25 6.26 6.27 6.28 6.29 6.30 6.31 6.32 6.33 6.34 6.35 6.36 6.37 6.38 6.39 6.40 6.41 6.42 6.43 6.44 6.45 6.46"
  "7|Linking|7.6 7.7 7.8 7.9 7.10 7.11 7.12 7.13"
  "8|Exceptional Control Flow|8.9 8.10 8.11 8.12 8.13 8.14 8.15 8.16 8.17 8.18 8.19 8.20 8.21 8.22 8.23 8.24 8.25 8.26"
  "9|Virtual Memory|9.11 9.12 9.13 9.14 9.15 9.16 9.17 9.18 9.19 9.20"
  "10|System-Level I/O|10.6 10.7 10.8 10.9 10.10"
  "11|Network Programming|11.6 11.7 11.8 11.9 11.10 11.11 11.12 11.13"
  "12|Concurrent Programming|12.16 12.17 12.18 12.19 12.20 12.21 12.22 12.23 12.24 12.25 12.26 12.27 12.28 12.29 12.30 12.31 12.32 12.33 12.34 12.35 12.36 12.37 12.38 12.39"
)

# Crawl each chapter
for chapter_entry in "${CHAPTERS[@]}"; do
  IFS='|' read -r ch_num ch_title problems <<< "$chapter_entry"

  echo "Processing Chapter $ch_num: $ch_title"

  # Create chapter directory
  ch_dir="$DEST_DIR/chapter$ch_num"
  mkdir -p "$ch_dir"

  # Crawl chapter main page
  extract_and_save "$BASE_URL/chapter$ch_num/" "$ch_dir/index.md" "chapter$ch_num" ""

  # Crawl each problem page
  if [ -n "$problems" ]; then
    for problem in $problems; do
      problem_slug=$(echo "$problem" | tr '.' '-')
      extract_and_save "$BASE_URL/chapter$ch_num/$problem/" "$ch_dir/$problem_slug.md" "chapter$ch_num" "$problem"
    done
  fi

  echo "  Done with chapter $ch_num"
done

echo "Crawling complete!"