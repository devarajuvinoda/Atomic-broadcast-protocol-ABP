# Atomic-broadcast-protocol-ABP
Implementation of ABP in Python from scratch. Used multi-threading for sending and receiving messages via TCP and Lamport logical clock for achieving total order.


bs - broadcast server, ap - application process 

The array, group_members contains three values (additional servers can be added based on the requirement) and the configuration of broadcast servers and application process is shown in config.png file.


1. bs1, bs2, bs3 listen for incoming connections
2. bs1 connects to bs2 and bs3; bs2 connects to bs3 and bs1; bs3 connects to bs1 and bs2;
3. a new ap1 connects to bs1, ap2 connect to bs2 and ap3 connects to bs3
4. 
	* ap1 sends a message to bs1, bs1 then sends that message to bs2 and bs3; 
		now bs2 and bs3 inturn sends those messages to ap2 and ap3
	* ap2 sends a message to bs2, bs2 then sends that message to bs1 and bs3.
		now bs1 and bs3 inturn sends those messages to ap1 and ap3
	* ap3 sends a message to bs3, bs3 then sends that message to bs2 and bs1.
		now bs2 and bs1 inturn sends those messages to ap2 and ap1
5. Application will receive the messages according to atomic broadcast protocol specification, with the help of local hold back queue.
