#!/bin/bash
# http-server-cli 安装脚本
# 用法: cd 到脚本目录后执行 bash setup.sh
#
# 推荐方式（全局可用）:
#   pip install -e .
#
# 备用方式（仅当前 shell）:
#   source alias.sh

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

cat > "${SCRIPT_DIR}/alias.sh" << 'ALIAS_EOF'
# http-server-cli alias
# 添加到 .zshrc:
#   source /path/to/http-server-cli/alias.sh
#
# 或直接 pip install -e . 使用全局 hs 命令

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
alias hs="python3 \"${SCRIPT_DIR}/src/http_server_cli/cli.py\""
alias hs-help='hs help'
alias hs-list='hs list'
alias hs-killall='hs kill-all'
alias hs-config='hs config'
ALIAS_EOF

# 标记可执行（方便直接 python3 cli.py）
chmod +x "${SCRIPT_DIR}/src/http_server_cli/cli.py" 2>/dev/null || true

echo "✅ alias 文件已生成: ${SCRIPT_DIR}/alias.sh"
echo ""
echo "推荐安装方式:"
echo "  pip install -e ."
echo ""
echo "或添加到 shell 配置（备用）:"
echo "  echo 'source ${SCRIPT_DIR}/alias.sh' >> ~/.zshrc && source ~/.zshrc"
echo ""
echo "使用示例:"
echo "  hs start . -o     当前目录启动 + 打开浏览器"
echo "  hs list           查看所有服务"
echo "  hs config         查看配置"
