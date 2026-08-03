# CNIPA 商标精准检索工具

> 📤 本工具由 **WorkBuddy 电脑端** 创建并上传至 GitHub · 2026年8月3日

## 它干了什么

通过 Playwright 浏览器自动化，打开 **tm.aliyun.com**（阿里云商标频道），在搜索框中填入商标名、点击搜索按钮，然后解析搜索结果页面提取商标信息。

**tm.aliyun.com 是什么**：阿里云的商标注册服务平台，底层直连 CNIPA（国家知识产权局商标局）官方数据库。你在阿里云搜到的结果 = 商标局官网搜到的结果，同一个库，只是阿里云前端更好用（React SPA）。

**为什么必须走浏览器**：tm.aliyun.com 是 React 单页应用，用 curl/requests 只能拿到空壳 HTML，必须真实浏览器渲染后才能提取数据。

## 为什么不用搜索引擎？

| 方法 | 可靠性 | 原因 |
|------|:------:|------|
| Google/Bing 搜索 | ❌ 不可靠 | 搜索引擎不索引全部商标页，**已验证漏检活标**（如 VENALISA 22262952） |
| WebFetch / curl | ❌ 不可用 | tm.aliyun.com 是 React SPA，curl 只能拿到空 HTML |
| **本工具（Playwright）** | ✅ 可靠 | 真实浏览器渲染，直接访问 CNIPA 镜像数据库 |

## 安装

```bash
pip install playwright
playwright install chromium
```

## 用法

### 单名查询
```bash
python cnipa_search.py AVELZORA
```

### 指定类别
```bash
python cnipa_search.py VESARIA --class 3
python cnipa_search.py VESARIA --class 3 --class 35
```

### 批量查询
```bash
# 创建 names.txt，每行一个商标名
python cnipa_search.py --batch names.txt
```

### JSON 输出
```bash
python cnipa_search.py VESARIA --json
python cnipa_search.py --batch names.txt --json -o results.json
```

### 显示浏览器窗口（调试用）
```bash
python cnipa_search.py VESARIA --headed
```

## 输出示例

```json
{
  "query": "VESARIA",
  "total": 0,
  "class_filter": [3, 35],
  "results": [],
  "risk": "low"
}
```

## 风险等级

| 等级 | 含义 | 建议 |
|:----:|------|------|
| 🟢 low | 无近似活标 | 可直接申请 |
| 🟡 moderate | 远距近似（LD≥2） | 需代理评估 |
| 🔴 high | 近距近似（LD=1） | 不建议推进 |
| 💀 dead | 完全同名活标 | 不可注册 |

## 族枚举检索法

精准查询后必须做族枚举防漏检（CNIPA 近似审查不是精确匹配）：

| 枚举类型 | 示例（查 AVELZORA） |
|---------|---------------------|
| 精确名 | AVELZORA |
| 前3字母 | AVE* |
| 后3字母 | *ORA |
| 核心词根 | *ZOR* |
| 包含关系 | 检查结果中是否有 AVELZORA 完全包含/被包含于其他标 |

## AI 助手集成

### WorkBuddy 用户
加载 `SKILL.md` 即可，触发词：「查商标」「能不能注册」「商标查重」「近似障碍」。

### 其他 AI 工具（Codex CLI、Claude Code、Cursor 等）
直接调用本脚本：
```bash
python cnipa_search.py <商标名> --class 3 --class 35 --json
```

### 如果你用的是 agent-browser（非 playwright-cli）
⚠️ agent-browser 的 `type` 命令对 tm.aliyun.com 的 React 搜索框**无效**（不触发 React 合成事件）。必须使用 playwright 或 playwright-cli。

## 检索流程（内部原理）

脚本执行以下步骤，与你手动操作一模一样：

1. **打开浏览器** → 启动 Chromium，导航到 `https://tm.aliyun.com`
2. **构造搜索 URL** → 将商标名编码为阿里云搜索接口的 JSON 参数，直接跳转到搜索结果页，跳过手动填表
3. **等待渲染** → React SPA 需要 2 秒完成客户端渲染
4. **提取文本** → `page.inner_text("body")` 获取页面全部可见文本
5. **正则解析** → 用正则提取每条结果的：商标名、注册号、类别、状态、申请日期
6. **类别过滤** → 仅保留第 3 类（日化）和第 35 类（广告）的结果
7. **风险评估** → 同名 → `dead`；编辑距离=1 → `high`；有结果但非近距 → `moderate`；零结果 → `low`
8. **翻页** → 如超过 20 条结果，继续点击下一页直到全部遍历

## 限制

- 依赖 tm.aliyun.com 的页面结构（React SPA），如页面改版需更新解析逻辑
- 不代替官方近似查询——正式提交前仍需代理做 CNIPA 官网最终确认
- 每次查询约 3-5 秒，批量查询时注意速率

## 教训

- **2026-08-03**：AVELISA 案例 — WebSearch 宣称"零冲突"，实际 AVELISSA (89680981, 第3类已初审) 和 VENALISA (22262952, 第3类已注册) 均未检出。自此禁用间接检索，必须走浏览器直接查询。
- 第 3 类（化妆品）是中国商标注册最拥挤的类目之一，6-7 字母的命名空间非常饱和。
