# -*- coding: utf-8 -*-
"""分析引擎 - 6步框架：学科优势→方向筛选→院校匹配→就业评估→96志愿→风险评估"""

import json
import os

# ============================================================
# Step 1: 学科优势分析
# ============================================================
def analyze_strengths(scores: dict) -> dict:
    """识别王牌科目(>=85)和软肋科目(<=70)"""
    if not scores:
        return {"strongest": None, "weakest": None, "king_card": None, "all_scores": {}}

    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    strongest = sorted_scores[0][0]
    weakest = sorted_scores[-1][0]
    king_card = strongest if scores[strongest] >= 85 else None

    return {
        "strongest": strongest,
        "weakest": weakest if scores[weakest] <= 70 else None,
        "king_card": king_card,
        "all_scores": scores,
    }


# ============================================================
# Step 2: 方向筛选
# ============================================================
DIRECTIONS = {
    "化工": {
        "key_subjects": {"化学": 85, "数学": 80, "物理": 70},
        "tags": ["化工", "应用化学", "化学工程", "制药工程"],
    },
    "材料": {
        "key_subjects": {"化学": 85, "物理": 80, "数学": 80},
        "tags": ["材料", "高分子", "复合材料", "金属材料", "无机非金属"],
    },
    "药学": {
        "key_subjects": {"化学": 85, "生物": 75},
        "tags": ["药学", "药物制剂", "生物制药", "制药"],
    },
    "食品": {
        "key_subjects": {"化学": 75, "生物": 70},
        "tags": ["食品", "酿酒", "发酵", "营养"],
    },
    "CS": {
        "key_subjects": {"数学": 85, "物理": 65},
        "tags": ["计算机", "软件", "数据科学", "人工智能", "网络工程", "电子信息"],
    },
    "211": {
        "key_subjects": {},
        "tags": [],
        "special": True,
    },
}


def match_directions(student: dict) -> list:
    """基于学科+性格+家庭+就业匹配方向，返回排序后的方向列表"""
    scores = student.get("academic", {}).get("scores", {})
    exclusions = student.get("career", {}).get("exclusions", [])
    results = []

    for dir_name, dir_info in DIRECTIONS.items():
        # 排除过滤
        skip = False
        for excl in exclusions:
            for tag in dir_info["tags"]:
                if excl in tag or tag in excl:
                    skip = True
                    break
            if skip:
                break
        if skip:
            continue

        # 211特殊处理
        if dir_info.get("special"):
            results.append({"direction": dir_name, "match_score": 70, "reason": "211文凭价值"})
            continue

        # 学科匹配计算
        key_subs = dir_info["key_subjects"]
        if not key_subs:
            continue

        total_weight = 0
        total_score = 0
        for subj, weight in key_subs.items():
            actual = scores.get(subj, 0)
            if actual == 0:
                total_score += 0
                total_weight += weight
            else:
                # 分数≥要求→满分；低于要求→按比例
                ratio = min(actual / weight, 1.5) if weight > 0 else 1.0
                total_score += ratio * weight
                total_weight += weight

        match_score = int((total_score / total_weight * 100) / 1.5) if total_weight > 0 else 0
        match_score = max(30, min(100, match_score))

        # 性格加成
        mbti = student.get("personality", {}).get("mbti", "")
        if "I" in mbti and "N" in mbti and dir_name in ["化工", "材料", "药学"]:
            match_score = min(100, match_score + 5)

        results.append({
            "direction": dir_name,
            "match_score": match_score,
            "reason": f"{','.join(k for k in key_subs if scores.get(k, 0) >= key_subs[k])}匹配",
        })

    results.sort(key=lambda x: x["match_score"], reverse=True)
    return results[:8]


# ============================================================
# Step 3: 院校匹配
# ============================================================
def calculate_tiers(rank: int) -> dict:
    """计算冲/稳/保位次区间"""
    return {
        "chong": (int(rank * 0.90), int(rank * 0.97)),
        "wen": (int(rank * 1.00), int(rank * 1.25)),
        "bao": (int(rank * 1.25), int(rank * 1.70)),
    }


def filter_schools(schools_data: list, student: dict, directions: list, tiers: dict) -> dict:
    """筛选院校，分冲/稳/保"""
    rank = student["basic"]["rank"]
    subjects = student["basic"].get("subjects", "")
    color_vision = student.get("health", {}).get("color_vision", "正常")
    budget_str = student.get("family", {}).get("tuition_budget", "不限")

    # 学费预算解析
    budget_map = {"5000元以内": 5000, "5000-8000元": 8000, "8000-15000元": 15000,
                  "15000-30000元": 30000, "不限": 999999}
    budget = budget_map.get(budget_str, 999999)

    result = {"chong": [], "wen": [], "bao": []}
    dir_names = [d["direction"] for d in directions]

    for school in schools_data:
        # 方向过滤
        if school.get("direction") not in dir_names and school.get("direction") != "211":
            continue

        # 位次过滤
        school_rank = school.get("rank_2025", 999999)
        if school_rank == 0:
            continue

        if tiers["chong"][0] <= school_rank <= tiers["chong"][1]:
            tier = "chong"
        elif tiers["wen"][0] <= school_rank <= tiers["wen"][1]:
            tier = "wen"
        elif tiers["bao"][0] <= school_rank <= tiers["bao"][1]:
            tier = "bao"
        else:
            continue

        # 色觉过滤
        if color_vision in ["色弱", "色盲"] and school.get("color_limit"):
            continue

        # 学费过滤
        if school.get("tuition", 5000) > budget:
            continue

        result[tier].append(school)

    return result


