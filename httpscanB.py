#!/usr/bin/env python
#coding:utf-8

import re
import sys
import queue as Queue
import threading
import optparse
import requests
from IPy import IP
import os

printLock = threading.Semaphore(1)  #lock Screen print
TimeOut = 3  #request timeout

per_ip="106.15."
aft_ip=".94"
str_ip=per_ip+"_"+aft_ip

ip_list=[]
for i in range(0,255):
	ip_list.append(str(per_ip+str(i)+aft_ip))

print(ip_list)
if os.path.exists("./log"):
	pass
else:
	os.mkdir("./log/")
#User-Agent
header = {'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.125 Safari/537.36','Connection':'close'}

class scan():

  def __init__(self,threads_num):
    self.threads_num = threads_num
	#build ip queue
    self.IPs = Queue.Queue()
    for ip in ip_list:
      ip = str(ip)
      self.IPs.put(ip)

  def request(self):
    with threading.Lock():
      while self.IPs.qsize() > 0:
        ip = self.IPs.get()
        try:
          #print(ip)
          r = requests.Session().get('http://'+str(ip),headers=header,timeout=TimeOut)
          r.encoding='utf-8'
          status = r.status_code
          title = re.search(r'<title>(.*)</title>', r.text) #get the title
          if title:
            title = title.group(1).strip().strip("\r").strip("\n")[:30]
          else:
            title = "None"
          banner = ''
          try:
            banner += r.headers['Server'][:20] #get the server banner
          except:pass
          printLock.acquire()
          print ("|%-16s|%-6s|%-20s|%-30s|" % (ip,status,banner,title))
          print ("+----------------+------+--------------------+------------------------------+")

          #Save log
          with open("./log/"+str_ip+".log",'a') as f:
            f.write(ip+"\n")

        except Exception as e:
          printLock.acquire()
        finally:
          printLock.release()

  #Multi thread
  def run(self):
    for i in range(self.threads_num):
      t = threading.Thread(target=self.request)
      t.start()

if __name__ == "__main__":
  parser = optparse.OptionParser("Usage: %prog [options] target")
  parser.add_option("-t", "--thread", dest = "threads_num",
    default = 30, type = "int",
    help = "[optional]number of  theads,default=30")
  (options, args) = parser.parse_args()
  print ("+----------------+------+--------------------+------------------------------+")
  print ("|     IP         |Status|       Server       |            Title             |")
  print ("+----------------+------+--------------------+------------------------------+")

  s = scan(threads_num=options.threads_num)
  s.run()
