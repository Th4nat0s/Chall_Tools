Generic multithreaded Bruteforcer

Need only to change the test function.

Default:
Charset a-z, lenght 1-8, 4 Thread.

Options (// not done)
-t number ; Threads
//-c charset; could be 
	A for A-Z
	a for a-z
	0 for 0-9
	f for all printable
	c for custom (need cc parameter)
//-cc custom charset ex: -cc "ABCD$0", meta allowed $A $b $0 $! (dont forget to double $ for '$')
-m min lenght
-M max lenght
//-nowin do not break on win
-print (print passwords)

