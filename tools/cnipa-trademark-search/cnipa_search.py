#!/usr/bin/env python3
"""
CNIPA 商标精准检索工具 — 通过 Playwright 浏览器直接在 tm.aliyun.com
（阿里云商标频道，底层为 CNIPA 官方数据库）执行商标近似查询。

依赖：pip install playwright && playwright install chromium

用法：
  python cnipa_search.py AVELZORA                    # 单名查询
  python cnipa_search.py AVELZORA --class 3           # 指定类别过滤
  python cnipa_search.py AVELZORA --class 3 --class 35  # 多类别
  python cnipa_search.py --batch names.txt            # 批量查询
  python cnipa_search.py VESARIA --json               # JSON 输出

输出格式（--json）：
  {
    "query": "VESARIA",
    "total": 0,
    "class_filter": [3, 35],
    "results": [],
    "risk": "low"
  }

风险等级定义：
  low     — 无任何近似活标，可直接申请
  moderate— 有远距近似标（LD>=2），需代理评估
  high    — 有近距近似标（LD=1），不建议推进
  dead    — 完全同名活标已注册，不可注册
"""

import sys
import json
import time
import re
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("请先安装: pip install playwright && playwright install chromium")
    sys.exit(1)


def parse_trademark_row(row_text: str) -> dict | None:
    """从页面文本行解析商标信息"""
    # tm.aliyun.com 搜索结果格式:
    # 商标名称 注册号 类别 状态 申请人 申请日期 ...
    pattern = re.compile(
        r'(\d+)\s+'                # 序号
        r'([A-Za-z\u4e00-\u9fff·\s\d]+?)\s+'  # 商标名称
        r'(\d{6,})\s+'             # 注册号
        r'(\d{1,2}类)\s*'          # 类别
        r'([^\d]+?)\s+'            # 状态
        r'(\d{4}-\d{2}-\d{2})'     # 申请日期
    )
    m = pattern.search(row_text)
    if m:
        return {
            "name": m.group(2).strip(),
            "reg_number": m.group(3),
            "class_label": m.group(4),
            "status": m.group(5).strip(),
            "application_date": m.group(6),
        }
    return None


def search_trademark(page, name: str, class_filter: list[int] | None = None) -> dict:
    """在 tm.aliyun.com 搜索商标并提取结果"""
    # 构建搜索参数
    search_data = {
        "keyword": name,
        "searchType": "ALL",
        "pageNum": 1,
        "pageSize": 20,
        "classification": "",
        "product": "",
        "Status": "",
        "ApplyYear": "",
        "applyDateOrder": "",
        "firstAnncDateOrder": "",
        "regDateOrder": "",
        "orderId": "",
        "valid": False,
        "ifPrecise": False,
        "image": "",
    }

    q = json.dumps(search_data, ensure_ascii=True, separators=(",", ":"))
    url = f"https://tm.aliyun.com/channel/search#/search?q={q}"
    
    page.goto(url, wait_until="networkidle", timeout=30000)
    time.sleep(2)  # 等待 React 渲染

    # 提取页面文本
    content = page.content()
    text = page.inner_text("body")

    # 尝试解析搜索结果
    results = []
    total_count = 0

    # 提取总数
    total_match = re.search(r"共\s*(\d+)\s*个", text)
    if total_match:
        total_count = int(total_match.group(1))

    # 提取每条结果
    lines = text.split("\n")
    for line in lines:
        line = line.strip()
        if line and any(kw in line for kw in ["已注册", "已初审", "待审", "已驳回", "已无效", "等待审查"]):
            parsed = parse_trademark_row(line)
            if parsed:
                # 类别过滤
                if class_filter:
                    cls_num = int(re.search(r"(\d+)类", parsed["class_label"]).group(1))
                    if cls_num not in class_filter:
                        continue
                results.append(parsed)

    # 风险评估
    risk = "low"
    has_live_3 = False
    has_live_35 = False
    
    for r in results:
        if r["status"] in ["已注册", "已初审"]:
            cls_num = int(re.search(r"(\d+)类", r["class_label"]).group(1))
            
            # 同名检查
            if r["name"].upper().replace(" ", "") == name.upper().replace(" ", ""):
                risk = "dead"
                break
            
            # 近似检查
            dist = levenshtein_distance(
                name.upper().replace(" ", ""),
                r["name"].upper().replace(" ", "")
            )
            
            if dist == 1:
                if cls_num == 3:
                    has_live_3 = True
                if cls_num == 35:
                    has_live_35 = True

    if risk != "dead":
        if has_live_3 or has_live_35:
            risk = "high"
        elif results:
            risk = "moderate"

    return {
        "query": name,
        "total": total_count,
        "class_filter": class_filter,
        "results": results[:20],  # 最多返回 20 条
        "risk": risk,
    }


def levenshtein_distance(s1: str, s2: str) -> int:
    """计算两个字符串的编辑距离"""
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)
    
    prev = list(range(len(s2) + 1))
    for i, c1 in enumerate(s1):
        curr = [i + 1]
        for j, c2 in enumerate(s2):
            curr.append(min(
                prev[j + 1] + 1,
                curr[j] + 1,
                prev[j] + (0 if c1 == c2 else 1),
            ))
        prev = curr
    return prev[-1]


def batch_search(names: list[str], class_filter: list[int] | None = None,
                 headless: bool = True) -> list[dict]:
    """批量查询多个商标名"""
    results = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context(
            viewport={"width": 1280, "height": 800},
            locale="zh-CN",
        )
        page = context.new_page()

        try:
            for i, name in enumerate(names):
                print(f"[{i+1}/{len(names)}] 查询: {name}", file=sys.stderr)
                result = search_trademark(page, name, class_filter)
                results.append(result)
                # 输出进度
                risk_emoji = {"low": "🟢", "moderate": "🟡", "high": "🔴", "dead": "💀"}
                print(f"  → {risk_emoji.get(result['risk'], '?')} {result['risk'].upper()} "
                      f"({result['total']} 个结果)", file=sys.stderr)
        finally:
            browser.close()

    return results


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="CNIPA 商标精准检索工具（通过 tm.aliyun.com）"
    )
    parser.add_argument("query", nargs="?", help="单个商标名查询")
    parser.add_argument("--class", dest="classes", type=int, action="append",
                        help="过滤类别（可多次指定，如 --class 3 --class 35）")
    parser.add_argument("--batch", help="批量文件路径，每行一个商标名")
    parser.add_argument("--json", action="store_true", help="JSON 格式输出")
    parser.add_argument("--headed", action="store_true", help="显示浏览器窗口")
    parser.add_argument("--output", "-o", help="结果输出文件（JSON）")

    args = parser.parse_args()

    class_filter = args.classes if args.classes else [3, 35]

    if args.batch:
        names = [line.strip() for line in open(args.batch, encoding="utf-8")
                 if line.strip() and not line.strip().startswith("#")]
    elif args.query:
        names = [args.query]
    else:
        parser.print_help()
        sys.exit(1)

    results = batch_search(names, class_filter, headless=not args.headed)

    output = json.dumps(results, ensure_ascii=False, indent=2)

    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
        print(f"结果已保存至: {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
