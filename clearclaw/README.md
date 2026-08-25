<div align="center">

# ClearClaw

<p align="center"> <strong>透明 · 记忆 · 协同 · 可信</strong><br> <em>让每个智能体的决策都被看见，让每次协作都有迹可循</em> </p><p align="center"></p>

</div>

<a id="中文"></a>


## 📖 简介

ClearClaw 是一个可信多智能体框架。它打破了传统 AI 黑箱的桎梏，通过行为透明化、长期记忆塑造、知识增强检索和团队化智能协作，为复杂业务场景提供可靠、可审计、可持续进化的自动化解决方案。

### 🔌 技能生态兼容

ClearClaw 支持**OpenClaw**技能和**Claude Code**技能，可直接使用两个生态系统的丰富技能资源，无需重新开发。

### 🧭 核心理念

| 理念 | 诠释 |
|------|------|
| **透明即信任** | 诠释每一个决策、每一次工具调用、每一条推理路径都以人类可读的日志和终端可视化呈现，拒绝黑箱。 |
| **记忆即成长** | 系统会持续学习用户偏好与任务模式，构建“长期个性档案”与“短期工作记忆”，越用越懂你。 |
| **知识即力量** | 内置 RAG 引擎，让智能体能够实时查阅企业文档、技术规范、历史记录，做到“言之有据”。|
| **协作即增效** | 多个智能体分工协作（规划师、执行者、质检员），像团队一样配合，处理复杂任务游刃有余。 |
| **安全即底线** | 所有操作限定在可控“工位”内，关键动作需二次确认，从根本上杜绝灾难性误操作。 |

---

## ✨ 功能特性

🧠 **双层记忆体系**  
<br>
长期个性档案：以 Markdown 文件存储用户习惯、偏好、历史结论，形成持久化“数字分身”。

短期工作记忆：以轻量级 SQLite 记录最近对话与上下文，实现快速的短期回忆。
注：RAG 知识库检索临时工具消息默认不存入短期工作记忆，会话持久化仅保留用户消息与助手回答，以保证数据实时性。

两者协同，让智能体既能记住你的喜好，又能紧跟当前话题。
<br><br>

🔍 **行为溯源日志**  
<br>
记录 5 大类关键事件：用户输入、LLM 思考、工具调用、工具返回、系统动作。

输出为结构化 JSONL 日志，同时提供 Rich 终端仪表盘，实时滚动显示系统内部状态。

支持事后回放、合规审计、性能分析。
<br><br>

📚 **知识增强检索（RAG）——全新能力**  
<br>
内置检索增强引擎，基于 Chroma 向量数据库实现稠密向量检索，默认接入阿里云通义千问 Embedding 模型。

支持 PDF、Word、Markdown、HTML、TXT 等格式文档批量索引；内置文档哈希变更检测，知识库文件改动后自动触发增量索引。

检索结果携带文档来源信息，智能体回答时可引用原文片段，构建可溯源知识问答。
<br><br>

⚖️ **审阅后执行机制**  
<br>
智能体在调用任何高危工具前，必须先输出“操作说明书”，由用户（或审批规则）确认后方可执行。

这种 “先亮牌，后出手” 的模式，降低灾难性操作风险。
<br><br>


🤝 **多智能体协同（Multi-Agent Collaboration）——全新能力**  
<br>
规划师（Planner）：拆解复杂目标，生成子任务分解图。

执行者（Executor）：按计划调用工具、检索知识、执行具体操作。

质检员（Validator）：交叉验证结果，检查一致性与完整性，提出改进建议。

支持三种协作模式：流水线式（顺序）、并行式（同时）、迭代式（反馈优化）。
<br><br>


⏰ **智能计划任务引擎**  
<br>
独立后台进程，支持一次性、每日、每周、每月及自定义 Cron 式定时任务。

任务可调用技能、RAG 查询或触发多智能体工作流。
<br><br>


🔌 **开放插件生态**  
<br>
兼容 OpenClaw 和 Claude Code 的技能定义（SKILL.md），只需放入 workspace/office/skills/ 即可自动识别。

同时支持自定义 Python 工具函数，通过装饰器注册。
<br><br>


🛡️ **安全工位**  
<br>
所有文件操作、Shell 命令均限制在 workspace/office/ 目录内，自动拦截路径穿越攻击。

危险 Shell 命令（如 rm -rf /）正则匹配拦截，超时（60秒）自动熔断。




---
## 🚀 快速开始
1. 安装
```bash
git clone https://github.com/wangJie12138/ClearClaw.git
cd ClearClaw
pip install -e .
```

2. 初始化配置
```bash
clearclaw config
```

3. 构建知识库（可选）
```bash
# 将你的文档放入 workspace/knowledge/ 目录
clearclaw rag index
```

4. 启动
```bash
clearclaw run
```

5. 启动监控
```bash
clearclaw monitor
```

---

## 📚 使用指南

### 配置文件说明

**`.env` 文件**：主配置文件，包含 API Key、模型设置等敏感信息。

**`.env.example` 文件**：配置模板，包含所有可用配置项的说明和示例值。

首次使用时，复制示例文件并修改：
```bash
cp .env.example.env
```

## 🔬 测试

### 运行测试

```bash
# 运行所有测试
python3 -m pytest tests/ -v
python3 tests/test_two_phase_skills.py
python3 -c "from tests.test_two_phase_skills import run_tests; run_tests()"
```

## 📚 贡献指南

欢迎提交 Issue 和 Pull Request！

### 开发环境

```bash
# 克隆项目
git clone https://github.com/wangJie12138/ClearClaw.git
cd ClearClaw

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装开发依赖
pip install -e ".[dev]"
```

---

## 📄 许可证

MIT License

---

## ❤️ 致谢

- **[OpenClaw](https://github.com/openclaw/openclaw)** - 技能生态的灵感源泉
- **LangGraph** - 智能体状态流转与多角色编排的强力引擎
- **Prompt** - 打造丝滑的命令行交互体验
- **LangChain** - 大模型应用开发的稳固基石
- **Rich** - 让终端监控从枯燥变得直观绚丽


**同时衷心感谢所有贡献者，你们的每一次提交都在让 ClearClaw 变得更好。**

---

## 💬 联系方式

- **GitHub**: [@wangJie12138](https://github.com/wangJie12138)
- **邮箱**: 949842719@qq.com

---

<div align="center">
  <strong>🔍 ClearClaw · 透明 · 记忆 · 协同 · 可信</strong><br>
  <a href="https://github.com/wangJie12138">@wangJie12138</a>
</div>

---
