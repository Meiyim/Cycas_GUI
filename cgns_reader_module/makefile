#!/bin/sh
cgns_include_dir=./include
cgns_lib_dir=./lib
cc=gcc
file_name=cgns_reader
all:
	$(cc) -fPIC -shared $(file_name).c -o $(file_name)_dll.so  \
   		-I$(cgns_include_dir)  \
		-L$(cgns_lib_dir) \
		-g \
		-fPIC\
		-std=c99 \
	 	-lcgns

