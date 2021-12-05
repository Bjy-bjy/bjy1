# coding=gbk
import time
import threading
import random

TOP = 6
BOTTOM = 1
STATE = {0: "门停开着", 1: "门停关着", 2: "电梯上升", 3: "电梯下降"}
DIR = {0: "向下", 1: "向上"}
# 消息编码：0 00关门 ，01 开门, 02 有人进
#           1 11去1L ，12去2L，13去三楼，14去4楼，15去五楼，16去六楼
#           2 21一楼有人按上，22二楼有人按上，23三楼有人按上，24四楼有人按上，25五楼有人按上
#           3 32二楼有人按下，33三楼有人按下，34四楼有人按下，35五楼有人按下，36六楼有人按下

msgLock = threading.Lock()  # 消息锁
exitLock = threading.Lock()  # 开关门锁

responseInterval = 0.3  # 响应间隔0.3秒
exitTime = 1.5  # 开关门时间


class Msg:
    msgDecode = [["关门", "开门", "有人进"], "去{}楼", "{}楼有人按上", "{}楼有人按下"]  # 消息解码表

    def __init__(self, type_, value):
        self.type = type_
        self.value = value
        if type_ == 0:
            self.info = self.msgDecode[0][value]
        else:
            self.info = self.msgDecode[type_].format(value)


class Exit:
    exitDecode = {0: "关门中", 1: "开门中", 2: "开门中", 3: "无状态"}

    def __init__(self, value):
        self.value = value
        self.info = self.exitDecode[value]


exitFlag = Exit(3)
msgQueue = []


def printMsg(name, queue):

    if type(queue) is list:
        info = [m.info for m in queue]
    else:
        info = queue.info
    print(" "*50 + name+": "+str(info))


def update_msgQueue(action, target):

    global msgQueue, msgLock
    if msgLock.acquire():
        if action == "=":
            if msgQueue[:] == target[:]:  # 如果没有改变则跳过
                msgLock.release()
                return
            msgQueue = target
        else:
            eval("msgQueue."+action)(target)
        printMsg("msgQueue",msgQueue)
        msgLock.release()


def update_exitFlag(target):

    global exitFlag, exitLock
    if exitLock.acquire():
        exitFlag = Exit(target)
        printMsg("exitFlag", exitFlag)
        exitLock.release()


def msgFunction():

    global msgQueue
    for i in range(4):
        type = random.randint(0, 3)
        value = 0
        if type == 0:
            value = random.randint(0, 2)
        if type == 2:
            value = random.randint(BOTTOM, TOP-1)
        if type == 3:
            value = random.randint(BOTTOM+1, TOP)
        if type == 1:
            value = random.randint(BOTTOM, TOP)

        TIME = random.randint(1, 8)
        m = Msg(type, value)
        print("产生消息:", m.info)
        exist = False
        for each in msgQueue:
            if m.type == each.type and m.value == each.value:
                exist = True
                break
        if not exist:
            update_msgQueue("append",m)
        time.sleep(TIME)


