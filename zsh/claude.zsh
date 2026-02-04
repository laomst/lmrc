# 使用 GLM (智谱 AI) 模型运行 Claude Code
claude-glm() {
  [[ -z "$GLM_API_KEY" ]] && { echo "Error: GLM_API_KEY is not set" >&2; return 1; }
  ANTHROPIC_AUTH_TOKEN="$GLM_API_KEY" \
  ANTHROPIC_BASE_URL="https://open.bigmodel.cn/api/anthropic" \
  ANTHROPIC_MODEL="glm-4.7" \
  ANTHROPIC_DEFAULT_HAIKU_MODEL="glm-4.5-air" \
  ANTHROPIC_DEFAULT_SONNET_MODEL="glm-4.7" \
  ANTHROPIC_DEFAULT_OPUS_MODEL="glm-4.7" \
  API_TIMEOUT_MS=300000 \
  CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1 \
  claude "$@"
}

# 使用 MiniMax 模型运行 Claude Code
claude-minimax() {
  [[ -z "$MINIMAX_KEY" ]] && { echo "Error: MINIMAX_KEY is not set" >&2; return 1; }
  ANTHROPIC_AUTH_TOKEN="$MINIMAX_KEY" \
  ANTHROPIC_BASE_URL="https://api.minimaxi.com/anthropic" \
  ANTHROPIC_MODEL="MiniMax-M2.1" \
  ANTHROPIC_DEFAULT_HAIKU_MODEL="MiniMax-M2.1" \
  ANTHROPIC_DEFAULT_SONNET_MODEL="MiniMax-M2.1" \
  ANTHROPIC_DEFAULT_OPUS_MODEL="MiniMax-M2.1" \
  API_TIMEOUT_MS=300000 \
  CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1 \
  claude "$@"
}