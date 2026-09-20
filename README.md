# Claude 配置同步仓库（PRIVATE）

这是 `~/.claude` 的**白名单式** git 同步仓库：只同步下面列出的内容，其余全部忽略。

## 同步内容
- `skills/` — 安全研究技能库（数百个 php-*/ctf-*/superpowers:* 技能）
- `hooks/` — 自定义 Hook（`security-context-hook.py`）
- `rules/` — 全局 Rules（`security-research-context.md`）
- `tools/` — 自定义渗透工具脚本（含本机绝对路径，跨机需适配）
- `agents/` — 自定义 Agent（预留）
- `memory/` — 跨机记忆（`settings.json` 的 `autoMemoryDirectory` 指向此处）
- `CLAUDE.md` — 全局指令

## 明确不同步（含密钥 / 本机专属）
- `settings.json` — 含 `ANTHROPIC_AUTH_TOKEN`（API 密钥）
- `.mcp.json` — 含 `ARL_TOKEN`（API 密钥）
- `settings.local.json` — 本机权限 allow 列表
- `projects/`、`sessions/`、`history.jsonl`、`jobs/`、`cache/`、`telemetry/`、`plugins/` 等 — 会话/缓存，本机专属

## 日常推送
```bash
cd ~/.claude
git add -A && git commit -m "sync" && git push
```

## 新机器恢复
`settings.json` / `.mcp.json` / `settings.local.json` 不在仓库内（含密钥），需在新机器手动重建。
同步内容可这样恢复：

```bash
git clone <this-repo> /tmp/claude-sync
cp -r /tmp/claude-sync/skills /tmp/claude-sync/hooks /tmp/claude-sync/rules \
      /tmp/claude-sync/tools /tmp/claude-sync/CLAUDE.md ~/.claude/
mkdir -p ~/.claude/memory
```
