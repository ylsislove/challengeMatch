import time
import threading

class Main:

    def __init__(self):
        self.my_list = []
        self.my_list2 = []

    def haoshi(self, _list, _list2):
        for i in _list:
            print(i)
        for i in _list2:
            print(i)

    def test(self):
        self.my_list.append("111")
        self.my_list.append("222")
        self.my_list.append("333")
        self.my_list.append("444")
        self.my_list.append("555")
        self.my_list.append("666")
        self.my_list.append("777")
        self.my_list.append("888")
        self.my_list.append("999")
        self.my_list2.append("1111")
        self.my_list2.append("2221")
        self.my_list2.append("3331")
        self.my_list2.append("4441")
        self.my_list2.append("5551")
        self.my_list2.append("6661")
        self.my_list2.append("7771")
        self.my_list2.append("8881")
        self.my_list2.append("9991")
        list1 = self.my_list
        list2 = self.my_list2
        # threading.Thread(target=self.haoshi, args=(list1, list2)).start()
        threading.Thread(target=self.haoshi, args=(self.my_list, self.my_list2)).start()
        # self.my_list.clear()
        # self.my_list2.clear()
        self.my_list = []
        self.my_list2 = []
        print("hhhhhhhhhhhhhhhhhhhhhhhhhhhhhh")


if __name__ == '__main__':
    test = Main()
    for i in range(3):
        test.test()
        time.sleep(3)
        print("----------------------------")
