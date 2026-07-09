# -*- coding: utf-8 -*-
"""考生调研模块 - 30+问题收集考生信息，输出student.json"""

import json
import os

PROVINCES = [
    "河北", "山东", "江苏", "浙江", "湖南", "湖北", "广东", "福建", "重庆",
    "辽宁", "安徽", "江西", "河南", "四川", "云南", "贵州", "陕西", "山西",
    "黑龙江", "吉林", "甘肃", "广西", "海南", "内蒙古", "新疆", "西藏",
    "青海", "宁夏", "北京", "天津", "上海"
]

SUBJECTS_3_1_2 = {
    "preferred": ["物理", "历史"],
    "reselect": ["化学", "生物", "地理", "政治"]
}

# ============================================================
# 30+问题定义
# ============================================================
SURVEY_QUESTIONS = [
    # === 基本信息 (6题) ===
    {"id": "name", "dim": "basic", "q": "考生姓名？", "type": "text", "required": True},
    {"id": "gender", "dim": "basic", "q": "性别？", "type": "choice", "options": ["男", "女"], "required": True},
    {"id": "province", "dim": "basic", "q": "所在省份？", "type": "choice", "options": PROVINCES, "required": True},
    {"id": "score", "dim": "basic", "q": "高考总分？", "type": "number", "required": True},
    {"id": "rank", "dim": "basic", "q": "全省位次（排名）？", "type": "number", "required": True},
    {"id": "subjects", "dim": "basic", "q": "选科组合是什么？", "type": "text", "required": True,
     "hint": "如：物理+化学+生物"},

    # === 学科能力 (6题) ===
    {"id": "score_chinese", "dim": "academic", "q": "语文分数？", "type": "number", "required": True},
    {"id": "score_math", "dim": "academic", "q": "数学分数？", "type": "number", "required": True},
    {"id": "score_english", "dim": "academic", "q": "英语分数？", "type": "number", "required": True},
    {"id": "score_physics", "dim": "academic", "q": "物理分数？（如选物理）", "type": "number", "required": False},
    {"id": "score_chemistry", "dim": "academic", "q": "化学分数？（如选化学）", "type": "number", "required": False},
    {"id": "score_biology", "dim": "academic", "q": "生物分数？（如选生物）", "type": "number", "required": False},

    # === 性格职业倾向 (6题) - MBTI简化版 + 霍兰德 ===
    {"id": "mbti_energy", "dim": "personality", "q": "课间休息时你更喜欢？", "type": "choice",
     "options": ["和同学聊天(E)", "自己看书/思考(I)"], "required": True},
    {"id": "mbti_info", "dim": "personality", "q": "你更感兴趣的是？", "type": "choice",
     "options": ["具体事实和细节(S)", "可能性和想法(N)"], "required": True},
    {"id": "mbti_decision", "dim": "personality", "q": "做决定时你更看重？", "type": "choice",
     "options": ["逻辑和分析(T)", "情感和人际关系(F)"], "required": True},
    {"id": "mbti_lifestyle", "dim": "personality", "q": "你更喜欢？", "type": "choice",
     "options": ["提前计划按部就班(J)", "灵活应变保持开放(P)"], "required": True},
    {"id": "holland_activity", "dim": "personality", "q": "以下活动你最喜欢哪个？", "type": "choice",
     "options": ["做实验/研究(R)", "设计/创作(A)", "组织/管理(E)", "帮助/服务(S)"], "required": True},
    {"id": "holland_env", "dim": "personality", "q": "你喜欢的工作环境是？", "type": "choice",
     "options": ["实验室/研究所(I)", "户外/动手操作(R)", "办公室/数据分析(C)", "与人打交道(S)"], "required": True},

    # === 家庭环境 (5题) ===
    {"id": "family_income", "dim": "family", "q": "家庭年收入大约？", "type": "choice",
     "options": ["10万以下", "10-20万", "20-50万", "50万以上"], "required": True},
    {"id": "parent_education", "dim": "family", "q": "父母最高学历？", "type": "choice",
     "options": ["初中及以下", "高中/中专", "大专/本科", "硕士及以上"], "required": True},
    {"id": "first_gen", "dim": "family", "q": "是否家族第一代大学生？", "type": "choice",
     "options": ["是", "否"], "required": True},
    {"id": "location_pref", "dim": "family", "q": "地域偏好（可多选，用逗号分隔）？", "type": "text",
     "required": True, "hint": "如：天津,济南,杭州"},
    {"id": "tuition_budget", "dim": "family", "q": "学费预算上限（每年）？", "type": "choice",
     "options": ["5000元以内", "5000-8000元", "8000-15000元", "15000-30000元", "不限"], "required": True},

    # === 就业意向 (5题) ===
    {"id": "grad_plan", "dim": "career", "q": "本科毕业后打算？", "type": "choice",
     "options": ["一定要考研", "可能考研", "直接就业", "考公务员", "还没想好"], "required": True},
    {"id": "company_type", "dim": "career", "q": "最想去的单位类型？", "type": "choice",
     "options": ["国企/央企", "民营/互联网", "外企", "公务员/事业编", "自己创业"], "required": True},
    {"id": "industry_pref", "dim": "career", "q": "感兴趣的行业（可多选）？", "type": "text",
     "required": False, "hint": "如：化工,新能源,医药,计算机,食品"},
    {"id": "salary_expect", "dim": "career", "q": "毕业后5年期望年薪？", "type": "choice",
     "options": ["10万以下", "10-20万", "20-30万", "30-50万", "50万以上"], "required": True},
    {"id": "exclusions", "dim": "career", "q": "明确不想学的专业方向（可多选）？", "type": "text",
     "required": False, "hint": "如：师范,中外合作,环境工程,土木"},

    # === 健康与限制 (4题) ===
    {"id": "color_vision", "dim": "health", "q": "色觉情况？（非常重要，影响退档）", "type": "choice",
     "options": ["正常", "色弱", "色盲", "不确定/未检查"], "required": True},
    {"id": "vision", "dim": "health", "q": "裸眼视力（左右眼平均）？", "type": "choice",
     "options": ["5.0以上", "4.8-5.0", "4.5-4.8", "4.5以下"], "required": True},
    {"id": "height", "dim": "health", "q": "身高（cm）？", "type": "number", "required": False},
    {"id": "other_health", "dim": "health", "q": "是否有其他体检异常？（如无则留空）", "type": "text",
     "required": False, "hint": "如：无"},
]


