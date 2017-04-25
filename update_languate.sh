#!/bin/sh
if [ $# -lt 1 ];then
    echo 'udpate b/r'
    exit -1
fi
if [ $1 == 'r' ];then
lrelease-qt4 cycas_gui_chinese.ts
fi

if [ $1 == 'b' ];then
pylupdate4 *.py -ts cycas_gui_chinese.ts 
linguist-qt4 cycas_gui_chinese.ts 
fi 

