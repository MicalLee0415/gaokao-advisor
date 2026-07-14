# -*- coding: utf-8 -*-
"""数据爬虫与加载器

功能：
1. parse_csv — 解析从各省考试院下载的CSV/Excel投档线数据
2. load_data_package — 加载内置JSON数据包
3. get_schools — 根据省份获取院校数据（内置包优先，可扩展为实时爬取）

数据格式（与analyzer.py对齐）：
{
    "name": "河北科技大学",
    "major": "化学工程与工艺",
    "rank_2025": 79754,
    "tuition": 5390,
    "direction": "化工",
    "color_limit": false,
    "note": ""
}

内置数据包路径：data/{province}_{year}.json
"""

import csv
import json
import os
import sys

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")

DIRECTION_KEYWORDS = {
    "化工": ["化学工程", "应用化学", "化学", "制药工程", "化工"],
    "材料": ["材料", "高分子", "复合材料", "金属材料", "无机非金属", "新能源材料"],
    "药学": ["药学", "药物制剂", "生物制药", "临床药学", "中药学"],
    "食品": ["食品", "酿酒", "发酵", "营养", "粮食"],
    "CS": ["计算机", "软件", "数据科学", "人工智能", "网络工程", "信息安全", "物联网"],
}


def detect_direction(major_name: str) -> str:
    """根据专业名称自动推断方向"""
    for direction, keywords in DIRECTION_KEYWORDS.items():
        for kw in keywords:
            if kw in major_name:
                return direction
    return "其他"


def parse_csv(csv_path: str, province: str = "", rank_column: str = "位次",
              school_column: str = "院校", major_column: str = "专业",
              tuition_column: str = "学费", has_header: bool = True) -> list:
    """解析从考试院下载的CSV投档线数据

    Args:
        csv_path: CSV文件路径
        province: 省份名（用于标记数据来源）
        rank_column: 位次列名（不同省考试院列名可能不同）
        school_column: 院校列名
        major_column: 专业列名
        tuition_column: 学费列名
        has_header: CSV是否有表头

    Returns:
        analyzer兼容的schools_data列表
    """
    schools = []
    try:
        with open(csv_path, "r", encoding="utf-8-sig") as f:
            if has_header:
                reader = csv.DictReader(f)
            else:
                reader = csv.reader(f)

            for row in reader:
                if has_header:
                    name = row.get(school_column, "").strip()
                    major = row.get(major_column, "").strip()
                    rank_str = row.get(rank_column, "0").strip()
                    tuition_str = row.get(tuition_column, "5000").strip()
                else:
                    if len(row) < 3:
                        continue
                    name = row[0].strip()
                    major = row[1].strip() if len(row) > 1 else ""
                    rank_str = row[2].strip() if len(row) > 2 else "0"
                    tuition_str = row[3].strip() if len(row) > 3 else "5000"

                if not name:
                    continue

                # 解析位次
                try:
                    rank = int(rank_str.replace(",", ""))
                except ValueError:
                    rank = 0

                # 解析学费
                try:
                    tuition = int(tuition_str.replace(",", "").replace("元", ""))
                except ValueError:
                    tuition = 5000

                direction = detect_direction(major)
                if direction == "其他":
                    # 211/985标记
                    if any(tag in name for tag in ["211", "985", "双一流"]):
                        direction = "211"
                    else:
                        continue  # 跳过无法分类的记录

                schools.append({
                    "name": name,
                    "major": major,
                    "rank_2025": rank,
                    "tuition": tuition,
                    "direction": direction,
                    "color_limit": False,
                    "note": "",
                })

    except FileNotFoundError:
        print(f"ERROR: CSV文件不存在: {csv_path}", file=sys.stderr)
        return []
    except Exception as e:
        print(f"ERROR: CSV解析失败: {e}", file=sys.stderr)
        return []

    print(f"Parsed {len(schools)} records from {csv_path}")
    return schools


