#!/bin/python
import math
import random



class Client:
  global time_now
  global client_qdepth
  def __init__(self, id):
    self.last_op=0
    self.saved_op=0
    self.queue=dict()
    self.me_id=id;
    self.pg_count = 128 #just select something
    self.pg_list=[]
    for i in range(self.pg_count):
      self.pg_list.append(random.randint(0, osd_count-1))
  
  def generate_op(self):
    self.last_op=self.last_op+1
    data=random.randint(0, self.pg_count-1)
    osd=self.pg_list[data] #get osd that is primary for relevant PG
    self.queue[self.last_op]=osd
    self.send_request(osd, self.last_op)

  def generate_ops(self, max):
    result=False
    while (max > 0 and len(self.queue) < client_qdepth):
      self.generate_op()
      result=True
    return result
    
  def send_request(self, osd, op_id):
    network.request(self.me_id, osd, op_id)

  def got_response(self, op_id):
    #print("op_id="+str(op_id))
    op = self.queue.pop(op_id)
    #print("op="+str(op)+" size="+str(len(self.queue)))
    #self.generate_op()

  

class Network: #simulates all delays of transmission
  global time_now
  global network_delay
  requests = [] #tuples (ready_at, client, osd, op_id) 
  responses = [] #tuples (ready_at, client, op_id)
  def request(self, client, osd, op_id):
    #client is here so osd would know whom to reply
    self.requests.append((time_now + network_delay, client, osd, op_id))

  def response(self, client, op_id):
    self.responses.append((time_now + network_delay, client, op_id))
    #not need to pass osd only one could reply


  def process_requests(self):
    while (len(self.requests) > 0 and self.requests[0][0] <= time_now):
      req = self.requests.pop(0)
      osd=req[2]
      #print("r="+str(req[2]))
      osds[req[2]].request_op(req[1], req[3])

  def process_responses(self):
    #print("sr="+str(len(self.responses)))
    while (len(self.responses) > 0 and self.responses[0][0] <= time_now):
      rsp = self.responses.pop(0)
      clients[rsp[1]].got_response(rsp[2])
  
  def tick(self): #do all the data-moving magic
    #print("time="+str(time_now))
    self.process_requests()
    self.process_responses()





class OSD:
  def __init__(self):
    self.queue = [] # fifo queue of requests from clients that will be executed in order, unlimited depth
  def request_op(self, client, op_id):
    self.queue.append((client, op_id)) #op from specific client
    
  def execute_ops(self, max_ops_to_process):
    i = max_ops_to_process
    while (i > 0 and len(self.queue) > 0):
      op = self.queue.pop(0)
      network.response(op[0], op[1])
      i = i - 1


def pre_init_clients():
  for j in range(client_qdepth):
    for i in range(client_count):
      clients[i].generate_op()


def init():
  for i in range(client_count):
    c = Client(i)
    clients.append(c)
  for i in range(osd_count):
    o = OSD()
    osds.append(o)
  pre_init_clients()




def print_state():

  s=""
  for i in range(client_count):
    s=s+str(clients[i].last_op)+" "
    #print(str(i)+":"+str(clients[i].last_op))
  #print(s)
  s=s+" | "
  for i in range(osd_count):
    s=s+str(len(osds[i].queue))+" "
  #print(str(i)+":"+str(len(osds[i].queue)))
  print(s)

def print_diff_state():
  s=""
  for i in range(client_count):
    s=s+str(clients[i].last_op-clients[i].saved_op)+" "
    clients[i].saved_op = clients[i].last_op
  s=s+" | "
  for i in range(osd_count):
    s=s+str(len(osds[i].queue))+" "
  print(s)


def run_sim():
  global time_now
  global time_tick
  global client_max_per_tick
  global osd_process_per_tick
  global osd_count
  while (time_now < 1000000):
    network.tick()
    for i in range(osd_count):
      osds[i].execute_ops(osd_process_per_tick)
    start = random.randint(0, osd_count-1) #needed to have equal processing for each osd
                                           #its not magic, just difficult to explain

    for j in range(client_max_per_tick):
      added_some=False
      for i in range(client_count):
        osd = (i + start) % client_count
        added_some = added_some or clients[osd].generate_ops(1)
      #if not added_some:
      #  break
    time_now = time_now + time_tick
    if ((time_now % 10000) == 0):
      print_diff_state()
  
pg_mapping={}

time_tick=10
time_now=0
network = Network()
clients=[]
osds=[]
client_count=20
osd_count=8
network_delay=20

client_qdepth=60
client_max_per_tick=30
osd_process_per_tick=20

client_qdepth=260
client_max_per_tick=10
osd_process_per_tick=15
network_delay=20

client_qdepth=128
client_max_per_tick=10
osd_process_per_tick=15
network_delay=30

client_qdepth=256
client_max_per_tick=30/5
osd_process_per_tick=10/5
network_delay=20

#interesting attrition of client #18 and #19
client_qdepth=256
client_max_per_tick=10
osd_process_per_tick=25
network_delay=20

#client #19 varies horribly
client_qdepth=256
client_max_per_tick=10
osd_process_per_tick=15
network_delay=20


client_qdepth=512
client_max_per_tick=10
osd_process_per_tick=35
network_delay=40


client_qdepth=512
client_max_per_tick=30
osd_process_per_tick=35
network_delay=20



# clients #17 18 weak #19 sore loser
client_qdepth=256
client_max_per_tick=10
osd_process_per_tick=35
network_delay=20

#client #19 shines like a star
client_qdepth=256
client_max_per_tick=20
osd_process_per_tick=35
network_delay=20


#beautiful all clients same perf ~11000
client_qdepth=128
client_max_per_tick=30
osd_process_per_tick=30
network_delay=50

client_qdepth=256
client_max_per_tick=20
osd_process_per_tick=10
network_delay=100

#some fluctuations
client_qdepth=260
client_max_per_tick=10
osd_process_per_tick=15
network_delay=20

client_qdepth=128
client_max_per_tick=10
osd_process_per_tick=15
network_delay=20

client_qdepth=256
client_max_per_tick=10
osd_process_per_tick=15
network_delay=20

#reached 0 at some points in #19
client_qdepth=256
client_max_per_tick=8
osd_process_per_tick=15
network_delay=20





random.seed(0)
init()
run_sim()
