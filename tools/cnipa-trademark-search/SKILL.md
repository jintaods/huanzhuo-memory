---
name: cnipa-trademark-search
description: CNIPA 中国商标局精准检索——通过 playwright-cli 沙箱浏览器直接在 tm.aliyun.com（阿里云商标频道，底层为 CNIPA 官方数据库）执行商标近似查询。当用户要查"XX 商标能不能注册""XX 在第3/35类有没有近似障碍""商标查重""批量候选名筛查"时调用。要求准确率优先、不允许用 WebSearch/WebFetch 替代。
agent_created: true
---

# CNIPA 商标精准检索（playwright-cli 沙箱版）

## 为什么需要这个技能

### 已验证的不可靠方案

| 方法 | 问题 | 实例 |
|------|------|------|
| **WebSearch** | 搜索引擎只索引部分商标页面，系统性漏检 | VENALISA (22262952, 第3类) 在 Google/Bing 搜不到，但在 CNIPA 是活标 |
| **WebFetch** | tm.aliyun.com 是 React SPA，客户端渲染，WebFetch 只能拿到空 HTML shell | `WebFetch https://tm.aliyun.com/search?q=AVELISA` 返回空 |
| **agent-browser `type`** | `type` 命令不触发 React 合成事件（synthetic events），输入框内容不会被 React state 接收 | 对 tm.aliyun.com 搜索框 type 后点击搜索，页面无反应 |

### 唯一可靠方案：playwright-cli

playwright-cli 的 `fill` 命令原生支持 React 表单——它会触发完整的 input + change 事件链，让 React SPA 正确接收输入。这是目前唯一能在沙箱中准确查询 CNIPA 商标数据库的方法。

**playwright-cli v0.1.17 已安装，路径：** `C:\Users\user\AppData\Local\Programs\WorkBuddy\resources\app.asar.unpacked\resources\extensions\playwright-cli\bin\playwright-cli.exe`

---

## 标准检索流程

### 第 1 步：启动浏览器并打开 tm.aliyun.com

```bash
playwright-cli open https://tm.aliyun.com
```

等待页面加载完成后，使用 `snapshot` 确认搜索界面已渲染。

### 第 2 步：执行搜索（核心操作）

tm.aliyun.com 首页的搜索框通常在页面中部，有两个关键元素：
- 搜索输入框（textbox，通常 ref 以 `e139` 附近）
- 搜索按钮（button，通常 ref 以 `e144` 附近）

**必须先 `snapshot` 确认当前页面的元素 ref，因为 ref 号会随页面加载状态变化。**

```bash
# 确认元素 ref
playwright-cli snapshot

# 填入商标名（必须用 fill，不能用 type）
playwright-cli fill <搜索框ref> "AVELISA"

# 点击搜索按钮
playwright-cli click <搜索按钮ref>
```

**关键：**`fill` 命令会依次触发 focus → input → change → blur，这是 React 受控组件正确接收值的必要条件。`type` 命令不触发 React 合成事件，会导致搜索失败。

### 第 3 步：截图 + 快照获取结果

搜索完成后，页面会跳转到搜索结果页。执行：

```bash
# 截图存证
playwright-cli screenshot --path=<name>.png

# 获取结构化 YAML 快照用于解析
playwright-cli snapshot --path=<name>.yaml
```

**重要：**`snapshot` 生成的 YAML 文件是结构化的，可以直接用 `Read` + `Grep` 工具解析，无需浏览器渲染。

### 第 4 步：解析 YAML 快照提取关键信息

从 YAML 快照中提取每条商标记录的以下字段：

- **商标名称**：搜索 `link "<NAME>"` 模式
- **当前状态**：紧随名称后的 `generic` 标签文本（已注册 / 已初审 / 待审中 / 已驳回 / 已无效）
- **商标类别**：`商标类别：` → `第XX类-XXX`
- **注册号**：`注册号：` → 数字串
- **申请日期 / 初审日期 / 注册日期**：对应的日期字段
- **申请人**：`申请：` → link 文本
- **代理机构**：`代理机构：` 后的文本
- **商品/服务项**：`商品/服务项：` → 类似群号列表（如 `0301、0306`）

**每条记录的结构模板（YAML 中反复出现）：**

```yaml
- link "商标名" [ref=xxx]:
    - /url: https://tm.aliyun.com/detail/xxxx_注册号_类别
- generic [ref=xxx]: 状态文本
- generic [ref=xxx]:
    - generic [ref=xxx]: 当前状态：
    - text: 状态文本
    - generic [ref=xxx]: 商标类别：
    - text: 第XX类-类别名
    - generic [ref=xxx]: 注册号：
    - text: "注册号"
    # ... 更多字段
```

### 第 5 步：翻页获取全部结果

搜索结果页底部有分页器。YAML 快照中会显示总页数：

```yaml
- emphasis [ref=xxx]: "1"
- text: /N    # N 为总页数
```

点击下一页按钮（ref 通常为类似 `f1e286` 的递增编号）：

```bash
playwright-cli click <下一页按钮ref>
playwright-cli screenshot --path=<name>_p2.png
playwright-cli snapshot --path=<name>_p2.yaml
```

重复直到所有页遍历完毕。

