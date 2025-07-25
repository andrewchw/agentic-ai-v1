#!/bin/bash

# Pre-commit hook to prevent API key leaks
# Place this in .git/hooks/pre-commit and make it executable

echo "🔍 Checking for potential API key leaks..."

# Define patterns to search for
patterns=(
    "sk-or-v1-[a-zA-Z0-9]+"              # OpenRouter API keys
    "sk-[a-zA-Z0-9]{32,}"                 # General API keys starting with sk-
    "OPENROUTER_API_KEY\s*=\s*[\"']sk-"   # Environment variable assignments
    "api[_-]?key\s*[=:]\s*[\"'][a-zA-Z0-9_-]{20,}[\"']"  # General API key patterns
)

# Files to exclude from checks
exclude_files=(
    ".env.example"
    "*.template"
    "*.md"
    "setup_secure_environment.ps1"
    "pre-commit-hook.sh"
)

# Check staged files
staged_files=$(git diff --cached --name-only --diff-filter=ACM)

leak_found=false

for file in $staged_files; do
    # Skip if file is in exclude list
    skip=false
    for exclude in "${exclude_files[@]}"; do
        if [[ "$file" == $exclude ]]; then
            skip=true
            break
        fi
    done
    
    if [[ "$skip" == true ]]; then
        continue
    fi
    
    # Check each pattern
    for pattern in "${patterns[@]}"; do
        if git show ":$file" | grep -E "$pattern" > /dev/null; then
            echo "❌ Potential API key leak detected in: $file"
            echo "   Pattern: $pattern"
            leak_found=true
        fi
    done
done

if [[ "$leak_found" == true ]]; then
    echo ""
    echo "🚫 COMMIT BLOCKED: Potential API key leak detected!"
    echo ""
    echo "Please:"
    echo "1. Remove hardcoded API keys from the files"
    echo "2. Use environment variables instead"
    echo "3. Add sensitive files to .gitignore if needed"
    echo ""
    echo "For help, see: setup_secure_environment.ps1"
    exit 1
fi

echo "✅ No API key leaks detected. Commit allowed."
exit 0
