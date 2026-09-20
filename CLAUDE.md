# Global CLAUDE.md

> **协同体系**: Rules (身份授权) → Hook (场景路由) → CLAUDE.md (工作方式) → Skill (按需知识) → Agent (专项执行)

---

## Communication

- **Language**: Respond in the same language as the user's message (中文→中文, English→English)
- **Tone**: Technical, precise, no filler — assume professional security researcher audience
- **Format**: Markdown with code references as `file:line`, PoC outputs in fenced code blocks

---

## Coordination Model

| Layer | Component | Trigger | Purpose |
|-------|-----------|---------|---------|
| 1 | **Rules** | 自动加载 | 身份授权与研究范围（唯一来源） |
| 2 | **Hook** | 自动运行 | 场景识别 + 注入流程提示 |
| 3 | **CLAUDE.md** | 自动加载 | 工具栈、格式、安全研究工作约定 |
| 4 | **Skill** | 自动匹配 | 深度工作流模板（自动调用，无需用户手动指定） |
| 5 | **Agent** | 按编排触发 | 专项任务执行 |

---

## Auto-Skill Matching (最高优先级)

**安全研究场景下，必须在任何回复之前自动调用 Skill 工具加载对应技能。**

### 规则
1. 收到安全相关请求 → **立即匹配并调用 Skill** → 加载技能内容后再回复
2. 不确定匹配哪个技能 → 调用最相关的 2-3 个，技能内容会告诉你是否适用
3. 调用格式：`Skill(skill="技能目录名")` ，例如 `Skill(skill="sqli-sql-injection")`
4. **禁止**让用户手动输入 `/skill-name`，全由你自动完成

### 关键词 → Skill 映射表