# ============================================================
# Step 5: 96志愿排序
# ============================================================
def generate_volunteers(filtered: dict, max_volunteers: int = 96) -> list:
    """合并冲稳保，生成志愿列表"""
    chong_ratio, wen_ratio, bao_ratio = 0.10, 0.58, 0.32
    chong_count = int(max_volunteers * chong_ratio)
    wen_count = int(max_volunteers * wen_ratio)
    bao_count = max_volunteers - chong_count - wen_count

    # 按位次排序（从高到低=冲→稳→保）
    chong_sorted = sorted(filtered["chong"], key=lambda x: x.get("rank_2025", 999999))
    wen_sorted = sorted(filtered["wen"], key=lambda x: x.get("rank_2025", 999999))
    bao_sorted = sorted(filtered["bao"], key=lambda x: x.get("rank_2025", 999999))

    volunteers = []
    for i, s in enumerate(chong_sorted[:chong_count], 1):
        volunteers.append({**s, "order": i, "tier": "冲"})
    for i, s in enumerate(wen_sorted[:wen_count], len(volunteers) + 1):
        volunteers.append({**s, "order": i, "tier": "稳"})
    for i, s in enumerate(bao_sorted[:bao_count], len(volunteers) + 1):
        volunteers.append({**s, "order": i, "tier": "保"})

    return volunteers


# ============================================================
# Step 6: 风险评估
# ============================================================
def assess_risks(volunteers: list, student: dict) -> dict:
    """评估滑档和退档风险"""
    rank = student["basic"]["rank"]
    color_vision = student.get("health", {}).get("color_vision", "正常")

    # 滑档风险
    bottom_rank = max((v.get("rank_2025", 0) for v in volunteers), default=0)
    slide_risk = "低" if bottom_rank > rank * 1.5 else "中"

    # 退档风险
    reject_risks = []
    if color_vision in ["色弱", "色盲"]:
        reject_risks.append("色觉异常可能导致退档")
    if color_vision in ["不确定/未检查"]:
        reject_risks.append("色觉未确认——建议立即检查")

    return {
        "slide_risk": slide_risk,
        "reject_risk": "中" if reject_risks else "低",
        "bottom_rank": bottom_rank,
        "reject_reasons": reject_risks,
        "checklist": [
            "色觉确认（去医院）",
            "地方专项资格确认",
            "招生章程核对",
            "全部96志愿勾选'专业服从调剂'",
            "保底位次>考生位次×1.5",
        ],
    }


# ============================================================
# 主分析函数
# ============================================================
def analyze(student: dict, schools_data: list, policy: dict = None) -> dict:
    """完整6步分析，输出analysis.json结构"""
    if policy is None:
        policy = {"max_volunteers": 96}

    scores = student.get("academic", {}).get("scores", {})
    rank = student.get("basic", {}).get("rank", 0)

    # Step 1
    strengths = analyze_strengths(scores)

    # Step 2
    directions = match_directions(student)

    # Step 3
    tiers = calculate_tiers(rank)
    filtered = filter_schools(schools_data, student, directions, tiers)

    # Step 5
    volunteers = generate_volunteers(filtered, policy.get("max_volunteers", 96))

    # Step 6
    risks = assess_risks(volunteers, student)

    return {
        "student_summary": {
            "name": student.get("basic", {}).get("name", ""),
            "king_card": strengths["king_card"],
            "weakness": strengths["weakest"],
            "rank": rank,
            "best_directions": [d["direction"] for d in directions[:4]],
        },
        "strengths": strengths,
        "directions": directions,
        "tiers": tiers,
        "filtered_schools": {
            "chong_count": len(filtered["chong"]),
            "wen_count": len(filtered["wen"]),
            "bao_count": len(filtered["bao"]),
        },
        "volunteers": volunteers,
        "risk_assessment": risks,
        "total_volunteers": len(volunteers),
    }


def save_analysis(analysis: dict, output_path: str):
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(analysis, f, ensure_ascii=False, indent=2)
    print(f"✅ 分析结果已保存: {output_path}")


if __name__ == "__main__":
    # 测试用例
    test_student = {
        "basic": {"name": "测试用户", "rank": 50000, "subjects": "物理+化学+生物"},
        "academic": {"scores": {"化学": 90, "数学": 92, "物理": 62, "英语": 118, "语文": 116, "生物": 78}},
        "personality": {"mbti": "INTJ", "holland_code": "IR"},
        "family": {"tuition_budget": "5000-8000元"},
        "career": {"exclusions": ["师范", "中外合作", "环境"]},
        "health": {"color_vision": "正常"},
    }
    test_schools = [
        {"name": "河北科技大学", "major": "化学工程与工艺", "rank_2025": 79754, "tuition": 5390, "direction": "化工"},
        {"name": "华北理工大学", "major": "材料类", "rank_2025": 54400, "tuition": 4900, "direction": "材料"},
    ]
    result = analyze(test_student, test_schools)
    print(json.dumps(result["student_summary"], ensure_ascii=False, indent=2))
