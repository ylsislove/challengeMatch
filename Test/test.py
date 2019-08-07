import time

old_time = time.time()
new_time = time.time()

print("我开始了：", old_time * 1000)

while (new_time - old_time) * 1000 < 3000:
    new_time = time.time()

print("我结束了：", new_time * 1000)