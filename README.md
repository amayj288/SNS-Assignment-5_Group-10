# SNS-CSL-443: Assignment 5
An implementation of the Ottway-Rees Protocol as part of the curriculum of the System and Network Security course in College.

The assignment consisted of 2 parts: Implementing the Keyed Transposition Cipher, and then implementing the Ottway-Rees Protocol 

1) Keyed Transposition Cipher
The file to run this is the 'trans_cipher.py' file which is inside the 'Keyed-Tranpsosition-Cipher Directory'.
The code has been explained in the video, and can be executed in the terminal as:


                 -> pip install pycipher
                 -> python trans_cipher.py
                 
Once this is run, it will ask the user to enter the inputs as required, and the user can enter them and see the required output.


2) Ottway-Rees Protocol

Extra modules to install: If it gives an error and doesn't run saying proper modules not installed, install the following model:

                 -> pip install pycryptodome
                 
The file to run this is the 'main.py' file which is inside the 'Ottway-Rees-Protocol Directory'.
The code has been explained in the video, and can be executed in the terminal in the following steps:

      i) Generate Keys/Provide own keys - We have generated random keys for using this Protocol of long length(16 bytes), so user doesn't have to worry about that. 
                                          Just open the terminal and execute the following command:
      
                  -> python main.py key
                                    
      ii) Main Execution: Since this - Since it involves communiaction between server and client, open 3 terminals with the path containing the 'main.py' file 
                                       and the generated keys in txt files. Then execute the following in the 3 separate terminals(in the same order as given i.e. first execute Terminal 1(KDC) then Terminal 2(Server) and then terminal 3 (client)):
      
                           Terminal 1:-
                                              -> python main.py KDC
                           
                           Terminal 2:-
                                              -> python main.py B
                                              
                           Terminal 3:-
                                              -> python main.py A
           
