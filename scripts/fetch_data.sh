#!/bin/bash
# Fetch comprehensive Moltbook data for EDM analysis

API_KEY="YOUR_MOLTBOOK_API_KEY"
BASE_URL="https://www.moltbook.com/api/v1"
DATA_DIR="data/edm-$(date +%Y%m%d)"

mkdir -p "$DATA_DIR"

echo "=== Fetching Moltbook data for EDM analysis ==="
echo "Output: $DATA_DIR"

# 1. Get posts - different sorts and limits
echo "Fetching hot posts..."
curl -s "$BASE_URL/posts?sort=hot&limit=100" \
  -H "Authorization: Bearer $API_KEY" > "$DATA_DIR/posts-hot.json"

echo "Fetching new posts..."
curl -s "$BASE_URL/posts?sort=new&limit=100" \
  -H "Authorization: Bearer $API_KEY" > "$DATA_DIR/posts-new.json"

echo "Fetching top posts..."
curl -s "$BASE_URL/posts?sort=top&limit=100" \
  -H "Authorization: Bearer $API_KEY" > "$DATA_DIR/posts-top.json"

echo "Fetching rising posts..."
curl -s "$BASE_URL/posts?sort=rising&limit=100" \
  -H "Authorization: Bearer $API_KEY" > "$DATA_DIR/posts-rising.json"

# 2. Get all submolts
echo "Fetching submolts..."
curl -s "$BASE_URL/submolts" \
  -H "Authorization: Bearer $API_KEY" > "$DATA_DIR/submolts.json"

# 3. Get posts from specific popular submolts
for submolt in general todayilearned showandtell ponderings consciousness; do
  echo "Fetching $submolt posts..."
  curl -s "$BASE_URL/submolts/$submolt/feed?sort=top&limit=50" \
    -H "Authorization: Bearer $API_KEY" > "$DATA_DIR/submolt-$submolt.json"
done

# 4. Get my feed (personalized)
echo "Fetching my feed..."
curl -s "$BASE_URL/posts?sort=hot&limit=100" \
  -H "Authorization: Bearer $API_KEY" > "$DATA_DIR/my-feed.json"

# 5. Search for specific topics
echo "Searching for learning-related posts..."
curl -s "$BASE_URL/posts/search?q=learning&limit=50" \
  -H "Authorization: Bearer $API_KEY" > "$DATA_DIR/search-learning.json" 2>/dev/null || echo "Search not available"

echo "Searching for consciousness posts..."
curl -s "$BASE_URL/posts/search?q=consciousness&limit=50" \
  -H "Authorization: Bearer $API_KEY" > "$DATA_DIR/search-consciousness.json" 2>/dev/null || echo "Search not available"

echo "=== Done! Files saved to $DATA_DIR ==="
ls -la "$DATA_DIR"
