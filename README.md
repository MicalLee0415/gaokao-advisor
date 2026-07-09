# Gaokao Advisor - 高考志愿填报分析 Skill

帮助考生/家长完成专业级高考志愿填报分析的 OpenCode Skill。

## 功能

- **30+问题深度调研**：学科能力 / MBTI性格 / 霍兰德职业兴趣 / 家庭环境 / 就业意向 / 健康限制
- **6步分析引擎**：学科优势分析 → 方向筛选 → 院校匹配 → 就业评估 → 志愿排序 → 风险评估
- **智库风格PDF报告**：国家级智库/顶级咨询公司视觉规范
- **6大专业方向库**：化工 / 材料 / 药学 / 食品 / CS / 211大学（含就业赛道/薪资/企业/门槛）
- **滑档退档防范**：冲稳保三档 + 风险评估 + 填报前确认清单

## 安装

将本目录复制到 OpenCode skills 目录：

```bash
cp -r gaokao-advisor ~/.config/opencode/skills/
```

## 使用

在 OpenCode 中说：

> "高考志愿填报分析"

或直接运行脚本：

```bash
# 1. 考生调研（对话问答）
python scripts/survey.py

# 2. 分析引擎
python scripts/analyzer.py

# 3. 生成PDF
python scripts/pdf_generator.py analysis.json report.pdf
```

## 目录结构

```
gaokao-advisor/
├── SKILL.md                        # 入口：触发条件 + 工作流路由
├── scripts/
│   ├── survey.py                   # 30+问题调研 → student.json
│   ├── analyzer.py                 # 6步分析引擎 → analysis.json
│   └── pdf_generator.py            # PDF报告生成（Playwright）
├── references/
│   ├── methodology.md              # 分析方法论（6步框架）
│   ├── major-database.md           # 专业方向库（就业/课程/门槛/企业）
│   ├── report-style.md             # 报告视觉规范
│   └── policy-templates/
│       └── hebei.md                # 河北省高考政策
├── templates/                      # 报告模板（P2）
└── workflows/
    └── full-analysis.md            # 完整分析流程
```

## 分析框架

### 6步分析

1. **学科优势分析** — 识别王牌科目(≥85分)和软肋(≤70分)
2. **方向筛选** — 学科+性格+家庭+就业 → 推荐6-8个方向
3. **院校匹配** — 冲/稳/保三档（位次×0.90~1.70）
4. **就业评估** — 每方向附完整就业数据
5. **志愿排序** — 冲10/稳56/保30
6. **风险评估** — 滑档/退档防范

### 冲稳保计算

| 档位 | 位次区间 |
|---|---|
| 冲档 | 考生位次 × 0.90 ~ × 0.97 |
| 稳档 | 考生位次 × 1.00 ~ × 1.25 |
| 保档 | 考生位次 × 1.25 ~ × 1.70 |

## 报告样式

国家级智库/顶级咨询公司风格：

- 配色：纯白底 + 深海蓝(#1E3A5F) + 勃艮第红(#6E2C2C) + 莫兰迪色系
- 字体：等线(DengXian) 12.5px
- 原则："内容为王，留白为骨"

## 依赖

- Python 3.10+
- Playwright（PDF生成）
- openpyxl（Excel输出，P2）

```bash
pip install playwright
playwright install chromium
```

## 路线图

| 阶段 | 内容 | 状态 |
|---|---|---|
| P0 | 核心Skill（调研+分析+PDF） | ✅ 完成 |
| P1 | 数据爬虫（4省）+ 内置数据包 | 📋 计划中 |
| P2 | 网页表单 + Excel输出 + 交互式网页 | 📋 计划中 |
| P3 | 全国31省 + 政策模板扩展 | 📋 计划中 |

## License

MIT

## 免责声明

本工具提供的分析建议仅供参考，不构成最终填报决策。请以各省教育考试院公布的官方数据为准，并结合考生实际情况和招生章程做出最终判断。