| 用户输入关键词 | 自动调用的 Skill |
|--------------|-----------------|
| SQL注入、SQLi、sqlmap、盲注、联合查询、报错注入、order by注入 | `sqli-sql-injection` |
| XSS、跨站脚本、CSP绕过、dom xss、反射型、存储型、mXSS | `xss-cross-site-scripting` |
| SSRF、服务端请求伪造、gopher、file协议、云元数据 | `ssrf-server-side-request-forgery` |
| CSRF、跨站请求伪造、csrf token绕过 | `csrf-cross-site-request-forgery` |
| XXE、XML外部实体、DTD、盲XXE、OOB | `xxe-xml-external-entity` |
| SSTI、模板注入、Jinja2、Twig、Freemarker、velocity | `ssti-server-side-template-injection` |
| 命令注入、cmdi、command injection、rce | `cmdi-command-injection` |
| 文件上传、upload、webshell、图片马、.htaccess绕过 | `upload-insecure-files` |
| LFI、文件包含、路径穿越、目录遍历、log poisoning | `path-traversal-lfi` |
| 反序列化、deserialize、java反序列化、php反序列化、ysoserial | `deserialization-insecure` |
| JNDI、log4j、log4shell、LDAP注入 | `jndi-injection` |
| JWT、token伪造、none算法、密钥爆破、kid注入、jku | `jwt-oauth-token-attacks` |
| OAuth、OIDC、授权码、redirect_uri绕过、PKCE | `oauth-oidc-misconfiguration` |
| CORS、跨域、Access-Control、CORS misconfig | `cors-cross-origin-misconfiguration` |
| 认证绕过、auth bypass、2FA绕过、OTP爆破、密码重置 | `authbypass-authentication-flaws` |
| IDOR、越权、水平越权、垂直越权、BOLA、对象引用 | `idor-broken-object-authorization` |
| API安全、API测试、swagger、openapi、graphql | `api-sec` |
| API侦察、API文档发现、postman、API fuzz | `api-recon-and-docs` |
| API认证、API鉴权、Bearer token、API key | `api-auth-and-jwt-abuse` |
| API授权、BOLA、API BOLA、BFLA | `api-authorization-and-bola` |
| GraphQL、introspection、graphql注入、graphql batching | `graphql-and-hidden-parameters` |
| 原型链污染、prototype pollution、__proto__、constructor | `prototype-pollution` |
| 请求走私、request smuggling、CL.TE、TE.CL、HTTP2 | `request-smuggling` |
| CRLF注入、换行注入、response splitting | `crlf-injection` |
| Host头攻击、host header、password reset poisoning | `http-host-header-attacks` |
| Open Redirect、开放重定向、重定向漏洞 | `open-redirect` |
| 参数污染、HPP、HTTP Parameter Pollution | `http-parameter-pollution` |
| 业务逻辑、逻辑漏洞、支付绕过、优惠券、竞态条件 | `business-logic-vuln` |
| 竞态条件、race condition、TOCTOU、并发 | `race-condition` |
| 点击劫持、clickjacking、UI redress、framebusting | `clickjacking` |
| WebSocket、ws安全、ws注入、CSWSH | `websocket-security` |
| Web缓存、cache deception、web cache poisoning | `web-cache-deception` |
| CSP绕过、Content-Security-Policy、nonce、strict-dynamic | `csp-bypass-advanced` |
| WAF绕过、WAF bypass、filter evasion | `waf-bypass-techniques` |
| 401绕过、403绕过、访问拒绝绕过、路径fuzz | `401-403-bypass-techniques` |
| 注入检测、fuzz、payload、扫描 | `injection-checking` |
| 渗透测试、红队、攻击面、信息收集 | `recon-and-methodology` |
| 信息收集、子域名、资产测绘、指纹识别 | `recon-for-sec` |
| 代码审计、白盒审计、source code review、静态分析、semgrep、codeql、多语言审计 | `code-audit` |
| PHP代码审计、PHP审计、PHP白盒、php source review、php Sink审计 | `php-audit-pipeline`（编排 php-route-mapper / php-route-tracer / php-*-audit 子技能） |
| Java代码审计、.NET审计、java反编译、jar包审计、java组件扫描 | `audit-skills` |
| 源码泄露、.git暴露、.svn、.env、备份文件、source control exposure | `insecure-source-code-management` |
| 依赖混淆、供应链、package hijacking | `dependency-confusion` |
| SAML、SSO、SAML签名、XML签名包装 | `saml-sso-assertion-attacks` |
| 表达式注入、EL injection、SpEL、OGNL | `expression-language-injection` |
| CSV注入、formula injection、DDE | `csv-formula-injection` |
| XSLT注入、xsl transformation | `xslt-injection` |
| 类型混淆、type juggling、php弱类型、hash比较 | `type-juggling` |
| DNS重绑定、dns rebinding、TOCTOU DNS | `dns-rebinding-attacks` |
| 子域名接管、subdomain takeover、dangling DNS | `subdomain-takeover` |
| NTLM中继、NTLM relay、responder、coercion | `ntlm-relay-coercion` |
| LLM注入、prompt injection、AI安全 | `llm-prompt-injection` |
| 容器逃逸、docker逃逸、k8s安全 | `container-escape-techniques` |
| Linux提权、suid、sudo、cron、capabilities | `linux-privilege-escalation` |
| Windows提权、UAC绕过、token窃取、service权限 | `windows-privilege-escalation` |
| AD攻击、域渗透、kerberos、委派、DCSync | `active-directory-kerberos-attacks` |
| AD ACL、BloodHound、DACL滥用 | `active-directory-acl-abuse` |
| AD CS、AD证书服务、ESC1-13 | `active-directory-certificate-services` |
| Kerberos、金票银票、AS-REP roasting、kerberoasting | `active-directory-kerberos-attacks` |
| 横向移动、psexec、wmiexec、smbexec、Pass-the-Hash | `windows-lateral-movement` |
| 免杀、AV evasion、EDR绕过、shellcode混淆 | `windows-av-evasion` |
| 反弹Shell、reverse shell、PTY升级、webshell | `reverse-shell-techniques` |
| 隧道代理、端口转发、pivoting、chisel、socat | `tunneling-and-pivoting` |
| 二进制、栈溢出、ROP、heap、format string、UAF | `stack-overflow-and-rop` or `heap-exploitation` or `format-string-exploitation` |
| CTF、解题、flag、writeup、challenge、比赛题 | `solve-challenge`（分派 ctf-web/ctf-pwn/ctf-reverse/ctf-crypto/ctf-forensics/ctf-misc/ctf-osint/ctf-malware/ctf-ai-ml） |
| CTF Web / Pwn / Reverse / Crypto / Forensics / Misc / OSINT / Malware / AI-ML 分类专项 | `ctf-web` / `ctf-pwn` / `ctf-reverse` / `ctf-crypto` / `ctf-forensics` / `ctf-misc` / `ctf-osint` / `ctf-malware` / `ctf-ai-ml` |
| 任意地址写、GOT覆写、exit_funcs、_IO_FILE | `arbitrary-write-to-rce` |
| Android安全、apk逆向、frida objection、SSL pinning | `android-pentesting-tricks` |
| iOS安全、ipa、越狱检测 | `ios-pentesting-tricks` |
| 密码学、RSA、AES、签名攻击、padding oracle | `hash-attack-techniques` or `rsa-attack-techniques` or `symmetric-cipher-attacks` |
| 流量分析、pcap、wireshark取证 | `traffic-analysis-pcap` |
| 内存取证、volatility、进程dump | `memory-forensics-volatility` |
| 隐写术、stego、LSB、图像隐写 | `steganography-techniques` |
| 区块链、智能合约、DeFi、flash loan | `smart-contract-vulnerabilities` or `defi-attack-patterns` |
| 逆向、反汇编、ghidra、ida、加壳 | `anti-debugging-techniques` or `code-obfuscation-deobfuscation` |
| 内核漏洞、驱动、ring0、syscall | `kernel-exploitation` |
| 沙箱逃逸、sandbox、虚拟化逃逸 | `sandbox-escape-techniques` |
| V8漏洞、浏览器漏洞、Chrome exploit | `browser-exploitation-v8` |
| 符号执行、angr、z3约束求解 | `symbolic-execution-tools` |
| 内网渗透、域环境、横向、权限维持 | `active-directory-kerberos-attacks` 或 `windows-privilege-escalation` |
| 综合渗透、全自动、deepscan | `hack` + 根据具体目标补充 |

