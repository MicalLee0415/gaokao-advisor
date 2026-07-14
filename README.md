# Gaokao Advisor - 高考志愿填报分析系统

从 OpenCode Skill 起步，逐步发展为面向所有考生/家长的志愿填报分析平台。

## 当前形态：OpenCode Skill（v1.0 已完成）

帮助考生/家长完成专业级高考志愿填报分析的 OpenCode Skill，也可通过网页表单和命令行直接使用。

### 核心功能

- **30+问题深度调研**：学科能力 / MBTI性格 / 霍兰德职业兴趣 / 家庭环境 / 就业意向 / 健康限制
- **6步分析引擎**：学科优势分析 → 方向筛选 → 院校匹配 → 就业评估 → 志愿排序 → 风险评估
- **智库风格PDF报告**：31页专业报告，国家级智库视觉规范
- **Excel志愿表**：3个Sheet（志愿清单/学生画像/风险评估），可直接编辑
- **交互式报告查看器**：浏览器加载analysis.json，动态渲染报告
- **网页调研表单**：30+问题可视化填写，提交即生成student.json
- **全国31省政策模板**：覆盖3+3/3+1+2/传统高考三种模式
- **4省内置数据包**：河北(57条)/山东(33条)/广东(29条)/河南(29条)
- **数据爬虫框架**：支持从考试院CSV导入数据，按省份自动加载
- **滑档退档防范**：冲稳保三档 + 风险评估 + 填报前确认清单

### 安装与使用

```bash
# 安装为 OpenCode Skill
cp -r gaokao-advisor ~/.config/opencode/skills/

# 或直接运行脚本
# 1. 考生调研（对话问答 或 网页表单）
python scripts/survey.py
# 浏览器打开 templates/survey_form.html

# 2. 分析引擎（自动加载内置数据包）
python scripts/analyzer.py

# 3. 生成报告
python scripts/pdf_generator.py analysis.json report.pdf
python scripts/excel_generator.py analysis.json report.xlsx

# 4. 浏览器预览报告
# 打开 templates/report_template.html，加载 analysis.json

# 数据管理
python scripts/data_scraper.py list          # 列出可用数据包
python scripts/data_scraper.py parse csv.csv # 从CSV导入
```

### 目录结构

```
gaokao-advisor/
├── SKILL.md                        # 入口：触发条件 + 工作流路由
├── scripts/
│   ├── survey.py                   # 30+问题调研 → student.json
│   ├── analyzer.py                 # 6步分析引擎（支持数据包自动加载）
│   ├── pdf_generator.py            # PDF报告生成（Playwright）
│   ├── excel_generator.py          # Excel志愿表生成（openpyxl，3个Sheet）
│   ├── data_scraper.py             # 数据爬虫与加载器（CSV解析+内置数据包）
│   └── gen_data_packages.py        # 数据包生成器
├── data/                           # 内置院校数据包
│   ├── 河北_2025.json              # 57条记录
│   ├── 山东_2025.json              # 33条记录
│   ├── 广东_2025.json              # 29条记录
│   └── 河南_2025.json              # 29条记录
├── references/
│   ├── methodology.md              # 分析方法论（6步框架）
│   ├── major-database.md           # 专业方向库（就业/课程/门槛/企业）
│   ├── report-style.md             # 报告视觉规范
│   └── policy-templates/           # 全国31省政策模板
│       ├── hebei.md
│       ├── 北京.md ... 西藏.md
│       └── ...
├── templates/
│   ├── survey_form.html            # 网页调研表单
│   └── report_template.html        # 交互式报告查看器
└── workflows/
    └── full-analysis.md            # 完整分析流程
```

### 分析框架

**6步分析**：学科优势 → 方向筛选 → 院校匹配 → 就业评估 → 志愿排序 → 风险评估

| 冲稳保档位 | 位次区间 |
|---|---|
| 冲档 | 考生位次 × 0.90 ~ × 0.97 |
| 稳档 | 考生位次 × 1.00 ~ × 1.25 |
| 保档 | 考生位次 × 1.25 ~ × 1.70 |

### 依赖

- Python 3.10+
- Playwright（PDF生成）：`pip install playwright && playwright install chromium`
- openpyxl（Excel输出）：`pip install openpyxl`

---

## 路线图

### v1.0 — OpenCode Skill（✅ 已完成）

| 阶段 | 内容 | 状态 |
|---|---|---|
| P0 | 核心Skill（调研+分析+PDF） | ✅ |
| P1 | 数据爬虫（4省）+ 内置数据包 | ✅ |
| P2 | 网页表单 + Excel输出 + 交互式网页 | ✅ |
| P3 | 全国31省政策模板 | ✅ |

### v2.0 — Web App（规划中）

目标：从需要安装的Skill变成浏览器直接使用的网站，降低使用门槛。

| 阶段 | 内容 | 状态 |
|---|---|---|
| W1 | Next.js前端 + FastAPI后端 | 📋 |
| W2 | 在线调研表单 + 实时分析 + 报告下载 | 📋 |
| W3 | 用户账号系统（学生/家长共享） | 📋 |
| W4 | 移动端适配（响应式设计） | 📋 |

### v3.0 — 数据准确度提升（规划中）

目标：从样本数据升级为真实、精准、实时的高考数据。

| 阶段 | 内容 | 状态 |
|---|---|---|
| D1 | 实时数据采集 — 各省考试院投档线自动抓取 | 📋 |
| D2 | 历史3-5年数据 — 趋势分析 + 波动预警 | 📋 |
| D3 | 地区差异校准 — 各省位次换算模型（非简单乘数） | 📋 |
| D4 | 政策精准获取 — 加分/专项/限报规则结构化入库 | 📋 |
| D5 | 院校招生计划实时同步 — 计划数变动影响分析 | 📋 |

### v4.0 — 移动端（规划中）

目标：让家长在手机上也能轻松使用。

| 阶段 | 内容 | 状态 |
|---|---|---|
| M1 | 微信小程序 — 调研+报告查看 | 📋 |
| M2 | 政策推送通知 — 分数线/填报截止提醒 | 📋 |
| M3 | 老师/咨询师模式 — 批量处理多个考生 | 📋 |

### v5.0 — 职业生涯规划（规划中）

目标：从"填志愿"延伸到"规划大学和职业"，陪伴考生更长生命周期。

| 阶段 | 内容 | 状态 |
|---|---|---|
| C1 | 学科课程图谱 — 各专业大学4年学什么、难度如何 | 📋 |
| C2 | 学习路径规划 — 大一到大四每学期重点、考证时间线 | 📋 |
| C3 | 职业路线图 — 各专业毕业去向（考研/就业/考公/留学）+ 真实薪资 | 📋 |
| C4 | 行业趋势分析 — 3-5年行业前景、AI替代风险评估 | 📋 |
| C5 | 院校对比 — 同档次院校的就业率/考研率/留学率横向对比 | 📋 |
| C6 | 社区 — 用户分享就读体验、就业真实情况 | 📋 |

---

## License

MIT

## 免责声明

本工具提供的分析建议仅供参考，不构成最终填报决策。请以各省教育考试院公布的官方数据为准，并结合考生实际情况和招生章程做出最终判断。
