# coding=gbk
import time
import threading
import random

TOP = 6
BOTTOM = 1
STATE = {0: "��ͣ����", 1: "��ͣ����", 2: "��������", 3: "�����½�"}
DIR = {0: "����", 1: "����"}
# ��Ϣ���룺0 00���� ��01 ����, 02 ���˽�
#           1 11ȥ1L ��12ȥ2L��13ȥ��¥��14ȥ4¥��15ȥ��¥��16ȥ��¥
#           2 21һ¥���˰��ϣ�22��¥���˰��ϣ�23��¥���˰��ϣ�24��¥���˰��ϣ�25��¥���˰���
#           3 32��¥���˰��£�33��¥���˰��£�34��¥���˰��£�35��¥���˰��£�36��¥���˰���

msgLock = threading.Lock()  # ��Ϣ��
exitLock = threading.Lock()  # ��������

responseInterval = 0.3  # ��Ӧ���0.3��
exitTime = 1.5  # ������ʱ��


class Msg:
    msgDecode = [["����", "����", "���˽�"], "ȥ{}¥", "{}¥���˰���", "{}¥���˰���"]  # ��Ϣ�����

    def __init__(self, type_, value):
        self.type = type_
        self.value = value
        if type_ == 0:
            self.info = self.msgDecode[0][value]
        else:
            self.info = self.msgDecode[type_].format(value)


