# Claude ↔ 鸾鸟 ↔ PentAGI 协同渗透测试工作流

## 架构

```
┌─────────────────────────────────────────────────────────┐
│                    Claude Code (我)                       │
│  角色: 总指挥 — 高层分析、策略决策、漏洞验证、报告编写      │
│                                                         │
│  ┌──────────────────────────────────────────────────┐   │
│  │           luan1ao_client.py                       │   │
│  │   Python API 客户端 — 与鸾鸟 Web API 通信          │   │
│  └──────────────┬───────────────────────────────────┘   │
└─────────────────┼───────────────────────────────────────┘
                  │ HTTP REST (:8000)
┌─────────────────┼───────────────────────────────────────┐
│                 ▼                                        │
│         鸾鸟 LuaN1aoAgent (自主渗透引擎)                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────────┐          │
│  │ Planner  │→│ Executor │→│  Reflector    │          │
│  │ (规划)   │  │ (执行)   │  │  (反思/归因)  │          │
│  └──────────┘  └──────────┘  └──────────────┘          │
│       │              │               │                  │
│       ▼              ▼               ▼                  │
│  ┌──────────────────────────────────────────────┐      │
│  │  MCP 工具层                                    │      │
│  │  http_request | shell_exec | python_exec      │      │
│  │  nuclei_scan  | sqlmap     | dirsearch        │      │
│  │  web_search   | search_exploit | think        │      │
│  └──────────────────────────────────────────────┘      │
│       │                                                 │
│       ▼                                                 │
│  ┌──────────────────────────────────────────────┐      │
│  │  RAG 知识库 (FAISS + PayloadsAllTheThings)     │      │
│  └──────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────┘
                  │ (Docker, 需要时)
┌─────────────────┼───────────────────────────────────────┐
│                 ▼                                        │
│          PentAGI (沙箱化渗透平台)                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────────┐          │
│  │Orchestrator│→│ Researcher│→│  Developer   │          │
│  └──────────┘  └──────────┘  └──────────────┘          │
│       │                                            │     │
│       ▼                                            ▼     │
│  ┌──────────┐  ┌──────────────────────────────┐        │
│  │ Executor │  │  Neo4j 知识图谱 + PostgreSQL   │        │
│  └──────────┘  └──────────────────────────────┘        │
└─────────────────────────────────────────────────────────┘
```

## 协同模式

### 模式 1: Claude 主导 + 鸾鸟自动化执行

**场景**: 给定渗透测试目标，Claude 进行高层分析和策略规划，鸾鸟执行自动化扫描。

**流程**:
```
1. Claude 分析目标 → 确定测试范围和策略
2. Claude 通过 luan1ao_client 启动 鸾鸟任务
3. 鸾鸟 P-E-R 循环自主执行
4. Claude 定期轮询 status/events 监控进度
5. Claude 通过 inject_task 实时注入专家指导
6. 鸾鸟完成后，Claude 分析结果、验证漏洞
7. Claude 编写最终渗透测试报告
```

**触发**: 用户说 "渗透测试 http://target.com"

### 模式 2: 人机协同 (HITL)

**场景**: 复杂测试需要 Claude 在关键节点审批决策。

**流程**:
```
1. 以 human_in_the_loop=true 启动 鸾鸟
2. 鸾鸟在每个关键决策点暂停 → 发介入请求
3. Claude 通过 check_intervention 检测待审批项
4. Claude 分析后调用 decide_intervention (approve/reject/modify)
5. 循环直到测试完成
```

**触发**: 高风险目标或需要精细控制的测试

### 模式 3: Claude 手工 + 鸾鸟辅助

**场景**: Claude 手动测试，鸾鸟提供知识检索和工具执行。

**流程**:
```
1. Claude 手工分析目标的特定漏洞点
2. 需要 Payload 时 → 查询 鸾鸟 RAG 知识库
3. 需要自动化扫描时 → Claude 构造子任务注入 鸾鸟
4. 鸾鸟执行具体工具调用返回结果
5. Claude 基于结果继续下一步
```

**触发**: 针对特定漏洞类型的精细化测试

## 目录结构

```
~/.claude/tools/
├── luan1ao_client.py   # 鸾鸟 API 客户端
├── start_luan1ao.sh    # 鸾鸟 启动脚本
└── setup_pentagi.sh    # PentAGI 部署脚本

~/LuaN1aoAgent/         # 鸾鸟 主目录
├── .env                # API 配置 (DeepSeek V4 Pro)
├── agent.py            # Agent 主程序
├── web/server.py       # Web API (FastAPI :8000)
├── mcp.json            # MCP 工具配置
├── rag/                # RAG 知识库 (FAISS)
└── knowledge_base/     # PayloadsAllTheThings
```

## 快速开始

### 1. 启动鸾鸟

```bash
# 终端 1: 启动 Web 控制台
bash ~/.claude/tools/start_luan1ao.sh

# 浏览器打开: http://127.0.0.1:8000
```

### 2. Claude 启动渗透测试

```python
# 在 Claude 对话中，我会自动执行:
from luan1ao_client import Luan1aoClient
client = Luan1aoClient()

# 启动一个任务
op = client.launch(
    goal="对 http://testphp.vulnweb.com 进行全面的 Web 安全测试，重点关注 SQL 注入和 XSS",
    human_in_the_loop=False,
)

# 等待完成
status = client.wait_for_completion(op["op_id"], timeout=3600)
print(client.summary(op["op_id"]))
```

### 3. Claude 协同介入

```python
# 注入新任务
client.inject_task(op_id, "用 sqlmap 对 /artists.php?id=1 进行完整测试")

# 查看执行图
graph = client.get_execution_graph(op_id)
causal = client.get_causal_graph(op_id)
```

## 环境要求

| 工具 | 状态 | API | 端口 |
|------|------|-----|------|
| 鸾鸟 LuaN1aoAgent | ✅ 已部署 | DeepSeek V4 Pro | 8000 (Web), 8081 (Knowledge) |
| PentAGI | ⏳ 需 Docker | 待配置 | 3000 (Web), 8080 (API) |
| Claude 集成层 | ✅ 已配置 | — | — |

## API Key

使用与 Claude Code 相同的 DeepSeek API Key:
- Key: `sk-834183a54b76432da23753fd92fc5b42`
- Endpoint: `https://api.deepseek.com/chat/completions`
- Model: `deepseek-v4-pro`
