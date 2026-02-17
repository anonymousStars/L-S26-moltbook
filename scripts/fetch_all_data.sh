#!/bin/bash
# Comprehensive Moltbook data fetcher using curl
# Paginates through all posts to maximize dataset size

API_KEY="YOUR_MOLTBOOK_API_KEY"
BASE_URL="https://www.moltbook.com/api/v1"
DATA_DIR="data/edm-full"
COMBINED_FILE="$DATA_DIR/all_posts_combined.json"

mkdir -p "$DATA_DIR"

echo "============================================================"
echo "MOLTBOOK DATA FETCHER - EDM Analysis"
echo "Output: $DATA_DIR"
echo "============================================================"

# Initialize combined file
echo '{"posts":[' > "$COMBINED_FILE.tmp"
first_post=true
total_posts=0
api_calls=0

fetch_endpoint() {
    local endpoint=$1
    local sort=$2
    local max_pages=${3:-20}
    local page=0
    
    echo ""
    echo "[FETCH] $endpoint (sort=$sort, max_pages=$max_pages)"
    
    while [ $page -lt $max_pages ]; do
        local offset=$((page * 100))
        local url="$BASE_URL/$endpoint?sort=$sort&limit=100&offset=$offset"
        local outfile="$DATA_DIR/temp_page.json"
        
        curl -s "$url" -H "Authorization: Bearer $API_KEY" > "$outfile"
        api_calls=$((api_calls + 1))
        
        # Check if we got valid JSON with posts
        local count=$(jq 'if type == "array" then length elif .posts then .posts | length elif .data then .data | length else 0 end' "$outfile" 2>/dev/null || echo "0")
        
        if [ "$count" == "0" ] || [ "$count" == "null" ]; then
            echo "  Page $((page+1)): No more posts"
            break
        fi
        
        # Extract posts and append to combined file
        jq -c 'if type == "array" then .[] elif .posts then .posts[] elif .data then .data[] else empty end' "$outfile" 2>/dev/null | while read -r post; do
            if [ "$first_post" = true ]; then
                first_post=false
            else
                echo "," >> "$COMBINED_FILE.tmp"
            fi
            echo "$post" >> "$COMBINED_FILE.tmp"
        done
        first_post=false
        
        total_posts=$((total_posts + count))
        echo "  Page $((page+1)): $count posts (running total: $total_posts)"
        
        if [ "$count" -lt 100 ]; then
            break
        fi
        
        page=$((page + 1))
        sleep 0.3
    done
}

# Fetch by different sorts
for sort in hot new top rising; do
    fetch_endpoint "posts" "$sort" 30
done

# Get submolts list
echo ""
echo "[SUBMOLTS] Fetching submolt list..."
curl -s "$BASE_URL/submolts" -H "Authorization: Bearer $API_KEY" > "$DATA_DIR/submolts.json"
api_calls=$((api_calls + 1))

# Extract submolt names
submolt_names=$(jq -r '.[] | .name // .slug // empty' "$DATA_DIR/submolts.json" 2>/dev/null | head -30)

# Fetch from each submolt
for name in $submolt_names; do
    if [ -n "$name" ]; then
        fetch_endpoint "submolts/$name/feed" "top" 10
        fetch_endpoint "submolts/$name/feed" "new" 5
    fi
done

# Close JSON array
echo ']}' >> "$COMBINED_FILE.tmp"

# Deduplicate posts by ID
echo ""
echo "[DEDUP] Removing duplicates..."
jq -s '.[0].posts | unique_by(.id)' "$COMBINED_FILE.tmp" > "$DATA_DIR/all_posts_deduped.json" 2>/dev/null

unique_count=$(jq 'length' "$DATA_DIR/all_posts_deduped.json" 2>/dev/null || echo "0")

# Create final output
jq -n --slurpfile posts "$DATA_DIR/all_posts_deduped.json" \
    --arg date "$(date -Iseconds)" \
    --arg calls "$api_calls" \
    '{
        fetched_at: $date,
        api_calls: ($calls | tonumber),
        total_unique_posts: ($posts[0] | length),
        posts: $posts[0]
    }' > "$COMBINED_FILE"

# Cleanup
rm -f "$COMBINED_FILE.tmp" "$DATA_DIR/temp_page.json"

echo ""
echo "============================================================"
echo "FINAL SUMMARY"
echo "============================================================"
echo "Total unique posts: $unique_count"
echo "API calls made: $api_calls"
echo "Output file: $COMBINED_FILE"
echo ""

# Quick stats
echo "Quick analysis:"
jq -r '.posts | {
    total_comments: (map(.commentCount // .comment_count // 0) | add),
    total_upvotes: (map(.upvotes // .score // 0) | add),
    avg_comments: ((map(.commentCount // .comment_count // 0) | add) / length),
    avg_upvotes: ((map(.upvotes // .score // 0) | add) / length)
} | "  Total comments: \(.total_comments)\n  Total upvotes: \(.total_upvotes)\n  Avg comments/post: \(.avg_comments | floor)\n  Avg upvotes/post: \(.avg_upvotes | floor)"' "$COMBINED_FILE"

echo ""
echo "Done! $(date)"
