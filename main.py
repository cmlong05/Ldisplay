import gpio as GPIO
import datetime
import time

#############################################################################
# 写数据
def tran_to_chip(data,dio,clk):
    # 物理传输数据到芯片
    bits = 16
    if len(data) == 1:
        bits = 8
    for byte in data:
        for bit in range(bits):
            GPIO.output(clk, 0)
            GPIO.output(dio, (byte >> bit) & 1)
            GPIO.output(clk, 1)
    
def command_display(stb,dio,clk,command,ABC_Data=[]):
    # 写入命令 与 数据
    GPIO.output(stb, 0)
    tran_to_chip(command,dio,clk)
    if len(ABC_Data) > 0:
        tran_to_chip(ABC_Data,dio,clk)
    GPIO.output(stb, 1)

def full_command_display(STB_arr,dio,clk,command,ABC_Data=[]):
    # 写入多行数据
    for stb in STB_arr:  
        command_display(stb,dio,clk,command,ABC_Data[:7])
        ABC_Data=ABC_Data[7:]
#############################################################################
## 转换函数
def reverseBits(n):
    # 颠倒二进制位
    n = '{:010b}'.format(n)[::-1]
    return int(n, 2)

def screen_code(array):
    # 屏幕显示码-数据 转换函数
    data=[]
    while array:
        # Remove the first two,移位后相加，颠倒后，加入数组
        data.append(reverseBits((array.pop(0) << 5) + array.pop(0)))
    return data

def transform(array, mark=0):
    # 组建全屏阵列数据，从文字码转换到屏幕码
    # 备料
    s_mark = mark << 1 #四角显示
    blank_length = 27 - len(array)
    round = blank_length // 2
    modulo = blank_length % 2
    elem_add_R = [0] * (round + modulo)
    elem_add_L = [0] * round
    new_array = elem_add_L + array + elem_add_R + [s_mark]
    # 转换 返值
    return screen_code(new_array)

###########################################################
# 文本传输到屏幕显示

def connected(arr_a,arr_b):
    # 判断连列数组是否相邻 以确定 是否需要加空列
    if len(arr_a) == 0:
        return 0
    a = arr_a[-1] 
    b = arr_b[0]
    x1 = a & b
    x2 = (a >> 1) & b
    x3 = (a << 1) & b
    if x1 == 0 and x2 == 0 and x3 == 0:
        return 0
    else:
        return 1
    
def showtext (STB_arr,dio,clk,startaddr,Dict,Text,mark=0,seconds=3):
    # 显示文本
    # 组成文本阵列
    screenData =[]
    for char in Text:
        if connected(screenData, Dict[char]):        # 判断是否需要加入空列
            screenData.append(0)
        screenData.extend(Dict[char])

    while screenData:
        data = transform(screenData[:27],mark)
        full_command_display(STB_arr,dio,clk,startaddr,data)
        screenData=screenData[27:]
        time.sleep(seconds)
        

#######################################################
## 应用

def displaytime(STB_arr,dio,clk,startaddr,dict,mark = 0b1000):
    # 显示时间
    current_time = datetime.datetime.now()
    formatted_time = current_time.strftime("%-I:%M")
    current_date = datetime.date.today()
    formatted_date = current_date.strftime("%m/%d")
    weekday = current_date.weekday()
    weekdays = ["周  一", "周  二", "周  三", "周  四", "周  五", "周  六", "周  日"]
    showtext(STB_arr,dio,clk,startaddr,dict,formatted_time,mark)
    time.sleep(6)
    showtext(STB_arr,dio,clk,startaddr,dict,formatted_date,0)
    time.sleep(2)
    showtext(STB_arr,dio,clk,startaddr,dict,weekdays[weekday],0)


######################################################

def waterfall(STB_arr=[581,582],dio=586,clk=585,startaddr=[0xc0]):
    # 瀑布
    a = 0b10000
    for i in range(5):
        arr = screen_code([a]*14)
        full_command_display(STB_arr,dio,clk,startaddr,arr)
        time.sleep(0.5)
        a = a >> 1


def bright(Brightness=1,base_Brt=0b10000111,STB_arr=[581,582],dio=586,clk=585):
    # 辉度调节
    a = 1
    for i in range(14):
        if Brightness == 8:
            a = -a
        Brightness += a
        if Brightness == 1:
            a = -a
        Brt = [base_Brt + Brightness]
        full_command_display(STB_arr,dio,clk,Brt)
        time.sleep(0.3)


def flash(times,Brt=[0x88],STB_arr=[581,582],dio=586,clk=585):
    # 闪烁
    no_Brt = [Brt[0] - 8]
    for i in range(times):
        full_command_display(STB_arr,dio,clk,no_Brt)
        time.sleep(0.5)
        full_command_display(STB_arr,dio,clk,Brt)
        time.sleep(0.5)

#######################################################
# 初始化
def initial(STB_arr,dio,clk,displaymode,addrmode,starAddr,base_Brt,Brightness):
    #初始化GPIO针脚
    GPIO.setup(dio, GPIO.OUT, initial=GPIO.HIGH)
    GPIO.setup(clk, GPIO.OUT, initial=GPIO.HIGH)
    GPIO.setup(STB_arr[0], GPIO.OUT, initial=GPIO.HIGH)
    GPIO.setup(STB_arr[1], GPIO.OUT, initial=GPIO.HIGH)

    # 显示模式设置
    full_command_display(STB_arr,dio,clk,displaymode)    # 7 位 10 段
    #地址增加模式 # 数据命令设置： 写数据到显示寄存器 普通模式 自动地址增加
    full_command_display(STB_arr,dio,clk,addrmode)
    # 全灭
    zero = [0]*14
    full_command_display(STB_arr,dio,clk,starAddr,zero)
    # 开启屏幕——显示控制命令设置, 默认低亮度
    Brt = [base_Brt + Brightness]
    full_command_display(STB_arr,dio,clk,Brt)
    # 全亮测试
    ff = [0x3ff]*14
    full_command_display(STB_arr,dio,clk,starAddr,ff)