class Exit:
    exitDecode = {0: "������", 1: "������", 2: "������", 3: "��״̬"}

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
            if msgQueue[:] == target[:]:  # ���û�иı�������
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
        print("������Ϣ:", m.info)
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
        # ��ʼ������״̬��¥��ͷ���
        state, new_state = 0, 0
        cur, new_cur = 1, 1
        d, new_d = 0, 0
        timeout = 3  # ��ʱ3��
        print("��ǰ״̬:%s,��ǰ¥��:%d,���з���%s" % (STATE[state], cur, DIR[d]))
        while True:
            time.sleep(responseInterval)  # ������Ӧ���ΪresponseInterval��
            if (state, cur, d) != (new_state, new_cur, new_d):  # ��������ı�,���Ʋ���ӡ״̬
                state, cur, d = new_state, new_cur, new_d
                print("��ǰ״̬:%s,��ǰ¥��:%d,���з���%s" % (STATE[state], cur, DIR[d]))
            else:
                print("............")

            if state == 0:  # ��ͣ����,�������ڿ���ʱ
                if exitFlag.value == 3:  # �����Ŷ����в����㳬ʱ
                    timeout -= responseInterval  # ��ʱ��ȥresponseInterval��
                tmp_list = msgQueue[:]
                for m in msgQueue:
                    if m.type == 0:  # ��0����Ϣ
                        tmp_list.remove(m)  # �������߶�ʮһ���Ƴ�
                        if m.value == 0:  # ������Ϣ
                            new_state = 1  # ������״̬Ϊ��ͣ���ţ������
                            self.closeDoor()
                            timeout = 3
                            break
                        else:  # ����״̬��  ���˰����Ż����˽�
                            timeout = 3
                    if m.value == cur:  # ����״̬�����������水���������ͬ����İ�ť
                        if (d == 1 and m.type == 2) or (d == 2 and m.type == 3):
                            tmp_list.remove(m)
                            timeout = 3
                update_msgQueue("=", tmp_list)
                if timeout <= 0:
                    print("��ʱ")
                    new_state = 1
                    self.closeDoor()

            elif state == 1:  # ��ͣ���ţ� �������ڹ���ʱ
                tmp_list = msgQueue[:]
                for m in msgQueue:
                    if m.type == 0:
                        tmp_list.remove(m)
                        if m.value:  # ���ǹ�����Ϣ
                            new_state = 0
                            self.openDoor()
                            timeout = 3
                            break
                    if m.value == cur:  # ����״̬�����������水���������ͬ����İ�ť
                        if (d == 1 and m.type == 2) or (d == 2 and m.type == 3):
                            tmp_list.remove(m)
                            new_state = 0
                            self.openDoor()
                            timeout = 3
                            break
                        if m.type == 1:  # ����ǰ��ֱ���Ƴ�
                            tmp_list.remove(m)

                update_msgQueue("=", tmp_list)

                if new_state == 1 and exitFlag.value == 3:  # ��ͣ������״̬��������
                    timeout = 3  # ���ó�ʱʱ��
                    new_state, new_cur, new_d = self.closed(state, cur, d)

            else:  # �����������½�
                if state == 2:
                    new_cur, new_d = self.up(cur, d)
                else:
                    new_cur, new_d = self.down(cur, d)

                tmp_list = msgQueue[:]  # ����������������½��ڼ��0��ָ��
                for m in msgQueue:
                    if m.type == 0:
                        tmp_list.remove(m)
                update_msgQueue("=", tmp_list)

                new_state = 1  # ����¥����Զ����ţ�����һ������ָ��
                m = Msg(0, 1)
                update_msgQueue("append", m)

    def closed(self, state, cur, d):


        if d == 1:  # ����
            if self.startup(cur, d):  # ���������
                state = 2  # ����״̬Ϊ����
            else:  # ��������
                d = 0  # ���Ըı���ݷ���
                if self.startup(cur, d):  # �������
                    state = 3  # �����½�
                else:
                    d = 1  # �ָ�d
        else:  # ����
            if self.startup(cur, d): # �������
                state = 3  # ����״̬����
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
            print("����ǰ����%d��..." % cur)
            time.sleep(2)
        print("�����{}��".format(cur))
        return cur, d

    def down(self, cur, d):
        while not self.stop(cur, d):
            cur -= 1
            print("����ǰ����%d��..." % cur)
            time.sleep(2)
        print("�����{}��".format(cur))
        return cur, d

    def startup(self, cur, d):

        global msgQueue
        is_start = False
        has_same_d = False
        tmp_list = msgQueue[:]
        for m in msgQueue:
            if m.type != 0:
                if d == 1 and m.value > cur:  # ���ϣ���0������Ϣ��¥����ڵ�ǰ¥��
                    has_same_d = True
                    is_start = True
                if d == 0 and m.value < cur:  # ���£���0������Ϣ��¥��С�ڵ�ǰ¥��
                    has_same_d = True
                    is_start = True
        if not has_same_d:  # ���û��ͬ������Ϣ����ֻҪ�е�ǰ�����Ϣ����ʹ����ݷ����෴���ӵ�
            for m in msgQueue:
                if m.type and m.value == cur:
                    tmp_list.remove(m)
        update_msgQueue("=", tmp_list)
        return is_start

    def stop(self, cur, d):

        global msgQueue
        is_stop = False  # ����ֵ�Ƿ�ͣ��
        has_same_d = False  # �Ƿ������������з�����ͬ������Ϣ
        tmp_list = msgQueue[:]
        if d == 1:  # ����
            if cur == TOP:
                is_stop = True
            for m in msgQueue:  # �Ƴ�����Ϣ�����ﵱǰ����й���Ϣ
                if m.type == 1 or m.type == 2:  # �����ڵĵ��ﵱǰ���Ƴ�, ������ĵ�ǰ�������Ƴ�
                    has_same_d = True  # ����ͬ������Ϣ
                    if m.value == cur:
                        is_stop = True
                        tmp_list.remove(m)
        else:  # �½�
            if cur == BOTTOM:
                is_stop = True
            for m in msgQueue:
                if m.type == 1 or m.type == 3:  # �����ڵĵ��ﵱǰ���Ƴ�,������ĵ�ǰ�������Ƴ�
                    has_same_d = True
                    if m.value == cur:
                        is_stop = True
                        tmp_list.remove(m)
        if not has_same_d:   # ���û��ͬ������Ϣ����ֻҪ�е�ǰ�����Ϣ����ʹ����ݷ����෴Ҳͣ����, ��ֹ�����ܹ�ͷ
            for m in msgQueue:
                if m.type and m.value == cur:
                    is_stop = True
                    tmp_list.remove(m)
        update_msgQueue("=", tmp_list)
        return is_stop

    def closeDoor(self):
        global exitFlag
        if exitFlag.value == 0:  # ����Ѿ��ڹ���״̬�������������߳�
            return
        t = threading.Thread(target=closeThread)  # �����������߳�
        t.start()

    def openDoor(self):
        global exitFlag
        if exitFlag.value == 1 or exitFlag.value == 2:  # ����Ѿ��ڿ���״̬�������������߳�
            return
        t = threading.Thread(target=openThread)  # �����������߳�
        t.start()


def openThread():

    global exitFlag, exitTime
    print("���ڿ���...")
    update_exitFlag(1)  # ����Ϊ������
    counter = exitTime
    while counter > 0:
        if exitFlag.value != 1 and exitFlag.value != 2:  # ����һ�������̴߳��
            print("������ֹ")
            exitTime = counter #��Ϳ��ϣ�������ʱ�����ѻ���ʱ��
            return
        if exitLock.acquire():
            time.sleep(responseInterval)
            exitLock.release()
        counter -= responseInterval
    # �ɹ�����
    print("�ѿ���...")
    update_exitFlag(3)
    exitTime = 1.5


def closeThread():

    global exitFlag, exitTime
    print("���ڹ���...")
    update_exitFlag(0)  # ����Ϊ������
    counter = exitTime
    while counter > 0:
        if exitFlag.value != 0:  # ����һ�������̸߳ı�
            print("������ֹ")
            exitTime = counter
            return
        if exitLock.acquire():
            time.sleep(responseInterval)
            exitLock.release()
        counter -= responseInterval
    # �ɹ�����
    print("�ѹ���")
    update_exitFlag(3)
    exitTime = 1.5


if __name__ == "__main__":

    thread1 = threading.Thread(target=msgFunction)
    thread2 = StateThreed()
    thread1.start()
    thread2.start()

