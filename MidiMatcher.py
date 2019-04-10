

class MidiMatcher:
    # 完整输入: Midi, Window
    # Midi为原谱midi序列
    # window为手机当前屏幕的五线谱对应的midi位置，为一个二元数组(start, end)
    def __init__(self, midi, window):
        self.midi = midi
        self.window = window
        self.record = [] # 一开始录音序列是空
        self.mapResult = []
        self.playLine = -1
        self.buffer = [] # buffer存储的音符总长度固定为一个小节，这样可以让过长停顿清空buffer
        self.bufferLength = 0
        self.bufferSize = 8

    # 输入一个note的接口
    def input(self, note):
        self.updateBuffer(note)
        self.match()
        self.updateWindow()

    def updateBuffer(self, note):
        if note[0]==0 and note[1]>self.bufferSize:
            self.buffer = []
        else:
            if self.bufferLength > self.bufferSize:
                self.bufferLength -= self.buffer[0][1]
                self.buffer.pop(0)
            self.buffer.append(note)
            self.bufferLength += note[1]
        print('buffer:',self.buffer)

    def match(self):
        # 匹配需要在window内，所以在移动播放线的同时需要更新window
        curMidiWindow = self.midi[self.window[0]:self.window[1]]
        # if self.playLine!=-1:
        #     curMidiWindow = self.midi[max(self.playLine-self.bufferSize/2,self.window[0]):min(self.playLine+self.bufferSize/2, self.window[1])]
        # 分为两种情况：候选集已经唯一和候选集还不唯一的情况
        minCost = 0xffffffff
        minIndex = -1
        resList = []
        cost = 0
        # print(self.window[0], int(self.window[1]-1.2*len(self.buffer)))
        for pointer in range(self.window[0], int(self.window[1]-1.2*len(self.buffer))):
            # print('midi:',self.midi[pointer : int(pointer+1.25*len(self.buffer))])
            cost, maplist = self.accurateMatch(self.midi[pointer : int(pointer+1.25*len(self.buffer))], self.buffer)
            # print('cost:', cost, 'maplist:', maplist)
            if resList==[]:
                minCost = cost
                resList = maplist
                continue
            if cost<minCost:
                minCost = cost
                minIndex = pointer
                resList = maplist
        # 然后就可以更新匹配列表和播放线
        # print('minCost:', minCost)
        # print('resList:', resList)
        self.mapResult.append(resList)
        if resList!=[]:
            self.playLine = resList[-1][0][2]+1 # note应该带有第三个属性，就是位置

    def accurateMatch(self, sheet, record):
        # print('accurateMatch:', sheet, record)
        return self.DPMatch(sheet, record)

    def DPMatch(self, sheet, record):
        # print('DPMatch:', sheet, record)
        if sheet==[]:
            if record==[]:
                return 0, []
            else:
                s = 0
                for r in record:
                    s += r[1]*10
                return s, []
        elif record==[]:
            return 0, []
        else:
            costOfMatch = self.matchCost(sheet[0], record[0])
            costOfLoss = record[0][1] * 2
            DPcost1, DPlist1 = self.DPMatch(sheet[1:], record[1:])
            DPcost2, DPlist2 = self.DPMatch(sheet, record[1:])
            # 1: 匹配i和j，i和j一定被匹配
            if 0.6 <= sheet[0][1] / record[0][1] <=1.6:
                cost1, list1 = DPcost1, DPlist1 # 第一种情况：i完全匹配j
            elif sheet[0][1] > record[0][1]:
                cost1, list1 = self.DPMatch(self.minusNote(sheet,record[0]), record[1:])  # 第二种情况：部分i匹配j
            else:
                cost1, list1 = self.DPMatch(sheet[1:], self.minusRecordNote(record,sheet[0]))  # 第二种情况：i匹配部分j
            cost1 += costOfMatch
            # 2: 不匹配i，并且继续匹配j
            cost2, list2 = self.DPMatch(sheet[1:], record)
            # 3: 不匹配i，也不匹配j
            cost3, list3 = costOfLoss+DPcost1, DPlist1
            # 4: 匹配i，但不匹配j
            cost4, list4 = costOfLoss+DPcost2, DPlist2

            minCost = min(cost1, cost2, cost3, cost4)
            if minCost==cost1:
                reslist = [(sheet[0],record[0])] + list1
            elif minCost==cost2:
                reslist = list2
            elif minCost==cost3:
                reslist = list3
            else:
                reslist = list4
            return minCost, reslist

    # 去除匹配的note
    def minusNote(self, sw, r):
        # print('minusNote:', sw, r)
        l = [(sw[0][0], sw[0][1] - r[1], sw[0][2])]
        l.extend(sw[1:])
        return l

    def minusRecordNote(self, sw, r):
        # print('minusNote:', sw, r)
        l = [(sw[0][0], sw[0][1] - r[1])]
        l.extend(sw[1:])
        return l

    def lossCost(self, note):
        # print('lossCost:', note)
        return note[1]

    def matchCost(self, s, r):
        # print('MatchCost:', s, r)
        return (2 ** abs(s[0] - r[0])) * (abs(s[1] - r[1]) + 1)  # 音高之差+1乘以2的长度之差次方

    def updateWindow(self):
        if self.playLine > (self.window[0]+self.window[1])/2:
            self.window = (int(0.75*self.window[0]+0.25*self.window[1]), int(-0.25*self.window[0]+1.25*self.window[1]))


sheet = [(9,2,1),(16,8,2),(14,3,3),(16,3,4),(19,2,5),(16,3,6),(14,3,7),(12,1,8),(14,1,9),(9,6,10),(12,1,11),(11,1,12),(12,6,13),(11,1,14),(9,1,15),(9,3,16),(11,3,17),(9,2,18),(9,2,19),(12,10,20)]
window = (0, 10)
mm = MidiMatcher(sheet, window)
record = [(7,1),(16,10),(14,4),(16,4),(17,1),(19,1),(16,4),(14,4),(11,1),(14,1),(7,1),(9,6),(12,1),(11,1),(12,6),(11,2),(9,3),(11,4),(9,4),(9,2),(12,12)]
# record = [(9,2),(16,8),(14,3),(16,3),(19,2),(16,3,6),(14,3,7),(12,1,8),(14,1,9),(9,6,10),(12,1,11),(11,1,12),(12,6,13),(11,1,14),(9,1,15),(9,3,16),(11,3,17),(9,2,18),(9,2,19),(12,10,20)]
for r in record:
    input(r)
    mm.input(r)
    print(mm.mapResult[-1])


