# Cursor MCP Configuration Setup

This directory contains configuration for Cursor's Model Context Protocol (MCP) integration with Task Master AI.

## Setup Instructions

1. **Copy the template:**
   ```bash
   cp mcp.json.template mcp.json
   ```

2. **Add your API keys:**
   Edit `.cursor/mcp.json` and replace the placeholder values:
   - `your-anthropic-api-key-here` → Your actual Anthropic API key
   - `your-perplexity-api-key-here` → Your actual Perplexity API key (optional)

3. **Security Note:**
   The `mcp.json` file is already in `.gitignore` to prevent accidentally committing your API keys.

## Configuration Options

- **ANTHROPIC_API_KEY**: Required for Task Master AI operations
- **PERPLEXITY_API_KEY**: Optional, enables research-backed features
- **MODEL**: Claude model to use (default: claude-3-7-sonnet-20250219)
- **MAX_TOKENS**: Maximum tokens per response (default: 64000)
- **TEMPERATURE**: Model creativity (default: 0.2)
- **DEFAULT_SUBTASKS**: Default subtasks per task expansion (default: 5)
- **DEFAULT_PRIORITY**: Default priority for new tasks (default: medium)

## Task Master Commands

Once configured, you'll have access to Task Master commands directly in Cursor for project management and AI-assisted development. 