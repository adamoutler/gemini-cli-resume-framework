#!/usr/bin/env bash

# Check for norag file to disable RAG
if [ -e ".settings/norag" ] || [ -e "$GEMINI_PROJECT_DIR/.settings/norag" ]; then
  echo "[Joplin Hook] .settings/norag present, not performing RAG." >&2
  cat <<EOF
{
  "decision": "allow"
}
EOF
  exit 0
fi

# Read the hook input from stdin
input=$(cat)

# Extract the user's prompt using jq
prompt=$(echo "$input" | jq -r '.prompt // empty')

# If there is no prompt, just return allow
if [ -z "$prompt" ]; then
  cat <<EOF
{
  "decision": "allow"
}
EOF
  exit 0
fi

# Log to stderr so it shows up in the CLI debug logs but doesn't break the JSON output
echo "[Joplin Hook] Querying semantic memory for context..." >&2

# Construct the payload safely
payload=$(jq -n --arg q "$prompt" '{query: $q, limit: 3}')

# Call the Joplin API using the environment variable for the token
api_response=$(curl -s http://192.168.1.101:30180/http-api/search \
  -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${JOPLIN_MEMORY_TOKEN}" \
  -d "$payload")

# Check if the response is empty or an error
if [ -z "$api_response" ] || echo "$api_response" | grep -q '"detail":'; then
  echo "[Joplin Hook] API error or empty response." >&2
  cat <<EOF
{
  "decision": "allow"
}
EOF
  exit 0
fi

# Parse out the blurbs to keep the injected context concise and readable.
formatted_context=$(echo "$api_response" | jq -r 'if type=="array" then (map("Note Title: " + .title + "\nContent: " + .blurb) | join("\n\n---\n\n")) else "No results." end')

# Return the hook output to Gemini CLI
jq -n --arg ctx "<joplin_memory_context>
$formatted_context
</joplin_memory_context>" '{
  "decision": "allow",
  "hookSpecificOutput": {
    "hookEventName": "BeforeAgent",
    "additionalContext": $ctx
  }
}'