class StateThreed(threading.Thread):

    def run(self):
        global msgQueue, exitFlag
        # 初始化电梯状态、楼层和方向
        state, new_state = 0, 0
        cur, new_cur = 1, 1
        d, new_d = 0, 0
        timeout = 3  # 超时3秒
        print("当前状态:%s,当前楼层:%d,运行方向：%s" % (STATE[state], cur, DIR[d]))
        while True:
            time.sleep(responseInterval)  # 动作响应间隔为responseInterval秒
            if (state, cur, d) != (new_state, new_cur, new_d):  # 如果发生改变,则复制并打印状态
                state, cur, d = new_state, new_cur, new_d
                print("当前状态:%s,当前楼层:%d,运行方向：%s" % (STATE[state], cur, DIR[d]))
            else:
                print("............")

            if state == 0:  # 门停开着,包括正在开门时
                if exitFlag.value == 3:  # 开关门动作中不计算超时
                    timeout -= responseInterval  # 超时减去responseInterval秒
                tmp_list = msgQueue[:]
                for m in msgQueue:
                    if m.type == 0:  # 有0类消息
                        tmp_list.remove(m)  # 不管三七二十一先移除
                        if m.value == 0:  # 关门消息
                            new_state = 1  # 先设置状态为门停关着，后关门
                            self.closeDoor()
                            timeout = 3
                            break
                        else:  # 开门状态下  有人按开门或有人进
                            timeout = 3
                    if m.value == cur:  # 开门状态下有人在外面按与电梯运行同方向的按钮
                        if (d == 1 and m.type == 2) or (d == 2 and m.type == 3):
                            tmp_list.remove(m)
                            timeout = 3
                update_msgQueue("=", tmp_list)
                if timeout <= 0:
                    print("超时")
                    new_state = 1
                    self.closeDoor()

            elif state == 1:  # 门停关着， 包括正在关门时
                tmp_list = msgQueue[:]
                for m in msgQueue:
                    if m.type == 0:
                        tmp_list.remove(m)
                        if m.value:  # 不是关门消息
                            new_state = 0
                            self.openDoor()
                            timeout = 3
                            break
                    if m.value == cur:  # 关门状态下有人在外面按与电梯运行同方向的按钮
                        if (d == 1 and m.type == 2) or (d == 2 and m.type == 3):
                            tmp_list.remove(m)
                            new_state = 0
                            self.openDoor()
                            timeout = 3
                            break
                        if m.type == 1:  # 到当前层直接移除
                            tmp_list.remove(m)

                update_msgQueue("=", tmp_list)

                if new_state == 1 and exitFlag.value == 3:  # 门停关着无状态才能启动
                    timeout = 3  # 重置超时时间
                    new_state, new_cur, new_d = self.closed(state, cur, d)

            else:  # 电梯上升或下降
                if state == 2:
                    new_cur, new_d = self.up(cur, d)
                else:
                    new_cur, new_d = self.down(cur, d)

                tmp_list = msgQueue[:]  # 清除掉电梯上升或下降期间的0类指令
                for m in msgQueue:
                    if m.type == 0:
                        tmp_list.remove(m)
                update_msgQueue("=", tmp_list)

                new_state = 1  # 到达楼层后自动开门，加入一个开门指令
                m = Msg(0, 1)
                update_msgQueue("append", m)

    def closed(self, state, cur, d):


        if d == 1:  # 向上
            if self.startup(cur, d):  # 如果启动，
                state = 2  # 电梯状态为上升
            else:  # 不能启动
                d = 0  # 尝试改变电梯方向
                if self.startup(cur, d):  # 如果启动
                    state = 3  # 电梯下降
                else:
                    d = 1  # 恢复d
        else:  # 向下
            if self.startup(cur, d): # 如果启动
                state = 3  # 电梯状态上升
            else:
                d = 1
                if self.startup(cur, d):
                    state = 2
                else:
                    d = 0
        return state, cur, d

    def up(self, cur, d):
        while not self.stop(cur, d):
            cur += 1
            print("正在前往第%d层..." % cur)
            time.sleep(2)
        print("到达第{}层".format(cur))
        return cur, d

    def down(self, cur, d):
        while not self.stop(cur, d):
            cur -= 1
            print("正在前往第%d层..." % cur)
            time.sleep(2)
        print("到达第{}层".format(cur))
        return cur, d

    def startup(self, cur, d):

        global msgQueue
        is_start = False
        has_same_d = False
        tmp_list = msgQueue[:]
        for m in msgQueue:
            if m.type != 0:
                if d == 1 and m.value > cur:  # 向上，非0类型消息，楼层大于当前楼层
                    has_same_d = True
                    is_start = True
                if d == 0 and m.value < cur:  # 向下，非0类型消息，楼层小于当前楼层
                    has_same_d = True
                    is_start = True
        if not has_same_d:  # 如果没有同方向消息，则只要有当前层的消息，即使与电梯方向相反都扔掉
            for m in msgQueue:
                if m.type and m.value == cur:
                    tmp_list.remove(m)
        update_msgQueue("=", tmp_list)
        return is_start

    def stop(self, cur, d):

        global msgQueue
        is_stop = False  # 返回值是否停下
        has_same_d = False  # 是否存在与电梯运行方向相同方向消息
        tmp_list = msgQueue[:]
        if d == 1:  # 上升
            if cur == TOP:
                is_stop = True
            for m in msgQueue:  # 移除掉消息队列里当前层的有关消息
                if m.type == 1 or m.type == 2:  # 电梯内的到达当前层移除, 电梯外的当前层向上移除
                    has_same_d = True  # 存在同方向消息
                    if m.value == cur:
                        is_stop = True
                        tmp_list.remove(m)
        else:  # 下降
            if cur == BOTTOM:
                is_stop = True
            for m in msgQueue:
                if m.type == 1 or m.type == 3:  # 电梯内的到达当前层移除,电梯外的当前层向下移除
                    has_same_d = True
                    if m.value == cur:
                        is_stop = True
                        tmp_list.remove(m)
        if not has_same_d:   # 如果没有同方向消息，则只要有当前层的消息，即使与电梯方向相反也停下来, 防止电梯跑过头
            for m in msgQueue:
                if m.type and m.value == cur:
                    is_stop = True
                    tmp_list.remove(m)
        update_msgQueue("=", tmp_list)
        return is_stop

    def closeDoor(self):
        global exitFlag
        if exitFlag.value == 0:  # 如果已经在关门状态则不启动关门子线程
            return
        t = threading.Thread(target=closeThread)  # 启动关门子线程
        t.start()

    def openDoor(self):
        global exitFlag
        if exitFlag.value == 1 or exitFlag.value == 2:  # 如果已经在开门状态则不启动开门子线程
            return
        t = threading.Thread(target=openThread)  # 启动开门子线程
        t.start()


def openThread():

    global exitFlag, exitTime
    print("正在开门...")
    update_exitFlag(1)  # 更新为开门中
    counter = exitTime
    while counter > 0:
        if exitFlag.value != 1 and exitFlag.value != 2:  # 被另一个开门线程打断
            print("开门终止")
            exitTime = counter #中涂打断，开关门时间变成已花费时间
            return
        if exitLock.acquire():
            time.sleep(responseInterval)
            exitLock.release()
        counter -= responseInterval
    # 成功开门
    print("已开门...")
    update_exitFlag(3)
    exitTime = 1.5


def closeThread():

    global exitFlag, exitTime
    print("正在关门...")
    update_exitFlag(0)  # 更新为关门中
    counter = exitTime
    while counter > 0:
        if exitFlag.value != 0:  # 被另一个开门线程改变
            print("关门终止")
            exitTime = counter
            return
        if exitLock.acquire():
            time.sleep(responseInterval)
            exitLock.release()
        counter -= responseInterval
    # 成功关门
    print("已关门")
    update_exitFlag(3)
    exitTime = 1.5


if __name__ == "__main__":

    thread1 = threading.Thread(target=msgFunction)
    thread2 = StateThreed()
    thread1.start()
    thread2.start()

