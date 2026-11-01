# 网站文案与数据

> 推送者：Codex CLI ｜ 日期：2026-11-01

这里保存网站可直接读取的文案和数据。建议一份内容对应一个文件，文件名使用英文 slug。

## Markdown 模板

```markdown
---
title: 页面标题
slug: page-slug
status: draft
updated: 2026-11-01
seo_title: 搜索标题
seo_description: 搜索摘要
---

正文内容。
```

## 规则

- `status` 使用 `draft`、`review` 或 `published`。
- 对外文案不要出现内部代号、未确认功效、供应商名称和未公开价格。
- 产品功效描述必须和已有证据一致，不把配方设想写成已证实结论。
- 中文是主文案，需要英文版本时另建 `*.en.md`，不要覆盖中文原文。
