import socket
import threading
import sys
import ast
import copy
import heapq


group_members = [("127.0.0.1", 8998), ("127.0.0.1", 8999), ("127.0.0.1", 9000)]

id = 0

# lamport clock
clock = 0
clocklock = threading.Lock()

# hold back queue, used to deliver messages in order
hold_back_q = []
heapq.heapify(hold_back_q)
qlock = threading.Lock()

# dictionary to keep track of message acknowledgements
acks = {}

sndlock = threading.Lock()

def receive():
	print('in receive....')
	while True:
		try:
			msg = client.recv(1024)
			msg = msg.decode("UTF-8")
			msg_dict = ast.literal_eval(msg)

			if(msg_dict['first']==False):
				
				global clock
				clocklock.acquire()	
				clock = max(clock, msg_dict['clock'])+1
				clocklock.release()
        		
        		# a mesage is identified by the original sender's id, it's clock value
				value = (msg_dict['sender_id'], msg_dict['clock'])

        		#if we have seen this message (or an ack from it) before
				if value in acks:
				    #if this is an ack, add to the end 
					if msg_dict['ack']:
						acks[value].append(msg_dict)
		            #if this is the original message, put it in the front
					else:
						acks[value].insert(0, msg_dict)
		        #first time we have seen this message, add it to our list
				else:
					acks[value]=[msg_dict]

				# When a process receives a message, it is put into a local
				# queue, ordered according to its timestamp. The receiver
				# multicasts an acknowledgment to the other processes. 

		        # this is the original message, push it in our hold-back queue
				qlock.acquire()
				global hold_back_q
				if(msg_dict['ack']==False):
					print("this message is not 'ack'(ed), so adding the message to local 'hold back queue': ")
					print("message: ",msg_dict['message'])
					print("logical clock of the sender: ",msg_dict['clock'])
					print("sender id: ",msg_dict['sender_id'])
					print("logical clock of the current node: ",clock)
					print('------------------------------------------------------------')
					heapq.heappush(hold_back_q, ((msg_dict['clock'], msg_dict['sender_id']), msg_dict))

				# A process can deliver a queued message to the application it
				# is running only when that message is at the head of the
				# queue and has been acknowledged by each other process. At
				# that point, the message is removed from the queue and
				# handed over to the application;

				# Each process has the same copy of the queue, all messages
				# are delivered in the same order everywhere. 

		        # got all the acks, mark this message to be delivered
				if(len(acks[value])==len(group_members)): 
					print("got 'ack' from all group_members for the following message: ") 
					print("the message will be removed from the queue and handed over to the application.") 
					print("message: ",acks[value][0]['message']) 
					print("logical clock: ",acks[value][0]['clock']) 
					print("sender id: ",acks[value][0]['sender_id']) 
					print("logical clock of the current node: ",clock) 
					print('------------------------------------------------------------')
					del acks[value]

				m = copy.copy(msg_dict)
				qlock.release()
        		
        		#if this message was a regular message (not an ack), ack it
				if( not m['ack'] and m['sender_id']!=id):
					m['ack'] = True
					m = (str)(m)
					client.send(m.encode())
			
		except:
			print("an error has occured!")
			# client.close()
			break


# Consider a group of processes multicasting messages to each other. Each 
# message is always timestamped with the current (logical) time of its sender.

# we assume that messages from the same sender are received 
# in the order they were sent, and that no messages are lost.
def write():
	while True:
		msg = input(">> ")
		global clock
		clocklock.acquire()
		clock = clock+1
		clocklock.release()

		sndlock.acquire()
		msg_val = {'message':msg, 'clock':clock, 'sender_id':id, 'ack':False, 'first':False}
		msg_val = (str)(msg_val)
		client.send(msg_val.encode())
		if(msg == "exit"):
			client.close()
			break
		sndlock.release()

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

id = int(sys.argv[1])
client.connect(group_members[int(id)])
        
# process incoming messages in a separate thread
receive_thread = threading.Thread(target=receive)
receive_thread.start()

send_thread = threading.Thread(target=write)
send_thread.start()
