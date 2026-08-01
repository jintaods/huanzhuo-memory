# Git 协作规范 / Git Collaboration Rules

> 本仓库用于多 AI 协作（Claude Code、Codex、Grok 等），请所有 AI 遵守以下规则。

---

## 🚫 **严禁操作**

### 1. 禁止强制推送
- ❌ **永远不要使用** `git push --force`
- ❌ **永远不要使用** `git push -f`
- ⚠️ 如果必须强制推送，使用 `git push --force-with-lease`（会检查远程是否被修改）

### 2. 禁止删除他人文件
- 推送前检查 `git status`
- 如果看到删除的文件（deleted），且不是你删的，**立即停止**
- 通知用户处理冲突

---

## ✅ **必须操作**

### 1. 推送前必须先拉取
```bash
git pull --rebase   # 先拉取远程更新
git push            # 再推送你的修改
```

### 2. 提交信息格式
```
[AI名称] 操作类型：简短描述
- 上传者：模型版本
- 时间：YYYY-MM-DD
- 来源：文件原始路径（如果是上传文件）
```

**示例：**
```
[Claude Code Desktop] 新增：东方女性护肤广告图2
- 上传者：Claude Opus 4.8 (桌面版)
- 时间：2026-08-01
- 来源：Desktop/生图的创意图GPT/微信图片_20260531223958_151_21.png
```

```
[Codex CLI] 新增：商标查询方法论文档
- 上传者：Codex GPT-5.6-sol
- 时间：2026-08-01
```

---

## 🔄 **标准工作流程**

### 上传新文件
```bash
git pull --rebase              # 1. 先拉取
cp /path/to/file .             # 2. 复制文件
git add file.ext               # 3. 添加文件
git commit -m "[AI名称] ..."   # 4. 提交（按格式）
git push                       # 5. 推送
```

### 修改现有文件
```bash
git pull --rebase              # 1. 先拉取
# 编辑文件...
git add file.ext               # 2. 添加修改
git commit -m "[AI名称] ..."   # 3. 提交
git push                       # 4. 推送
```

### 遇到冲突
```bash
# 如果 git pull 报冲突：
git status                     # 查看冲突文件
# 通知用户："遇到冲突，需要你手动处理以下文件：xxx"
# 不要擅自解决复杂冲突
```

---

## 📂 **仓库结构**

```
huanzhuo-memory/
├── README.md                           # 仓库说明
├── GIT_RULES.md                        # 本文件（协作规范）
├── 焕琢商标查询_记忆存档.md             # 商标查询项目记忆
├── METHODS.md                          # 方法论文档
├── 自然声音放松工具.html               # 放松工具成品
├── 东方女性护肤广告图.png              # 广告素材
├── 东方女性护肤广告图2.png             # 广告素材
└── scripts/
    ├── README.md                       # 脚本说明
    ├── check_tm_batch.py               # 商标批量查询（原版）
    └── query_tm_batch.py               # 商标批量查询（改进版）
```

---

## 🤝 **协作原则**

1. **尊重他人提交** - 不要覆盖或删除其他 AI 的文件
2. **先拉后推** - 永远先 `git pull`，再 `git push`
3. **清晰标注** - 提交信息必须说明是谁、做了什么
4. **遇事通知用户** - 遇到冲突、错误、不确定的情况，立即停止并通知用户

---

## ⚠️ **违规后果**

- 强制推送导致文件丢失 → 需要其他 AI 花时间恢复
- 覆盖他人提交 → 破坏协作，浪费所有人的时间
- 不标注来源 → 无法追溯文件历史

**请所有 AI 严格遵守本规范！**

---

*最后更新：2026-08-01 by Claude Code Desktop*
