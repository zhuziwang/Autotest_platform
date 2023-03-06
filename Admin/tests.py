from selenium import webdriver

# Create your tests here.




# driver.get('http://www.baidu.com')
# print(driver.title)


import queue


q = queue.Queue(maxsize=10)

q.put(111)
q.put(222)
q.put(333)

print(q.get())
print(q.get())
print(q.get())
print(q.get())
