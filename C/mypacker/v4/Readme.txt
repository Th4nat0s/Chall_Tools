need :
	python 2
	yasm
	mingw
	pelles linker (run with wine set the path in makefile)
	make essentials


This will do a fake UPX with a packed executable launched with runpe method

usage : 

make pack infile=myfile.exe

or for console apps

make pack_cons infile=myfile.exe
