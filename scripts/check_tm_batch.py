import subprocess, time, urllib.parse, json, re

candidates = ["AVZELUN", "AVZELVE", "AVZELMA", "AVZELTA", "AVZELVA", "AVZELNA"]
classes = ["3", "35", "10"]

skip_patterns = ['顾问','监控','中国商标网','您可试试','立即注册','阿里云','商标服务','JAVA',
    '打开菜单','文档','备案','控制台','登录','热门','智能','定制','商标注册',
    '精选','权益','大模型','产品','服务','解决方案','定价','云市场','伙伴','了解',
    '域名','什么是','全球','技术','稳定','安全','分析师','AI应用','全部产品',
    '免费','产品动态','配置','云上','开发者','天池','高校','推荐','基础服务',
    '企业','迁云','官网','健康','信任','大模型认证','全部认证','训练营',
    '官网公告','健康看板','我要','阿里云国际','www','Careers','社会','校园',
    '移动端','商标查询','商标监控','起名','分类','智能注册','商标顾问',
    '商标变更','商标驳回','商标续展','异议答辩','商标撤三','商标异议',
    '帮助','发票','商标控制台','法律','Cookies','廉正','联系','加入',
    '阿里巴巴','淘宝','千问','天猫','1688','阿里妈妈','飞猪','万网','高德',
    'UC','友盟','优酷','钉钉','支付宝','达摩院','浙','Kimi','GLM','Wan2',
    'Fun-ASR','AI 应用','秒悟','快速部署','即刻拥有','多模态','超强辅助',
    '计算','容器','存储','网络与CDN','中间件','数据库','开发工具','迁移与运维',
    '专有云','百炼','Qoder','HappyHorse','一句话生成','PPT','影视创作',
    '低风险','中风险','高风险','积极注册','尝试注册','谨慎注册',
    '风险图','查看近似','没有找到','商标类别','广告销售','日化用品',
    '化学原料','颜料油漆','燃料油脂','医药','金属材料','机械设备','手工器械',
    '科学仪器','医疗器械','灯具空调','运输工具','军火烟火','珠宝钟表','乐器',
    '办公用品','橡胶制品','皮革皮具','建筑材料','家具','厨房洁具','绳网袋蓬',
    '纱线丝','布料床单','服装鞋帽','纽扣拉链','地毯席垫','健身器材','食品',
    '方便食品','饲料种籽','啤酒饮料','酒','烟草烟具','金融物管','建筑修理',
    '通讯服务','运输贮藏','材料加工','教育娱乐','网站服务','餐饮住宿',
    '医疗园艺','社会服务','开启图形','商标检索','仅供参考','或','注册',
    '上海元来','代小虎','陈钢','channel','q=','pageNum','pageSize','classification',
    'searchType','ifPrecise','valid','image','orderId','Status','ApplyYear',
    'applyDateOrder','firstAnncDateOrder','regDateOrder','keyword','product',
    'AI\xea','漫剧工坊','电商营销','广告创作','建站','短剧','生产力先锋','飞天发布']

skip_patterns += candidates

for cand in candidates:
    for cls in classes:
        q = json.dumps({
            "keyword": cand, "searchType": "ALL", "pageNum": 1, "pageSize": 20,
            "classification": cls, "product": "", "Status": "", "ApplyYear": "",
            "applyDateOrder": "", "firstAnncDateOrder": "", "regDateOrder": "",
            "orderId": "", "valid": False, "ifPrecise": True, "image": ""
        })
        url = f"https://tm.aliyun.com/channel/search#/search?q={urllib.parse.quote(q)}"
        try:
            subprocess.run(["agent-browser", "open", url], capture_output=True, text=True, timeout=90)
        except subprocess.TimeoutExpired:
            print(f"{cand}\t{cls}类\t超时跳过\t-")
            continue
        time.sleep(5)

        r = subprocess.run(["agent-browser", "snapshot", "-i"], capture_output=True, text=True, timeout=30)
        lines = r.stdout.split("\n")
        target_ref = None
        target_count = "0"
        for line in lines:
            if f"{int(cls):02d}类" in line and "generic" in line and "clickable" in line:
                m = re.search(r'ref=(e\d+)', line)
                if m:
                    target_ref = m.group(1)
                    parts = line.split("类")
                    if len(parts) > 1:
                        cm = re.search(r'(\d+)', parts[-1])
                        if cm:
                            target_count = cm.group(1)

        if target_ref and target_count != "0":
            subprocess.run(["agent-browser", "click", f"@{target_ref}"], capture_output=True, text=True, timeout=30)
            time.sleep(4)

        subprocess.run(["agent-browser", "scroll", "down", "1000"], capture_output=True, text=True, timeout=15)
        time.sleep(1)

        r2 = subprocess.run(["agent-browser", "snapshot", "-i"], capture_output=True, text=True, timeout=30)
        rlines = r2.stdout.split("\n")

        marks = []
        for i, line in enumerate(rlines):
            if 'link "' in line:
                m = re.search(r'link "([^"]+)"', line)
                if m:
                    name = m.group(1)
                    if len(name) < 50 and not any(sp in name for sp in skip_patterns):
                        applicant = ""
                        for j in range(i+1, min(i+4, len(rlines))):
                            am = re.search(r'link "([^"]+)"', rlines[j])
                            if am:
                                an = am.group(1)
                                if any(x in an for x in ['公司','有限','科技','商贸','贸易','生物','化工','集团','国际','企业','事务所','工作室']):
                                    applicant = an
                                    break
                            sm = re.search(r'StaticText "([^"]+)"', rlines[j])
                            if sm:
                                sn = sm.group(1)
                                if any(x in sn for x in ['公司','有限','科技','商贸','贸易','生物','化工','集团','国际','企业']):
                                    applicant = sn
                                    break
                        marks.append(f"{name}" + (f" ({applicant})" if applicant else ""))

        seen = set()
        unique = []
        for m in marks:
            base = m.split(" (")[0]
            if base not in seen:
                seen.add(base)
                unique.append(m)

        result_str = " | ".join(unique[:6]) if unique else "无近似"
        print(f"{cand}\t{cls}类\t近似:{target_count}\t{result_str}")

print("\n=== DONE ===")