def run_dialogue_survey():
    """对话问答模式：逐个提问，返回answers字典"""
    answers = {}
    print("=" * 50)
    print("高考志愿填报调研（共30+问题）")
    print("请逐一回答，输入后按回车确认。")
    print("=" * 50)

    current_dim = None
    for i, question in enumerate(SURVEY_QUESTIONS, 1):
        # 维度切换提示
        dim_names = {
            "basic": "基本信息", "academic": "学科能力",
            "personality": "性格职业倾向", "family": "家庭环境",
            "career": "就业意向", "health": "健康与限制"
        }
        if question["dim"] != current_dim:
            current_dim = question["dim"]
            print(f"\n--- {dim_names.get(current_dim, current_dim)} ---")

        # 构建提示
        required_tag = " *" if question.get("required") else ""
        hint = f"（{question['hint']}）" if question.get("hint") else ""
        prompt = f"[{i}/{len(SURVEY_QUESTIONS)}] {question['q']}{hint}{required_tag}: "

        if question["type"] == "choice":
            options_str = " / ".join(question["options"])
            prompt += f"\n  选项: {options_str}\n  > "

        while True:
            raw = input(prompt).strip()
            if not raw and not question.get("required"):
                break
            if not raw and question.get("required"):
                print("  ⚠ 此题为必答，请输入答案。")
                continue
            if question["type"] == "number":
                try:
                    answers[question["id"]] = float(raw) if "." in raw else int(raw)
                except ValueError:
                    print("  ⚠ 请输入数字。")
                    continue
            else:
                answers[question["id"]] = raw
            break

    return answers


def organize_answers(answers: dict) -> dict:
    """将flat answers整理为结构化student profile"""
    # MBTI
    mbti = ""
    mbti_map = {
        "mbti_energy": "E", "mbti_info": "N", "mbti_decision": "T", "mbti_lifestyle": "J"
    }
    for key, default in mbti_map.items():
        val = answers.get(key, "")
        if val:
            letter = val[-2] if len(val) > 1 else default
            mbti += letter

    # Holland code
    holland = ""
    for key in ["holland_activity", "holland_env"]:
        val = answers.get(key, "")
        if val and "(" in val:
            holland += val[val.index("(") + 1]

    # 学科分数
    scores = {}
    for subj_key, subj_name in [("score_chinese", "语文"), ("score_math", "数学"),
                                  ("score_english", "英语"), ("score_physics", "物理"),
                                  ("score_chemistry", "化学"), ("score_biology", "生物")]:
        if answers.get(subj_key) is not None:
            scores[subj_name] = answers[subj_key]

    # 排除项
    exclusions = []
    if answers.get("exclusions"):
        exclusions = [e.strip() for e in answers["exclusions"].replace("，", ",").split(",") if e.strip()]

    # 地域偏好
    loc_pref = []
    if answers.get("location_pref"):
        loc_pref = [l.strip() for l in answers["location_pref"].replace("，", ",").split(",") if l.strip()]

    return {
        "basic": {
            "name": answers.get("name", ""),
            "gender": answers.get("gender", ""),
            "province": answers.get("province", ""),
            "score": answers.get("score", 0),
            "rank": answers.get("rank", 0),
            "subjects": answers.get("subjects", ""),
        },
        "academic": {
            "scores": scores,
        },
        "personality": {
            "mbti": mbti,
            "holland_code": holland,
            "raw": {k: v for k, v in answers.items() if k.startswith("mbti_") or k.startswith("holland_")},
        },
        "family": {
            "income": answers.get("family_income", ""),
            "parent_education": answers.get("parent_education", ""),
            "first_gen": answers.get("first_gen", ""),
            "location_preference": loc_pref,
            "tuition_budget": answers.get("tuition_budget", ""),
        },
        "career": {
            "grad_plan": answers.get("grad_plan", ""),
            "company_type": answers.get("company_type", ""),
            "industry_preference": answers.get("industry_pref", ""),
            "salary_expectation": answers.get("salary_expect", ""),
            "exclusions": exclusions,
        },
        "health": {
            "color_vision": answers.get("color_vision", ""),
            "vision": answers.get("vision", ""),
            "height": answers.get("height", ""),
            "other": answers.get("other_health", ""),
        },
    }


def save_student_profile(profile: dict, output_path: str):
    """保存为student.json"""
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(profile, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 考生档案已保存: {output_path}")


def load_student_profile(path: str) -> dict:
    """加载student.json"""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# ============================================================
# AI Agent调用入口（非交互式，直接传answers dict）
# ============================================================
def create_profile_from_answers(answers: dict, output_path: str = "student.json") -> dict:
    """从AI对话收集的答案直接创建profile，不需要终端交互"""
    profile = organize_answers(answers)
    save_student_profile(profile, output_path)
    return profile


if __name__ == "__main__":
    answers = run_dialogue_survey()
    profile = organize_answers(answers)
    save_student_profile(profile, "student.json")
