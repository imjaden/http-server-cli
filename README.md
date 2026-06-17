# http-server-cli

> 本地 HTTP 服务管理器 — 基于 `python3 -m http.server`，零外部依赖。
>
> 到项目目录下 `hs start . -o`，自动分配端口、记录路径、打开浏览器。再也不用记端口。

## 为什么需要这个工具？

| 工具 | 启动服务 | 自动分配端口 | 追踪项目↔端口 | 列出所有 | 按名杀死 | 打开浏览器 |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| `python3 -m http.server` | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| `http-server` (npm) | ✅ | ❌ | ❌ | ❌ | ❌ | ✅ |
| `serve` (npm) | ✅ | ❌ | ❌ | ❌ | ❌ | ✅ |
| `live-server` | ✅ | ✅ | ❌ | ❌ | ❌ | ✅ |
| `kill-port-cli` (npm) | ❌ | ❌ | ❌ | ✅ | ✅ | ❌ |
| `lsof` / `netstat` | ❌ | ❌ | ❌ | 手动 | 手动 | ❌ |
| **`http-server-cli`** | **✅** | **✅** | **✅** | **✅** | **✅** | **✅** |

**痛点**：你有多个项目目录，每个都需要 `python3 -m http.server 8080` 来预览静态页面。时间长了你记不住：
- 8080 被哪个项目占了？
- 8081 空闲吗？
- 项目 A 的端口是多少？
- 想关掉项目 B 的服务，PID 是啥？

**没有现成工具解决这个组合问题。** `http-server` (npm) 能启动但不会追踪。`kill-port-cli` 能杀死但不会启动。组合起来用就需要你自己记映射关系。这个 CLI 用一个 JSON registry 把"启动→追踪→列出→关闭"闭环了。

## 平台要求

当前仅支持 **macOS**（依赖 `lsof` 命令检测端口占用）。

> Linux/Windows 支持开发中（欢迎 PR：https://github.com/imjaden/http-server-cli）

## 安装

```bash
cd /path/to/http-server-cli
pip install -e .
# 安装后系统全局可用 hs 命令
```

验证安装：

```bash
hs version       # 应显示 http-server-cli v1.0.1
hs help          # 显示帮助
```

## 用法

| 命令 | 说明 |
|:---|:---|
| `hs start [path] [-o] [-d]` | 启动服务（path 默认 `.`；`-o` 打开浏览器；`-d` daemon 模式） |
| `hs list` | 列出所有运行中服务 |
| `hs status [port\|path]` | 查询单个服务状态 |
| `hs kill <port\|path>` | 关闭指定服务 |
| `hs kill-all` | 关闭所有服务（别名 `killall`） |
| `hs config` | 显示配置 |
| `hs set port <num>` | 修改默认端口（默认 8080） |
| `hs set domain <str>` | 修改绑定域名（默认 localhost） |
| `hs help` | 显示帮助 |
| `hs version` | 显示版本号 |

### 示例

```bash
# 到前端项目下无脑执行
cd ~/project-alpha
hs start . -o

# daemon 模式：查看日志，Ctrl+C 不影响服务
cd ~/project-beta
hs start . -d

# 查看所有
hs list
# ✅  http://localhost:8080  →  ~/project-alpha
# ✅  http://localhost:8081 🖥  →  ~/project-beta  (daemon)

# 关闭（按端口或按路径）
hs kill 8081
hs kill ~/project-alpha

# 一键全关
hs kill-all
```

## 工作原理

1. **`start`** → 查 registry（`~/.http-server-cli/registry.json`）→ 已注册且存活则打开浏览器 → 否则从 8080 递增找空闲端口 → `subprocess.Popen` 启动 `python3 -m http.server` → 写入 registry
2. **`start -d`**（daemon）→ 同上启动流程，然后前台 `tail -f` 日志文件 → Ctrl+C 仅停止日志查看，服务继续后台运行
3. **`list`** → 读 registry → `lsof -i :PORT` + `os.kill(pid, 0)` 双重验证存活 → 输出状态表（含 daemon 标记 🖥）
4. **`kill`** → 读 registry → SIGTERM → 等 0.5s → 未退出则 SIGKILL → 清理 registry
5. **`config`** → 读 `~/.http-server-cli/config.json`

## 数据目录

```
~/.http-server-cli/
├── config.json       # 默认端口/域名配置
├── registry.json     # port → {path, pid, domain, daemon, started_at}
└── logs/
    └── {port}.log    # http.server 日志
```

## 本地开发

```bash
cd /path/to/http-server-cli
pip install -e .           # 开发模式安装
python3 -m pytest tests/   # 运行 69 个测试
```

## 项目结构

```
http-server-cli/
├── pyproject.toml           # PEP 621, entry point `hs`
├── .gitignore
├── RELEASE.md               # 发布流程
├── src/http_server_cli/
│   ├── __init__.py          # 版本号
│   ├── __main__.py          # python -m support
│   ├── cli.py               # argparse + 命令分派
│   ├── config.py            # 配置管理（持久化）
│   ├── registry.py          # port↔project 注册表
│   ├── server.py            # 服务生命周期
│   └── utils.py             # lsof 检测、进程管理、JSON IO
├── tests/
│   ├── conftest.py
│   ├── test_config.py / test_registry.py
│   ├── test_server.py / test_utils.py
├── http-server-cli.spec.yaml # OpenSpec 规格说明书
└── setup.sh                 # alias 备用安装
```
