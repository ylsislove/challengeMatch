import re

# data = "0a0bAA05AFF10C0001FFFF000000000BC600002BAA05AF123456789AA05AF"
# # p = re.compile("(.*?aa05af(.*?))aa05af", re.IGNORECASE)
# # m = p.search(data)
# # if m:
# #     print(m.group(1))
# #     print(m.group(2))
# #
# #     data = data[len(m.group(1)):]
# #     print(data)
#
# p = re.compile(".*?aa05af(.*?)aa05af.*?", re.IGNORECASE)
# list = p.findall(data)
# print(list)

list = ["aa", "ab", "cc"]
print(str(list[1:]))
