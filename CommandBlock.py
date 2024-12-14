import mido
import nbtlib 
import os
import shutil

def chooseMidi():
    n=0
    midiFile={}
    for filename in os.listdir(r'Midi'):
        midiFile[n]=filename
        print(f"{n}:{filename}")
        n += 1
    print("请选择midi文件（打名字前的序号）:",end="")
    while True:
        midiRight = False
        try:
            midiRight=True
            midName= midiFile[int(input())]
        except KeyError:
            midiRight=False
            print("请输入一个正确的值")
        except ValueError:
            midiRight = False
            print("请输入一个正确的值")
        if midiRight == True:
            print(f"你选择了{midName}")
            break
    return midName

def parse_midi_file(file_path:str):
    '''
    传入midi文件路径后传回播放音符列表
    [(playsound音调值,tick数,秒数)]
    '''

    # 打开 MIDI 文件
    mid = mido.MidiFile(file_path)
    current_time = float(0)
    tempo = 500000
    seconds_per_time = tempo/mid.ticks_per_beat/1000000

    notes = []

    # 遍历所有 MIDI 事件
    for track in mid.tracks:
        for msg in track:
            # 如果是 Note On 事件
            if msg.type == 'note_on':
                #print(msg)
                # 计算音符播放的 tick
                tick = int(current_time*18)
                current_time += msg.time * seconds_per_time

                # 计算音符的音调值
                note_value = 2 ** ((msg.note - 66) / 12)

                # 将 tick 和音调数据值添加到列表中
                #print((tick, note_value))
                notes.append((note_value,tick))
            elif msg.type == "set_tempo":
                current_time += msg.time * seconds_per_time
                tempo = msg.tempo
                seconds_per_time = tempo/mid.ticks_per_beat/1000000
            else :
                current_time += msg.time * seconds_per_time
    return notes

def noteToCommand(note:tuple):
    playsound = f"execute @e[scores={'{'}music={note[1]},musiclist={score}{'}'}] ~~~ playsound note.harp @s ~~~ 255 {note[0]}"
    return playsound

def getIndex():
    '''
    获取放置命令方块位置的数据
    '''
    global CBN
    num = CBN
    CBN += 1
    if num % 200 < 100:
        return [num,0]
    else:
        fol = num % 100
        lev = num // 100
        return [(((fol-50)*-1)+49)+lev*100,2]

def generate_progress_bar(progress):
    completed_blocks = int(progress * 30)
    remaining_blocks = 30 - completed_blocks

    progress_bar = "§e" + "▏" * completed_blocks + "§r" + "▏" * remaining_blocks

    return progress_bar

def pad_zero(number):
    if number < 10:
        return "0" + str(number)
    else:
        return str(number)

def setCommand(command,cond,delay):
    info = getIndex()
    ind = info[1]
    if CBN % 100 == 0:
        ind = 1
    if cond == 1:
        ind += 4
    file["structure"]["block_indices"][0][info[0]] = nbtlib.Int(ind)
    file["structure"]["palette"]["default"]["block_position_data"][str(info[0])] = nbtlib.Compound({"block_entity_data":nbtlib.Compound({
        "Command":nbtlib.String(command),
        "x" : nbtlib.Int(0),
        "y" : nbtlib.Int(info[0]//100),
        "z" : nbtlib.Int(info[0]%100),
        "conditionMet" : nbtlib.Byte(abs(cond-1)),
        "conditionalMode" : nbtlib.Byte(cond),
        "TickDelay" : nbtlib.Int(delay),
        "CustomName":nbtlib.String(""),
        "ExecuteOnFirstTick":nbtlib.Byte(0),
        "LPCondionalMode":nbtlib.Byte(0),
        "LPRedstoneMode":nbtlib.Byte(0),
        "LPRedstoneMode":nbtlib.Int(2),
        "LastExecution":nbtlib.Long(0),
        "LastOutput":nbtlib.String(""),
        "LastOutputParams":nbtlib.List([]),
        "SuccessCount" : nbtlib.Int(1),
        "Version" : nbtlib.Int(19),
        "TrackOutput":nbtlib.Byte(1),
        "auto":nbtlib.Byte(1),
        "isMovable":nbtlib.Byte(1),
        "powered":nbtlib.Byte(0),
        "id":nbtlib.String("CommandBlock"),
    })})

def main():
    global filePath,file,cmd,CBN,score
    notes = parse_midi_file(f"Midi\{chooseMidi()}")
    takeFile = nbtlib.load("b.mcstructure",byteorder="little")#b.mcstructure as a template
    fn = input("请输入要生成的mcstructure文件名（无需打后缀）")
    fileName = fn + ".mcstructure"
    musicName = input("请输入音乐名")
    score = input("请输入分数")
    filePath = f"McStructure\{fileName}"
    shutil.copyfile("a.mcstructure", filePath)
    file = nbtlib.load(filePath,byteorder="little")
    file["structure"]["block_indices"][0] = nbtlib.List([nbtlib.Int(3) for _ in range(10000)])
    file["structure"]["block_indices"][1] = nbtlib.List([nbtlib.Int(-1) for _ in range(10000)])
    file.save()
    cmd = takeFile["structure"]["palette"]["default"]["block_position_data"][str(0)]
    lateTick = 0
    for index in range(len(notes)):
        note = list(notes[index])
        note[1] += 1145140000 #114514 to cope with the filter in NetEase Minecraft
        detick = note[1] - lateTick
        if detick > 0:
            setCommand(f'execute @e[scores={"{"}music={lateTick}..{note[1]},musiclist={score}{"}"}] ~~~ scoreboard players set @s music {note[1]}',0,0)
        setCommand(noteToCommand(note),1,detick)
        lateTick = note[1]
    file.save()
    lcrName = fn + "LCR.mcstructure"
    filePath = f"McStructure\{lcrName}"
    shutil.copyfile("a.mcstructure", filePath)
    file = nbtlib.load(filePath,byteorder="little")
    file["structure"]["block_indices"][0] = nbtlib.List([nbtlib.Int(3) for _ in range(10000)])
    file["structure"]["block_indices"][1] = nbtlib.List([nbtlib.Int(-1) for _ in range(10000)])
    file.save()
    CBN = 0
    endTime = notes[-1][1] //18
    for time in range(endTime):
        time +=1
        cmdStr = f'''execute @e[tag=mt,scores={'{'}music={time*18+1145140000}..{(time+1)*18+1145140000},musiclist={score}{'}'}] ~~~ title @s actionbar
§r    §6正在播放:§3{musicName}
§r{time//60}:{pad_zero(time%60)} {generate_progress_bar((time)/endTime)} {endTime//60}:{pad_zero(endTime%60)}
    '''
        setCommand(cmdStr,0,0)
        file.save()

CBN = 0

if __name__ == "__main__":
    main()
