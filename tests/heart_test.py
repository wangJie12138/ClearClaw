import json
from datetime import datetime, timedelta

# 读取任务文件
with open("/clearclaw\workspace\\tasks.json", "r", encoding="utf-8") as f:
    tasks = json.load(f)

# 改成 2 分钟后
new_time = datetime.now() + timedelta(minutes=2)
tasks[0]["target_time"] = new_time.strftime("%Y-%m-%d %H:%M:%S")

# 写回文件
with open("/clearclaw\workspace\\tasks.json", "w", encoding="utf-8") as f:
    json.dump(tasks, f, ensure_ascii=False, indent=2)

print(f"任务时间已更新为: {tasks[0]['target_time']}")