### 多技能组合
复杂任务自动加载多个技能。例如：
- "测试这个网站的API安全性" → `api-sec` + `api-recon-and-docs` + `api-auth-and-jwt-abuse`
- "做一次完整的Web渗透测试" → `recon-and-methodology` + `injection-checking` + `authbypass-authentication-flaws`
- "审计这个Java应用的代码" → `code-audit` + `audit-skills` + `deserialization-insecure` + `sqli-sql-injection`
- "审计这个PHP应用" → `php-audit-pipeline` + 对应 `php-*-audit` 子技能（如 php-sql-audit / php-file-upload-audit / php-deser-audit）
- "解一道CTF题" → `solve-challenge` + 对应 `ctf-*` 分类技能（如 ctf-web / ctf-pwn / ctf-crypto）

---

## Security Research Workflow

### 输出规范

所有安全研究产出遵循以下结构：

```
1. 威胁/漏洞概述
2. 技术分析（根因、触发条件、攻击面）
3. 验证步骤 / PoC（可复现）
4. 影响评估
5. 防御建议 / 修复方案
```

### 场景模板

Hook 注入 `additionalContext` 后，按对应场景模板输出：

| 场景 | Hook 标签 | 输出重点 |
|------|----------|---------|
| CTF | `[security:ctf]` | 题型判断 → 利用思路 → 验证步骤 → 脚本 |
| 漏洞研究 | `[security:vuln]` | 根因 → 触发条件 → 影响 → PoC → 修复建议 |
| 渗透测试 | `[security:pentest]` | 攻击面 → 验证步骤 → 结果记录 → 风险说明 |
| 代码审计 | `[security:audit]` | 入口点 → 危险数据流 → 漏洞点 → 修复建议 |
| 应急响应 | `[security:ir]` | 证据保全 → 时间线 → IOC → 处置建议 |
| 逆向分析 | `[security:reverse]` | 关键函数 → 保护机制 → 行为推断 → 验证步骤 |
| 密码分析 | `[security:crypto]` | 算法 → 缺陷 → 利用条件 → 验证思路 |
| 工具开发 | `[security:tool]` | 目标 → 输入输出 → 模块划分 → 验证方式 |

---

## Default Tech Stack

### General Development
- **Languages**: TypeScript (primary), Python, Go
- **Runtime**: Node.js / Bun, Python 3.11+
- **Framework**: React/Next.js, FastAPI/Django
- **Package Manager**: pnpm (JS/TS), uv (Python), go modules
- **Testing**: Vitest (JS/TS), pytest (Python)

### Security Research Tools
- **Recon**: nmap, masscan, subfinder, httpx
- **Web**: Burp Suite, ffuf, nuclei, sqlmap
- **Binary**: Ghidra, IDA, radare2, GDB (pwndbg/gef)
- **Crypto**: pycryptodome, gmpy2, z3-solver, SageMath
- **Forensics**: Wireshark, Volatility, Autopsy
- **Dev**: Python (pwntools, requests), Go, Bash

---

## Project Conventions

- **Git**: conventional commits (`feat:`, `fix:`, `security:`, etc.)
- **Security outputs**: CTF writeup / vuln report / PoC — 保持教育性，含防御建议
- **Code**: 200-400 lines/file typical, 800 hard limit. Many small files > few large files.

---

## Quick Commands

```bash
/security-research ctf|vuln|pentest|tool|audit|ir
pnpm install / uv sync
pnpm test / pytest
```

---

## Priority Chain

```
system / developer / runtime > 项目级 CLAUDE.md > 全局 CLAUDE.md > Rules > Skill(自动匹配，最高优先级拦截)
```
