# -*- coding: utf-8 -*-
"""PDF报告生成器 - analysis.json → HTML → PDF（Playwright）"""

import json
import os
import subprocess
from datetime import datetime


def load_analysis(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def render_html(analysis: dict) -> str:
    """将analysis.json渲染为智库风格HTML"""
    s = analysis["student_summary"]
    strengths = analysis.get("strengths", {})
    directions = analysis.get("directions", [])
    volunteers = analysis.get("volunteers", [])
    risks = analysis.get("risk_assessment", {})
    scores = strengths.get("all_scores", {})

    # 封面
    score_items = " · ".join(f"{k} {v}" for k, v in scores.items()) if scores else ""
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>高考志愿专业评估分析报告</title>
<style>
@page {{ size: A4; margin: 22mm 13mm 22mm 13mm; }}
@page :first {{ margin: 0; }}
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ font-family:"DengXian","等线","Microsoft YaHei",sans-serif; font-size:12.5px; line-height:1.6; color:#1a1a1a; background:#FFFFFF; font-weight:400; }}
.cover {{ background:#FFFFFF; padding:55mm 25mm 30mm 25mm; text-align:left; }}
.cover-tag {{ font-size:9px; color:#888; letter-spacing:6px; margin-bottom:30px; }}
.cover h1 {{ font-size:36px; margin-bottom:18px; color:#1E3A5F; font-weight:700; letter-spacing:3px; }}
.cover-line {{ width:100%; height:1px; background:#1E3A5F; margin:24px 0; }}
.cover .sub {{ font-size:12px; color:#888; margin-bottom:8px; }}
.cover .meta {{ font-size:10px; color:#888; margin-top:6px; }}
.cover-confidential {{ font-size:8px; color:#6E2C2C; text-align:right; margin-top:40px; }}
h1.ch {{ font-size:20px; color:#0D1A2E; border-bottom:2px solid #1E3A5F; padding-bottom:6px; margin:24px 0 14px; font-weight:700; }}
h2 {{ font-size:15px; color:#0D1A2E; margin:18px 0 8px; font-weight:700; }}
h3 {{ font-size:13px; color:#1E3A5F; margin:14px 0 6px; font-weight:700; }}
p {{ margin:5px 0; color:#1a1a1a; }}
table {{ width:100%; border-collapse:collapse; margin:8px 0; font-size:10.5px; }}
th {{ background:#1E3A5F; color:#FFFFFF; padding:8px 6px; text-align:center; border:1px solid #1E3A5F; font-weight:700; }}
td {{ padding:7px 5px; border:1px solid #AAAAAA; text-align:center; color:#1a1a1a; }}
tr:nth-child(even) {{ background:#F2F2F2; }}
tr:nth-child(odd) {{ background:#FFFFFF; }}
td.l {{ text-align:left; }}
.pb {{ page-break-before:always; }}
.callout {{ background:#F8F6F0; border-left:3px solid #1E3A5F; padding:10px 14px; margin:10px 0; color:#1a1a1a; }}
.danger {{ background:#F8F6F0; border-left:3px solid #6E2C2C; padding:10px 14px; margin:10px 0; color:#1a1a1a; }}
.warn {{ background:#F8F6F0; border-left:3px solid #C87A4A; padding:10px 14px; margin:10px 0; color:#1a1a1a; }}
</style>
</head>
<body>
<div class="cover">
<div class="cover-tag">PROFESSIONAL EVALUATION REPORT</div>
<h1>高考志愿<br/>专业评估分析报告</h1>
<div class="cover-line"></div>
<div class="sub">{s.get('name','考生')}　|　{scores.get('总分','')}分　|　位次{s.get('rank','')}</div>
<div class="meta">报告版本：v1.0　|　{datetime.now().strftime('%Y年%m月')}</div>
<div class="cover-line" style="height:0.5px;background:#CCCCCC;"></div>
<div class="sub" style="font-size:9px;">学科成绩：{score_items}</div>
<div class="cover-confidential">内部资料 · 请勿外传</div>
</div>

<h1 class="ch">一、学科优势分析</h1>
<table>
<tr><th style="width:20%;">项目</th><th>分析结果</th></tr>
<tr><td><b>王牌科目</b></td><td class="l">{strengths.get('king_card') or '无显著王牌'}</td></tr>
<tr><td><b>软肋科目</b></td><td class="l">{strengths.get('weakest') or '无明显软肋'}</td></tr>
<tr><td><b>推荐方向</b></td><td class="l">{'、'.join(s.get('best_directions',[]))}</td></tr>
</table>

<h1 class="ch pb">二、推荐方向与匹配度</h1>
<table>
<tr><th>方向</th><th>匹配度</th><th>推荐理由</th></tr>
"""
    for d in directions:
        html += f'<tr><td><b>{d["direction"]}</b></td><td>{d["match_score"]}%</td><td class="l">{d["reason"]}</td></tr>\n'

    html += "</table>\n"

    # 志愿清单
    if volunteers:
        html += '<h1 class="ch pb">三、志愿填报参考列表</h1>\n'
        html += '<table>\n<tr><th style="width:5%;">序号</th><th style="width:22%;">院校</th><th style="width:24%;">专业</th><th style="width:8%;">冲稳保</th><th>备注</th></tr>\n'

        current_tier = None
        tier_names = {"冲": "冲档", "稳": "稳档", "保": "保档"}
        for v in volunteers:
            tier = v.get("tier", "")
            if tier != current_tier:
                current_tier = tier
                html += f'<tr><td colspan="5" style="background:#1E3A5F;color:#fff;font-weight:700;text-align:center;">━━ {tier_names.get(tier,tier)} ━━</td></tr>\n'
            html += f'<tr><td>{v.get("order","")}</td><td><b>{v.get("name","")}</b></td><td class="l">{v.get("major","")}</td><td>{tier}</td><td class="l">{v.get("note","")}</td></tr>\n'
        html += "</table>\n"

    # 风险评估
    html += '<h1 class="ch pb">四、风险评估与防范</h1>\n'
    html += f'<div class="danger"><b>滑档风险：{risks.get("slide_risk","未评估")}</b>　保底位次：{risks.get("bottom_rank","未知")}</div>\n'
    html += f'<div class="warn"><b>退档风险：{risks.get("reject_risk","未评估")}</b>'
    if risks.get("reject_reasons"):
        html += "<br>" + "<br>".join(f"⚠ {r}" for r in risks["reject_reasons"])
    html += '</div>\n'

    if risks.get("checklist"):
        html += '<h2>填报前紧急确认清单</h2><table>\n'
        for i, item in enumerate(risks["checklist"], 1):
            html += f'<tr><td style="width:10%;">{i}</td><td class="l">{item}</td></tr>\n'
        html += "</table>\n"

    html += f"""
<div style="text-align:center;margin-top:14px;padding:8px;border-top:1px solid #1E3A5F;">
<p style="font-size:9px;color:#888;">v1.0·高考志愿专业评估分析报告·{datetime.now().strftime('%Y-%m-%d')}</p>
</div>
</body></html>"""

    return html


def generate_pdf(analysis_path: str, output_pdf: str, html_path: str = None):
    """从analysis.json生成PDF"""
    if html_path is None:
        html_path = os.path.join(os.path.dirname(output_pdf), "temp_report.html")

    analysis = load_analysis(analysis_path)
    html = render_html(analysis)

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"HTML generated: {len(html):,} chars")

    # Playwright生成PDF
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(f"file:///{html_path.replace(os.sep, '/')}", wait_until="networkidle")
        page.evaluate("document.fonts.ready")
        page.pdf(
            path=output_pdf,
            format="A4",
            margin={"top": "22mm", "bottom": "22mm", "left": "13mm", "right": "13mm"},
            print_background=True,
        )
        browser.close()

    size = os.path.getsize(output_pdf)
    print(f"PDF generated: {size:,} bytes ({size/1024/1024:.2f} MB)")


if __name__ == "__main__":
    import sys
    if len(sys.argv) >= 3:
        generate_pdf(sys.argv[1], sys.argv[2])
    else:
        print("Usage: python pdf_generator.py <analysis.json> <output.pdf>")
