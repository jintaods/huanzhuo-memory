# 商标查询方法论 — Methodology

> 本文件教 AI 工具（Codex / Claude Code / WorkBuddy 等）如何为"焕琢 AVELZORA"品牌查询新英文商标的近似风险。
> 配套脚本见 `scripts/` 目录。
> 背景与已确认结论见 `焕琢商标查询_记忆存档.md`。

---

## 一、目标

为焕琢品牌找一个新英文商标，需在第3类（日化/护肤）、第35类（广告销售）、第10类（医疗器械/美容工具）**三类全部零近似**才能注册，要求99%通过率、好听好记、A或AV开头。

---

## 二、核心结论（先读这个，避免走弯路）

### ⚠️ 最重要的一条：网页端不可信，必须手机端复核

- 阿里云商标网**网页版** `tm.aliyun.com` 用精准查询时**有严重漏报**。
  - 实例：AVZELMA、AVZELVA 网页端显示"0近似"，实际手机端查出 ADVELMA、AVZOZVA（已注册）。
  - AVELINE、AVENIRE、AVELORA、ALZENA 网页端全0，手机端全有近似。
- **阿里云商标手机端小程序/App 的近似算法更宽更全，结果更可信。**
- **判定标准：最终一律以手机端为准。网页端只能当粗筛。**

### ⚠️ 第二条：纯造词才安全，沾真实单词必撞车

- 安全的名字（AVZELUN/VE/TA/NA）是**纯无意义造词**，在任何语言里都不是真实词汇，天然零近似。
- 失败的（AVELINE=Aveline法语名、AVENIRE=Avvenire意语"未来"、AVELORA=VELORA、ALZENA=ALENA）都是**为了好听偷用了真实词感**，结果全撞车。
- **教训：好听与安全在商标上基本矛盾，只能走"顺口的纯造词"。**

### 已确认安全候选（手机端三类全清）
AVZELNA、AVZELUN、AVZELVE、AVZELTA（AVZELNA 为首选）

### 已排除（撞车）
AVZELMA(ADVELMA)、AVZELVA(AVZOZVA)、AVELORA(VELORA)、ALZENA(ALENA)、AVELINE(3类已注册)、AVENIRE(AVENIEE/AVVENIRE)、ALVENA、AVENIRA

---

## 三、AI 查询操作 SOP

### 方案A：用网页端 agent-browser 粗筛（快，但需手机端复核）

适合有浏览器自动化能力的环境（如 WorkBuddy 的 `agent-browser` CLI）。

1. 构造查询 URL（关键参数 `ifPrecise=true`、`classification` 为 "3"/"35"/"10"）：
   ```
   https://tm.aliyun.com/channel/search#/search?q={JSON}
   ```
   JSON 示例：
   ```json
   {"keyword":"AVZELNA","searchType":"ALL","pageNum":1,"pageSize":20,
    "classification":"3","product":"","Status":"","ApplyYear":"",
    "applyDateOrder":"","firstAnncDateOrder":"","regDateOrder":"",
    "orderId":"","valid":false,"ifPrecise":true,"image":""}
   ```
2. 打开 URL → snapshot 提取各类近似计数（如 `03类 日化用品0`）→ 若计数非0，点击该类展开提取具体近似商标名与申请人。
3. 用 `eval document.body.innerText` 验证是否真的"共有0个搜索结果"（网页端前端计数常有bug，显示"1"实际为0）。
4. **把网页端0近似的候选列出来，交用户手机端复核。绝不自行判定"安全"。**

### 方案B：直接指导用户在手机端查询（最准，推荐）

让用户在阿里云商标小程序：
1. 搜索商标名 → 看是否"未检索到近似商标"
2. 单类详情页看与哪些已注册商标构成近似、风险等级
3. 全45类概览页看整体风险分布（注意：概览页常显示全绿，单类详情页才严格，以单类详情页为准）

---

## 四、命名生成策略（生成新候选时遵循）

1. **前缀用 A 或 AV**（与家族 AVELZORA/AVENZORA 呼应）
2. **纯造词**：A开头 + 2-3个无意义元音/辅音音节组合，6-8字母
3. **避开已知真实词根**：VEL、LOR、ZORA、ZEN、LENA、ENIR、ALENA、AVEN、ADVE、AVZO、ZOZ、ELMA
4. **发音顺口**：结尾用开口音（na/ta/ve/un/ra/la），避免拗口组合
5. 每生成一个批次，网页端粗筛后，**必须手机端复核**

---

## 五、已知环境坑（踩过的雷）

| 问题 | 现象 | 解决 |
|---|---|---|
| 浏览器残留进程 | `CDP command timed out` | `pkill -9 -f agent-browser` 后重开 |
| 限流/风控 | 约80次查询后阿里云弹"异常流量" | 关闭浏览器等20分钟再开 |
| 结果区空白 | 快照只显示页脚 | 用 `eval document.body.innerText` 取文本 |
| 网页端漏报 | 显示0实际有近似 | 必须手机端复核 |
| 沙箱无法直连GitHub HTTPS | API请求被拦截返回空 | 改用 **SSH 22端口**（生成SSH key，加到GitHub账号） |
| GitHub DNS被劫持 | 解析到 198.18.0.10 | 写 `/etc/hosts` 绑定真实IP 或 用SSH |

---

## 六、给接手AI的指令模板

> "请先读 GitHub 仓库 jintaods/huanzhuo-memory 里的 `焕琢商标查询_记忆存档.md` 和 `METHODS.md`，了解焕琢商标查询的背景、已确认安全候选和排除清单。然后为品牌生成一批新的**纯造词**候选（A开头，避开 VEL/LOR/ZORA/ZEN/LENA 等真实词根），用网页端粗筛后列出待手机端复核名单。"

---

*此方法论文档随记忆存档一同维护，更新时 commit 到本仓库。*
