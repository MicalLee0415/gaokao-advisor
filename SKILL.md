# 高考志愿填报分析

帮助考生/家长完成专业级高考志愿填报分析，生成智库风格PDF报告。

## 何时使用

当用户提到以下内容时触发：
- 高考志愿 / 志愿填报 / 报志愿 / 选大学 / 选专业
- gaokao / college admission / 志愿分析 / 择校
- 分数线 / 投档线 / 位次 / 一分一段

## 工作流

### 完整分析流程（full-analysis）

1. **考生调研**：通过30+问题收集考生信息（学科/性格/家庭/就业/健康）
   - 对话问答模式：逐个提问
   - 网页表单模式：生成HTML让用户填写
   - 输出：student.json

2. **数据获取**：加载目标省份的投档数据
   - P0：使用内置数据包（CSV/JSON）
   - P1+：实时爬取阳光高考/各省考试院
   - 输出：data_{省份}_{年份}.json

3. **分析引擎**：基于6步框架分析
   - 学科优势分析 → 方向筛选 → 院校匹配 → 就业评估 → 96志愿排序 → 风险评估
   - 参考：references/methodology.md
   - 输出：analysis.json

4. **报告生成**：生成PDF/Excel/网页
   - PDF：智库风格（等线字体/深海蓝/莫兰迪色系）
   - 参考：references/report-style.md
   - 输出：交付到桌面

### 快速建议（quick-advice）

只需分数+位次+选科，快速给出方向建议和院校清单（不做深度调研）。

### 数据更新（data-refresh）

重新爬取/更新某省份的投档数据。

## 文件索引

| 文件 | 用途 |
|---|---|
| `scripts/survey.py` | 考生调研（30+问题收集） |
| `scripts/analyzer.py` | 核心分析引擎（6步框架） |
| `scripts/pdf_generator.py` | PDF报告生成 |
| `references/methodology.md` | 分析方法论（6步框架详解） |
| `references/major-database.md` | 专业方向库（就业/课程/门槛/企业） |
| `references/report-style.md` | 报告视觉规范 |
| `references/policy-templates/` | 各省高考政策模板 |
| `templates/report_template.html` | PDF报告HTML模板 |
| `templates/survey_form.html` | 网页调研表单模板 |
| `workflows/full-analysis.md` | 完整分析流程 |

## 注意事项

- 所有数据必须标注来源URL和采集日期（可追溯性）
- 色觉/体检限制是退档主因，调研时必须确认
- 冲稳保三档必须齐全，避免滑档
- 96个志愿全部建议勾选"专业服从调剂"
