#!/usr/bin/python
# -*- coding: UTF-8 -*-

from main import *
import time
import json
# import schedule

# 四角参数 左上角逆时针表示
mark = 0b1111 # 全亮，左上角逆时针 控制
STARTADDR = [0xc0]
DPMODE = [0x03]
AUTOADDR = [0x40]
BASE_BRT = 0b10000111 
Brightness = 1

DIO = 586
CLK = 585
STB_ARR = [581,582]

# 导入字典
with open("dict.json", "r") as f:
  dict = json.load(f)

###############################
# 初始化
initial(STB_ARR,DIO,CLK,DPMODE,AUTOADDR,STARTADDR,BASE_BRT,Brightness)

# 灰度测试
bright(Brightness)
# 闪烁3次
Brt = [BASE_BRT + Brightness]
flash(3, Brt)

# 显示 LibWrt 图标
text = "LibWrt"
mark = 0 
showtext(STB_ARR,DIO,CLK,STARTADDR,dict,text,mark)
time.sleep(3)

####显示时间和日期
# schedule.every(1).minutes.do(displaytime())

while True:
#   schedule.run_pending()
    displaytime(STB_ARR,DIO,CLK,STARTADDR,dict)
    time.sleep(2)