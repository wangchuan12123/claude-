#!/usr/bin/env python3
"""
鸾鸟 (LuaN1aoAgent) API 客户端 — Claude Code 集成层

提供 Claude Code 与 鸾鸟自主渗透测试智能体之间的交互接口。

功能:
  - launch(task)        → 启动渗透测试任务
  - status(op_id)       → 查询任务状态与进度
  - result(op_id)       → 获取完整测试报告
  - inject(op_id, msg)  → 人工介入注入子任务
  - abort(op_id)        → 终止任务
  - list_ops()          → 列出所有任务
  - events(op_id)       → SSE 实时事件流

架构:
  Claude Code (分析/决策) ←→ luan1ao_client.py ←→ 鸾鸟 Web API (:8000)
                                                      ↓
                                                  P-E-R Agent
                                                  (Planner/Executor/Reflector)

使用示例:
  from luan1ao_client import Luan1aoClient
  client = Luan1aoClient()
  op = client.launch(
      goal="对 http://testphp.vulnweb.com 进行 Web 安全测试",
      human_in_the_loop=True,
  )
  client.wait_for_completion(op["op_id"])
  report = client.get_report(op["op_id"])
"""

import httpx
import json
import time
import sys
import os
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime

# ============================================================
# Configuration
# ============================================================

LUAN1AO_HOST = os.getenv("LUAN1AO_HOST", "127.0.0.1")
LUAN1AO_PORT = int(os.getenv("LUAN1AO_PORT", "8000"))
LUAN1AO_BASE_URL = f"http://{LUAN1AO_HOST}:{LUAN1AO_PORT}"


@dataclass
class OpStatus:
    """任务状态快照"""
    op_id: str
    name: str
    goal: str
    status: str  # pending / running / completed / failed / aborted
    created_at: str
    updated_at: str
    config: Dict[str, Any] = field(default_factory=dict)


