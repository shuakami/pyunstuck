import threading
import time
import socket
import os

class DeadlockScenario:
    """死锁场景"""
    def __init__(self):
        self.lock1 = threading.Lock()
        self.lock2 = threading.Lock()
        
    def run(self):
        t1 = threading.Thread(target=self._thread1)
        t2 = threading.Thread(target=self._thread2)
        
        t1.start()
        t2.start()
        
    def _thread1(self):
        with self.lock1:
            print("线程1获取了锁1")
            time.sleep(1)  # 确保死锁发生
            print("线程1正在等待锁2...")
            with self.lock2:
                print("这行永远不会执行")
                
    def _thread2(self):
        with self.lock2:
            print("线程2获取了锁2")
            time.sleep(1)  # 确保死锁发生
            print("线程2正在等待锁1...")
            with self.lock1:
                print("这行永远不会执行")

class IOBlockScenario:
    """I/O阻塞场景"""
    def __init__(self):
        self.server_socket = None
        
    def run(self):
        # 创建一个永远不会有连接的服务器socket
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(('localhost', 0))  # 随机端口
        self.server_socket.listen(1)
        
        print(f"等待连接在端口 {self.server_socket.getsockname()[1]}...")
        # 这里会永远阻塞
        connection, address = self.server_socket.accept()

class ResourceCompetitionScenario:
    """资源竞争场景"""
    def __init__(self):
        self.resource_lock = threading.Lock()
        self.resource_count = 0
        
    def run(self):
        threads = []
        for i in range(10):
            t = threading.Thread(target=self._compete_for_resource)
            threads.append(t)
            t.start()
            
    def _compete_for_resource(self):
        while True:
            with self.resource_lock:
                self.resource_count += 1
                time.sleep(0.1)  # 模拟处理时间
                self.resource_count -= 1

def main():
    print("请选择要测试的场景：")
    print("1. 死锁场景")
    print("2. I/O阻塞场景")
    print("3. 资源竞争场景")
    
    choice = input("请输入数字(1-3): ").strip()
    
    if choice == '1':
        print("\n启动死锁场景...")
        scenario = DeadlockScenario()
        scenario.run()
    elif choice == '2':
        print("\n启动I/O阻塞场景...")
        scenario = IOBlockScenario()
        scenario.run()
    elif choice == '3':
        print("\n启动资源竞争场景...")
        scenario = ResourceCompetitionScenario()
        scenario.run()
    else:
        print("无效的选择")
        return
        
    # 保持主线程运行
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n检测到Ctrl+C，但由于场景设计，可能无法正常退出...")

if __name__ == "__main__":
    main() 