def load_data_package(province: str, year: int = 2025) -> list:
    """加载内置JSON数据包

    Args:
        province: 省份名（如"河北"）
        year: 数据年份

    Returns:
        schools_data列表，空列表如果数据包不存在
    """
    filename = f"{province}_{year}.json"
    filepath = os.path.join(DATA_DIR, filename)

    if not os.path.exists(filepath):
        # 尝试无年份的文件名
        filepath = os.path.join(DATA_DIR, f"{province}.json")
        if not os.path.exists(filepath):
            print(f"WARN: 无内置数据包: {province} {year}（查找: {filename}）")
            return []

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            print(f"Loaded {len(data)} records from {filepath}")
            return data
        elif isinstance(data, dict) and "schools" in data:
            schools = data["schools"]
            print(f"Loaded {len(schools)} records from {filepath}")
            return schools
        else:
            print(f"WARN: 数据包格式异常: {filepath}", file=sys.stderr)
            return []
    except Exception as e:
        print(f"ERROR: 加载数据包失败: {e}", file=sys.stderr)
        return []


def get_schools(province: str, year: int = 2025, csv_path: str = None) -> list:
    """获取院校数据（统一入口）

    优先级：
    1. 如果提供了csv_path，解析CSV
    2. 否则加载内置数据包
    3. 都没有则返回空列表

    Args:
        province: 省份名
        year: 数据年份
        csv_path: 可选的CSV文件路径（用户手动下载的投档线数据）

    Returns:
        schools_data列表
    """
    if csv_path:
        schools = parse_csv(csv_path, province)
        if schools:
            return schools

    return load_data_package(province, year)


def list_available_packages() -> list:
    """列出所有可用的内置数据包"""
    if not os.path.exists(DATA_DIR):
        return []

    packages = []
    for f in os.listdir(DATA_DIR):
        if f.endswith(".json"):
            filepath = os.path.join(DATA_DIR, f)
            size = os.path.getsize(filepath)
            # 读取记录数
            try:
                with open(filepath, "r", encoding="utf-8") as fh:
                    data = json.load(fh)
                count = len(data) if isinstance(data, list) else len(data.get("schools", []))
            except Exception:
                count = 0
            packages.append({"file": f, "records": count, "size": size})

    return packages


def save_to_package(schools: list, province: str, year: int = 2025):
    """将院校数据保存为内置数据包格式"""
    os.makedirs(DATA_DIR, exist_ok=True)
    filepath = os.path.join(DATA_DIR, f"{province}_{year}.json")
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(schools, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(schools)} records to {filepath}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="高考数据爬虫与加载器")
    sub = parser.add_subparsers(dest="command")

    # list
    sub_list = sub.add_parser("list", help="列出可用数据包")

    # parse
    sub_parse = sub.add_parser("parse", help="解析CSV文件")
    sub_parse.add_argument("csv", help="CSV文件路径")
    sub_parse.add_argument("-p", "--province", default="", help="省份")
    sub_parse.add_argument("-o", "--output", help="输出JSON路径")

    # load
    sub_load = sub.add_parser("load", help="加载内置数据包")
    sub_load.add_argument("province", help="省份（如：河北）")
    sub_load.add_argument("-y", "--year", type=int, default=2025, help="年份")

    args = parser.parse_args()

    if args.command == "list":
        packages = list_available_packages()
        if packages:
            print(f"可用数据包（{len(packages)}个）:")
            for p in packages:
                print(f"  {p['file']}: {p['records']}条记录, {p['size']:,} bytes")
        else:
            print("无可用数据包。使用 'parse' 命令从CSV导入。")

    elif args.command == "parse":
        schools = parse_csv(args.csv, args.province)
        if args.output:
            save_to_package(schools, args.province or "unknown")
        else:
            print(json.dumps(schools[:5], ensure_ascii=False, indent=2))
            print(f"... 共{len(schools)}条")

    elif args.command == "load":
        schools = load_data_package(args.province, args.year)
        if schools:
            print(json.dumps(schools[:3], ensure_ascii=False, indent=2))
            print(f"... 共{len(schools)}条")
        else:
            print(f"无数据包: {args.province} {args.year}")
    else:
        parser.print_help()