class Luan1aoClient:
    """鸾鸟 API 客户端"""

    def __init__(self, base_url: str = LUAN1AO_BASE_URL, timeout: float = 10.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.client = httpx.Client(timeout=httpx.Timeout(timeout))

    # ============================================================
    # Task Management
    # ============================================================

    def launch(
        self,
        goal: str,
        task_name: Optional[str] = None,
        human_in_the_loop: bool = False,
        output_mode: str = "default",
        llm_planner_model: str = "",
        llm_executor_model: str = "",
        llm_reflector_model: str = "",
    ) -> Dict[str, Any]:
        """
        启动一个新的渗透测试任务。

        参数:
          goal: 测试目标描述，例如 "对 http://target.com 进行全面 Web 安全测试"
          task_name: 任务名称（可选，默认自动生成）
          human_in_the_loop: 是否开启人机协同模式
          output_mode: 输出模式 (simple / default / debug)
        """
        payload = {
            "goal": goal,
            "task_name": task_name or f"claude_task_{int(time.time())}",
            "human_in_the_loop": human_in_the_loop,
            "output_mode": output_mode,
        }
        if llm_planner_model:
            payload["llm_planner_model"] = llm_planner_model
        if llm_executor_model:
            payload["llm_executor_model"] = llm_executor_model
        if llm_reflector_model:
            payload["llm_reflector_model"] = llm_reflector_model

        r = self.client.post(f"{self.base_url}/api/ops", json=payload)
        r.raise_for_status()
        return r.json()

    def list_ops(self) -> List[Dict[str, Any]]:
        """列出所有渗透测试任务"""
        r = self.client.get(f"{self.base_url}/api/ops")
        r.raise_for_status()
        return r.json()

    def get_op(self, op_id: str) -> Dict[str, Any]:
        """获取单个任务详情"""
        r = self.client.get(f"{self.base_url}/api/ops/{op_id}")
        r.raise_for_status()
        return r.json()

    def get_status(self, op_id: str) -> OpStatus:
        """获取任务状态快照"""
        data = self.get_op(op_id)
        return OpStatus(
            op_id=data["id"],
            name=data["name"],
            goal=data["goal"],
            status=data["status"],
            created_at=data.get("created_at", ""),
            updated_at=data.get("updated_at", ""),
            config=data.get("config", {}),
        )

    def abort(self, op_id: str) -> Dict[str, Any]:
        """终止一个正在运行的任务"""
        r = self.client.post(f"{self.base_url}/api/ops/{op_id}/abort")
        r.raise_for_status()
        return r.json()

    def delete_ops(self, op_ids: List[str]) -> Dict[str, Any]:
        """删除任务记录"""
        r = self.client.request(
            "DELETE", f"{self.base_url}/api/ops",
            json={"op_ids": op_ids},
        )
        r.raise_for_status()
        return r.json()

    # ============================================================
    # Intervention (Human-in-the-Loop)
    # ============================================================

    def check_intervention(self, op_id: str) -> Optional[Dict[str, Any]]:
        """检查是否有待审批的人工介入请求"""
        r = self.client.get(f"{self.base_url}/api/ops/{op_id}/intervention/pending")
        r.raise_for_status()
        data = r.json()
        return data if data else None

    def decide_intervention(self, op_id: str, request_id: str, decision: str, feedback: str = "") -> Dict[str, Any]:
        """
        对人工介入请求做出决策。

        参数:
          op_id: 任务ID
          request_id: 介入请求ID
          decision: "approve" / "reject" / "modify"
          feedback: 反馈/修改意见
        """
        payload = {
            "request_id": request_id,
            "decision": decision,
            "feedback": feedback,
        }
        r = self.client.post(
            f"{self.base_url}/api/ops/{op_id}/intervention/decision",
            json=payload,
        )
        r.raise_for_status()
        return r.json()

    def inject_task(self, op_id: str, message: str) -> Dict[str, Any]:
        """
        向运行中的任务注入子任务/指令。

        参数:
          op_id: 任务ID
          message: 注入的指令内容
        """
        payload = {"message": message}
        r = self.client.post(
            f"{self.base_url}/api/ops/{op_id}/inject_task",
            json=payload,
        )
        r.raise_for_status()
        return r.json()

    # ============================================================
    # Graph & Visualization
    # ============================================================

    def get_execution_graph(self, op_id: Optional[str] = None) -> Dict[str, Any]:
        """获取执行图（DAG）"""
        params = {"op_id": op_id} if op_id else {}
        r = self.client.get(f"{self.base_url}/api/graph/execution", params=params)
        r.raise_for_status()
        return r.json()

    def get_causal_graph(self, op_id: Optional[str] = None) -> Dict[str, Any]:
        """获取因果图"""
        params = {"op_id": op_id} if op_id else {}
        r = self.client.get(f"{self.base_url}/api/graph/causal", params=params)
        r.raise_for_status()
        return r.json()

    def get_execution_tree(self, op_id: Optional[str] = None) -> Dict[str, Any]:
        """获取执行树"""
        params = {"op_id": op_id} if op_id else {}
        r = self.client.get(f"{self.base_url}/api/tree/execution", params=params)
        r.raise_for_status()
        return r.json()

    # ============================================================
    # LLM Events
    # ============================================================

    def get_llm_events(self, op_id: str) -> List[Dict[str, Any]]:
        """获取 LLM 调用事件记录"""
        r = self.client.get(f"{self.base_url}/api/ops/{op_id}/llm-events")
        r.raise_for_status()
        return r.json()

    # ============================================================
    # High-Level Helpers
    # ============================================================

    def wait_for_completion(
        self,
        op_id: str,
        poll_interval: float = 10.0,
        timeout: Optional[float] = None,
        verbose: bool = True,
    ) -> OpStatus:
        """
        轮询等待任务完成。

        参数:
          op_id: 任务ID
          poll_interval: 轮询间隔（秒）
          timeout: 超时时间（秒），None 表示不限制
          verbose: 是否打印进度
        """
        start = time.time()
        last_log = ""
        while True:
            status = self.get_status(op_id)

            # Print progress updates
            if verbose and status.status != last_log:
                elapsed = time.time() - start
                print(f"[{elapsed:6.0f}s] {op_id[:20]}... → {status.status}")
                last_log = status.status

            if status.status in ("completed", "failed", "aborted"):
                return status

            if timeout and (time.time() - start) > timeout:
                raise TimeoutError(f"Task {op_id} did not complete within {timeout}s")

            time.sleep(poll_interval)

    def get_report(self, op_id: str) -> Dict[str, Any]:
        """
        获取任务完整报告（包含图、事件、状态）。

        返回:
          {
            "status": OpStatus,
            "execution_graph": ...,
            "causal_graph": ...,
            "llm_events": ...,
          }
        """
        return {
            "status": self.get_status(op_id),
            "execution_graph": self.get_execution_graph(op_id),
            "causal_graph": self.get_causal_graph(op_id),
            "llm_events": self.get_llm_events(op_id),
        }

    def summary(self, op_id: str) -> str:
        """
        生成人类可读的任务总结。

        返回适合 Claude Code 上下文使用的文本总结。
        """
        try:
            report = self.get_report(op_id)
        except Exception as e:
            return f"[鸾鸟] 无法获取 {op_id} 的报告: {e}"

        status = report["status"]
        lines = [
            "=" * 60,
            f"  鸾鸟渗透测试报告 — {op_id}",
            "=" * 60,
            f"  任务名称: {status.name}",
            f"  测试目标: {status.goal}",
            f"  状态:     {status.status}",
            f"  创建时间: {status.created_at}",
            f"  更新时间: {status.updated_at}",
            "",
            "  [执行图节点]",
        ]

        exec_graph = report.get("execution_graph", {})
        nodes = exec_graph.get("nodes", [])
        edges = exec_graph.get("edges", [])

        for node in nodes[:20]:  # Limit to 20 nodes
            node_id = node.get("id", "?")
            node_type = node.get("type", "?")
            node_status = node.get("status", "?")
            node_label = node.get("label", "")[:80]
            lines.append(f"    [{node_type}] {node_label} ({node_status})")

        if len(nodes) > 20:
            lines.append(f"    ... 及其他 {len(nodes) - 20} 个节点")

        lines.append("")
        lines.append(f"  边: {len(edges)}")
        lines.append("")
        lines.append("  [LLM 调用统计]")

        events = report.get("llm_events", [])
        if events:
            by_role = {}
            for ev in events:
                role = ev.get("role", "unknown")
                by_role[role] = by_role.get(role, 0) + 1
            for role, count in sorted(by_role.items()):
                lines.append(f"    {role}: {count} 次调用")
        else:
            lines.append("    (无事件记录)")

        lines.append("=" * 60)
        return "\n".join(lines)


# ============================================================
# CLI
# ============================================================

if __name__ == "__main__":
    client = Luan1aoClient()

    if len(sys.argv) < 2:
        print("Usage:")
        print("  python luan1ao_client.py launch <goal> [--hitl]")
        print("  python luan1ao_client.py list")
        print("  python luan1ao_client.py status <op_id>")
        print("  python luan1ao_client.py report <op_id>")
        print("  python luan1ao_client.py abort <op_id>")
        print("  python luan1ao_client.py inject <op_id> <message>")
        sys.exit(0)

    cmd = sys.argv[1]

    if cmd == "launch":
        goal = sys.argv[2] if len(sys.argv) > 2 else input("Goal: ")
        hitl = "--hitl" in sys.argv
        op = client.launch(goal=goal, human_in_the_loop=hitl)
        print(f"Launched: {op}")

    elif cmd == "list":
        ops = client.list_ops()
        for op in ops:
            print(f"  [{op.get('status','?')}] {op.get('id','?')} — {op.get('goal','?')[:60]}")

    elif cmd == "status":
        op_id = sys.argv[2]
        status = client.get_status(op_id)
        print(f"Status: {status}")

    elif cmd == "report":
        op_id = sys.argv[2]
        print(client.summary(op_id))

    elif cmd == "abort":
        op_id = sys.argv[2]
        client.abort(op_id)
        print(f"Aborted {op_id}")

    elif cmd == "inject":
        op_id = sys.argv[2]
        message = " ".join(sys.argv[3:])
        client.inject_task(op_id, message)
        print(f"Injected to {op_id}")
