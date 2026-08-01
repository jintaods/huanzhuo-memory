# 商标查询脚本使用说明

## 环境依赖

- Python 3.11+
- `agent-browser` CLI（WorkBuddy 内置的浏览器自动化工具，真实 Chromium）
- 能访问 `tm.aliyun.com` 的网络环境

## 运行方式

```bash
python3 scripts/check_tm_batch.py
```

## 脚本功能

`check_tm_batch.py` 会批量查询一组候选商标在第3类、第35类、第10类的近似风险：

- 通过 `agent-browser` 打开阿里云商标网查询URL（带 `ifPrecise=true` 精准参数）
- 从页面快照提取各类近似计数
- 计数非0时点击展开，提取具体近似商标名与申请人
- 用 `document.body.innerText` 验证是否真的"共有0个搜索结果"（规避前端计数bug）

## 修改候选名单

编辑脚本顶部的：
```python
candidates = ["AVZELNA", "AVZELUN", "AVZELVE", "AVZELTA"]  # 候选商标
classes = ["3", "35", "10"]                                  # 查询类别
```

## ⚠️ 重要警告

1. **网页端结果仅供参考，必须手机端复核**。脚本查出的"0近似"不代表真安全（实测 AVZELMA/AVZELVA 网页端0但手机端有近似）。
2. 运行前确认 `agent-browser` 浏览器已就绪，残留进程用 `pkill -9 -f agent-browser` 清理。
3. 约80次查询会触发阿里云限流，需等待20分钟。
4. 生成新候选时遵循 `../METHODS.md` 的纯造词策略，避开 VEL/LOR/ZORA/ZEN/LENA 等真实词根。

## 输出示例

```
AVZELNA	3类	近似:0	无近似
AVZELNA	35类	近似:0	无近似
AVZELNA	10类	近似:0	无近似
```
