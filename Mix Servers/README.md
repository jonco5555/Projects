# Mix Servers

Implementation of a Network Communication System with several servers that allows anonymous communication against Eavesdropping attacks using Cryptography Concepts

Instructions how to execute appears in the PDF file in Hebrew.

Sum up in English:
 1. Run mix.py and send a number as command line argument (the number should be as the number of lines in the ips.txt file)
    It also means that the corresponding pk_i and sk_i are used by this mix server.
 2. In order to create multiple mixes, one can run mix.py again in cmd with different number, or run mix2.py and mix3.py in the IDE, and create more as he wishes.
 3. After the mixes servers are running, run the receivers. Send [password, salt, port] as command line arguments. Same password and salt that appear in the messagesX.txt.
 4. Now, execute sender.py. Send a number X as command line argument to open messagesX.txt.
 5. Wait for the code to run, each server sends the messages ha's gathered last 60 seconds, every 60 seconds. It could be changed for faster test in line 24 in mix.py.

Example for a line in messagesX.txt:
  cc cc 3,2,1 0 password salt 127.0.0.1 5000
  
  cc cc - message
  3,2,1 - path, mix3 -> mix2 -> mix1 (the numbers correspond to the number in the command line in the execution)
  0 - round, message should be sent on first round. If it was 1, the message should be sent after 60 secs
  password - password for symmetric key creation
  salt - salt for symmetric key creation
  127.0.0.1 - destination IP
  5000 - destination port
 
receiver2.py is for messages2.txt, there are two targets there.