### 第 6 步：查看商标详情（可选，当需要确认类似群时）

每个商标条目有一个 `https://tm.aliyun.com/detail/xxxx_注册号_类别` 格式的链接。点击该链接可查看详细信息页，包含完整的类似群商品列表。

```bash
playwright-cli click <详情链接ref>
playwright-cli screenshot --path=<name>_detail.png
```

### 第 7 步：关闭浏览器

```bash
playwright-cli close
```

---

## 族枚举检索法（防漏检核心）

**绝对不可以用"只搜精确词"了事**。这已被多次验证会导致系统性漏检。对每个候选名称，必须执行以下全部检索类别，**且第3类和第35类各做一遍**：

### 必做清单（每个候选 × 每类）

| # | 检索类型 | 示例（候选=VELZORA） | 目的 |
|---|---------|---------------------|------|
| 1 | **精确名** | `VELZORA` | 确认自身记录 |
| 2 | **前3字母族** | `VEL*` 或 `VEL` | 捕获同前缀变体（VELORA, VELIORA, VELLORA...） |
| 3 | **后3字母族** | `*ORA` 或 `ORA` | 捕获同后缀变体（VELORA, MELORA, DELORA...） |
| 4 | **核心词根族** | `*ZOR*` | 捕获含核心词根的变体（ZORA, AZORA, VANZO...） |
| 5 | **包含关系检查** | 检查候选是否包含已注册更短名（VELZORA ⊃ VELORA） | 防"大鱼吃小鱼"型冲突 |

**第 5 类需特别注意**：如果候选名 A 完全包含已注册商标名 B（如 VELZORA 包含 VELORA），且 B 在第3类已注册，则 A 大概率被驳回——这是 CNIPA 审查中的"包含关系近似"原则。

### 著名商标交叉核对

对每个候选的字母组成，必须核对以下著名品牌是否构成近似（这些品牌在第3类有密集防御注册）：

- ZARA (Inditex) — 4字母级 Z*RA 家族
- AVÈNE (雅漾) — AV*NE 家族
- 欧莱雅/资生堂/宝洁旗下各品牌

---

## 风险评估框架

### 1 字母红线（硬性规则）

在第3类（日化用品）和第35类（广告销售），候选英文标与已注册/待审/初审标**仅差 1 个字母**（Levenshtein 编辑距离 ≤1）→ **一律判不可行**。

- 同长度6字母 → 5同+1不同 → 冲突
- 7字母 → 6同+1不同 → 冲突
- 长度差1且只差1字母 → 冲突

必须**至少差 2 个字母**且**发音明显不像**才算可区分。

### 风险等级定义

| 等级 | 条件 | 建议 |
|------|------|------|
| 🔴 **高** | 同类似群(0306) + 活标 + 编辑距离≤1 或读音近似 | 不建议推进 |
| 🟡 **中** | 同大类(第3类) + 不同类似群 + 活标 + 编辑距离2 | 需代理评估 |
| 🟢 **低** | 不同类 或 死标 或 编辑距离≥3 | 可考虑 |

### 活标 vs 死标判断

| 状态 | 判定 | 说明 |
|------|------|------|
| 已注册 | **活标** | 有效期内的注册商标，构成引证障碍 |
| 已初审 | **活标** | 初审公告中，即将注册，构成障碍 |
| 待审中 | **活标** | 审查中，可能注册也可能驳回，按活标计 |
| 驳回复审中 | **活标** | 复审中，仍有可能翻盘，按活标计 |
| 已驳回 | **死标** | 驳回未复审或复审失败，不构成障碍 |
| 已无效 | **死标** | 过期/注销/撤销，不构成障碍 |

---

## 输出格式要求

对每个候选名，输出以下风险矩阵：

```
## [候选名] — 第3类 + 第35类 风险评估

### 第3类（日化用品/化妆品）
| # | 商标名 | 注册号 | 状态 | 申请人 | 编辑距离 | 类似群 | 风险 |
|---|--------|--------|------|--------|----------|--------|------|

### 第35类（广告销售）
| # | 商标名 | 注册号 | 状态 | 申请人 | 编辑距离 | 类似群 | 风险 |
|---|--------|--------|------|--------|----------|--------|------|

### 综合判定
- 风险等级：[高/中/低]
- 致命障碍：[列出]
- 建议：[推进/不推进/需代理评估]
```

每次输出必须附带免责声明：**结论基于 tm.aliyun.com 镜像检索，正式提交前需代理做 CNIPA 官方近似查询。**

---

## 已验证的教训与红线

1. **严禁用 WebSearch/WebFetch 替代沙箱浏览器查询**——已被多次验证会漏掉活标。
2. **严禁用 agent-browser 的 `type` 命令**——对 React SPA 无效。
3. **严禁只搜精确词**——必须做完整的族枚举（前3字母、后3字母、核心词根）。
4. **必须同时查第3类和第35类**——单查一类会漏跨类活标。
5. **包含关系是高频漏检**——VELZORA ⊃ VELORA，候选包含已注册短名即冲突。
6. **"未搜到" ≠ "可注册"**——镜像有索引延迟（1-3天），最终以 CNIPA 官方查询为准。
