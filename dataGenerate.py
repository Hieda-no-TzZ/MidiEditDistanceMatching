# 第一个是相对音高，指从低音1的半音数；第二个是相对长度，是与八分音符的比值
#         (6)   3      2      3      5      3      2      1      2      (6)   1      (7)    1      (7)   (6)   (6)   (7)    (6)   (6)    1
sheet = [(9,2),(16,8),(14,3),(16,3),(19,2),(16,3),(14,3),(12,1),(14,1),(9,6),(12,1),(11,1),(12,6),(11,1),(9,1),(9,3),(11,3),(9,2),(9,2),(12,10)]
sheet10 = [(9,2),(16,8),(14,3),(16,3),(19,2),(16,3),(14,3),(12,1),(14,1),(9,6),(12,1)]
#
record = [(7,1),(16,10),(14,4),(16,4),(17,1),(19,1),(16,4),(14,4),(11,1),(14,1),(7,1),(9,6),(12,1),(11,1),(12,6),(11,2),(9,3),(11,4),(9,4),(9,2),(12,12)]
record10 = [(14,4),(16,4),(17,1),(19,1),(16,4),(14,4),(14,1)]
UnMatchedWeight = 100 # 未匹配的权重

def match(pointer, sheet, window):
    sheetWindow = sheet[pointer, pointer + 8]
    print(sheetWindow, window)
    m = len(sheetWindow) # 8
    n = len(window) # 4
    cost, matchList = iterCost(sheetWindow, window)

def iterCost(sw, rw):
    if len(sw)==0: # 如果有未匹配的，需要给以较大权重
        return lengthOfNotes(rw) * UnMatchedWeight, []
    elif len(rw)==0: # 如果全都匹配完，则没有损失
        return 0, []
    else:
        [cost, matchList1] = iterCost(minusNote(sw, rw[0]), rw[1:]) # 这里应该返回cost加上match列表
        tmplist = [(sw[0],rw[0])]
        tmplist.extend(matchList1)
        match1cost = matchCost(sw[0], rw[0]) + cost
        [nonmatchcost, matchList2] = iterCost(sw[1:], rw[0:])
        if match1cost > nonmatchcost:
            return nonmatchcost, matchList2
        else:
            return match1cost, tmplist

def lengthOfNotes(notes):
    if len(notes)==0:
        return 0
    s = 0
    for n in notes:
        s += n[1]
    return s

def matchCost(s, r):
    return (2**abs(s[0]-r[0])) * (abs(s[1]-r[1])+1) # 音高之差+1乘以2的长度之差次方

# 去除匹配的note
def minusNote(sw, r):
    if sw[0][1] < 1.5 * r[1]:
        return sw[1:]
    else:
        l = [(sw[0][0], sw[0][1]-r[1])]
        l.extend(sw[1:])
        return l
import time
s = time.time()
print(iterCost(sheet10, record10))
e = time.time()
print(e-s)
# window = []
# pointer = 0
# for r in record:
#     window.append(r)
#     if len(window)<4:
#         continue
#     elif len(window)>4:
#         window.pop(0)
#     pointer = match(pointer, sheet, window)

