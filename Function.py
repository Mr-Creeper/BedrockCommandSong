import os
from mido import MidiFile

time = 0
tempo = 500000#设置默认拍数（后面大概率会被改，主要是防报错）
lastTime = 0#当前播放音符与上一个播放音符相隔的时间
xyzMax=[1,254,1]
b1=0
detect = [False,0]
block=["concretepowder","concrete","stained_hardened_clay","_glazed_terracotta","stained_glass"]#36-51,52-67,68-83,84-99,100-108
df=["white","orange","magenta","light_blue","yellow","lime","pink","gray","light_blue","cyan","purple","blue","brown","green","red","black"]
'''
函数：将time转换为方块数量
需要提交：音符的秒数
返回值：方块长度
'''
def timeToBlock(time):
    global ticks_per_beat,tempo#将每拍为多少time与拍数设为公共变量
    beat = time / ticks_per_beat#计算当前音符为多少拍
    s = tempo * beat / 1000000#将拍数与拍频相除获得秒速
    if s % 0.1 >= 0.05 :
        s = s // 0.1 + 1
    elif s % 0.1 < 0.05:
        s = s // 0.1
    return int(s)

'''
函数：将方块长转换为放方块坐标
需要提交：方块长度，是否在上一个音符位置，上一个音符位置在哪
返回值：坐标
'''
def blockLongToXyz(blockLong,inSameLoc,sameLocLong):
    xyz = [1,0,1]
    if inSameLoc == True:
        xyz[0] = sameLocLong +1
    xyz[1] = blockLong % 255
    xyz[2] = blockLong // 255 +1
    return xyz

'''
函数：将音调转化为方块
输入值：音调
返回值：方块id，特殊值
'''
def noteToBlock(note):
    global block,df
    if note>108:
        note = note -((note-109)//12+1)*12
    if note < 36:
        b,dn=block[0],note%16
        return b,dn
    b = block[(note-36)//16]
    dn = (note-36) %16
    if b == "_glazed_terracotta":
        b = f"{df[(note-4)%16]}{b}"
        dn = 0
    return b,dn

'''
函数：将信息转换为str指令
需要提交：当前音符的音调
返回值：str指令
'''
def infoToCommand(note):
    global xyz
    bd = noteToBlock(note)
    command = f'setblock ~{xyz[0]} {xyz[1]} ~{xyz[2]} {bd[0]} {bd[1]}'
    return command

'''
函数：写入函数
需要提交：要输入的指令
'''
def writeFunction(command):
    global functionName
    file=open(f"\Function\{functionName}.mcfunction","a")
    file.write(f"{command}\n")
    file.close()


'''
函数：选择文件
让用户自行选择midi文件
返回值：midi文件名
'''
def chooseMidi():
    n=0
    midiFile={}
    for filename in os.listdir(r'\Midi'):
        midiFile[n]=filename
        print(f"{n}:{filename}")
        n += 1
    print("请选择midi文件（打名字前的序号）:",end="")
    while True:
        try:
            midiRight=True
            midNmae= midiFile[int(input())]
        except KeyError:
            midiRight=False
            print("请输入一个正确的值")
        except ValueError:
            midiRight = False
            print("请输入一个正确的值")
        if midiRight == True:
            break
    return midNmae

print('''欢迎使用midi转command工具
By：Mr Creeper''')
midiName=chooseMidi()
print(f"你选择的是{midiName}\n请输入生成的Function文件名（无需打后缀）：",end='')
functionName = str(input())
f=open(f"\{functionName}.mcfunction","w")#将function替换掉
f.close()
mid = MidiFile(f"\Midi\{midiName}")
ticks_per_beat = mid.ticks_per_beat#获取每拍为多少time
musicLong = mid.length
#print(mid.ticks_per_beat)
while time < 2:
    for i, track in enumerate(mid.tracks):
        #print('Track {}: {}'.format(i, track.name))#遍历midi上的音符
        for msg in track:
            #print(msg,msg.type)
            if msg.type == "note_on":#当为播放音符时，加上时间并转换为方块长度
                lastTime += msg.time
                blockLong = timeToBlock(lastTime)
                if blockLong == b1:#当方块长度与上一个相同时，方块在同一位置改为True，同位置长度+1
                    detect[0] = True
                    detect[1] += 1
                else:#当不在同一位置时，全部重置
                    detect = [False,0]
                b1 = blockLong#存储方块长度用于检测下一个音符是否位于同一个长度上
                #print(blockLong)
                xyz = blockLongToXyz(blockLong,detect[0],detect[1])#获取方块坐标
                #print(msg.note,xyz,infoToCommand(msg.note))
                command = infoToCommand(msg.note)
                if xyz[0] > xyzMax[0]:
                    xyzMax[0] = xyz[0]
                elif xyz[2] > xyzMax[2]:
                    xyzMax[2] = xyz[2]
                #if "_glazed_terracotta" in command:
                #print(msg.note,xyz,infoToCommand(msg.note))
                if time == 1:
                    writeFunction(infoToCommand(msg.note))
                    #print(msg.note,xyz,infoToCommand(msg.note))
                #typeCommand(command)
                #lastTime = 0

            elif msg.type == "note_off" or msg.type == "control_change":#当为停止音符时，只加上时间
                lastTime += msg.time
            elif msg.type == "set_tempo":#当为拍数时，获取拍数信息
                tempo = msg.tempo
    time +=1
    lastTime=0
    detect = [False, 0]
    if time == 1:
        writeFunction(f"fill ~1 1 ~1 ~{xyzMax[0]} 254 ~{xyzMax[2]} wool")
        writeFunction(f"fill ~1 255 ~1 ~{xyzMax[0]} 255 ~{xyzMax[2]-1} wool 1")
        writeFunction(f"fill ~1 255 ~{xyzMax[2]} ~{xyzMax[0]} 255 ~{xyzMax[2]} wool 2")
