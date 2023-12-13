import datetime
import logging
import socket
import sys

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from bottle import route, response, request, static_file, hook
import threading
import webbrowser
import re
import json
from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

import argparse
parser = argparse.ArgumentParser(description='Wenda config')
parser.add_argument('-c', type=str, dest="Config",
                    default='config.yml', help="配置文件")
parser.add_argument('-p', type=int, dest="Port", help="使用端口号")
parser.add_argument('-l', type=bool, dest="Logging", help="是否开启日志")
parser.add_argument('-t', type=str, dest="LLM_Type", help="选择使用的大模型")
args = parser.parse_args()


class dotdict(dict):
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


def object_hook(dict1):
    for key, value in dict1.items():
        if isinstance(value, dict):
            dict1[key] = dotdict(value)
        else:
            dict1[key] = value
    return dotdict(dict1)


green = "\033[1;32m"
red = "\033[1;31m"
white = "\033[1;37m"


def error_helper(e, doc_url):
    error_print(e)
    error_print("查看：", doc_url)
    # webbrowser.open_new(doc_url)


import threading
print_lock = threading.Lock()

def join_string(content):
    s = ""
    for e in content:
        s += str(e)
    return s

logger = logging.getLogger("wenda_log")


def AddFileHandler(m_logger):
    # 获取当前的年月日时分秒
    now = datetime.datetime.now()
    # 格式化文件名
    filename = "./log/log_{}_{}_{}_{}_{}_{}.txt".format(now.year, now.month, now.day, now.hour, now.minute, now.second)
    # 设置日志器的输出级别
    m_logger.setLevel(logging.INFO)
    # 创建文件处理器对象
    file_handler = logging.FileHandler(filename, encoding="utf-8")
    # 设置文件处理器的输出级别
    file_handler.setLevel(logging.INFO)
    # 设置文件处理器的输出格式
    file_fmt = "%(asctime)s - %(filename)s [line:%(lineno)d] - %(levelname)s: %(message)s"
    formatter = logging.Formatter(file_fmt)
    file_handler.setFormatter(formatter)
    # 将文件处理器添加到日志器对象中
    m_logger.addHandler(file_handler)

def AddConsoleHandler(m_logger):
    # 创建StreamHandler对象，用于输出到控制台
    console_handler = logging.StreamHandler(sys.stdout)
    # 设置StreamHandler的日志级别
    console_handler.setLevel(logging.DEBUG)
    # 设置StreamHandler的日志格式
    console_fmt = "%(levelname)s: %(message)s"
    formatter = logging.Formatter(console_fmt)
    console_handler.setFormatter(formatter)
    # 将FileHandler和StreamHandler添加到Logger对象中
    m_logger.addHandler(console_handler)

def printx(*content,end="\n"):
    now = datetime.datetime.now()
    # str_t = now.strftime("%Y-%m-%d %H:%M:%S")
    # s = f"[{str_t}]{join_string(content)}{white}"
    s = f"{join_string(content)}{white}"
    with print_lock:
        logger.info(s)

AddConsoleHandler(logger)

def error_print(*s):
    printx(f"{red}{join_string(s)}")

def success_print(*s):
    printx(f"{green}{join_string(s)}")


wenda_Config = args.Config
wenda_Port = str(args.Port)
wenda_Logging = str(args.Logging)
wenda_LLM_Type = str(args.LLM_Type)
print(args)
try:
    stream = open(wenda_Config, encoding='utf8')
except:
    error_print('加载配置失败，改为加载默认配置')
    stream = open('example.config.yml', encoding='utf8')
settings = load(stream, Loader=Loader)
settings = dotdict(settings)
stream.close()
if wenda_Port != 'None':
    settings.port = wenda_Port
if wenda_Logging != 'None':
    settings.logging = wenda_Logging
if wenda_LLM_Type != 'None':
    settings.llm_type = wenda_LLM_Type
try:
    settings.llm = settings.llm_models[settings.llm_type]
except:
    error_print("没有读取到LLM参数，可能是因为当前模型为API调用。")
del settings.llm_models


settings_str_toprint = dump(dict(settings))
settings_str_toprint = re.sub(r':', ":"+"\033[1;32m", settings_str_toprint)
settings_str_toprint = re.sub(r'\n', "\n\033[1;31m", settings_str_toprint)
printx(settings_str_toprint)

settings_str = json.dumps(settings)
settings = json.loads(settings_str, object_hook=object_hook)
if(settings.logging):
    AddFileHandler(logger)


def print_cuda_state():
    import torch
    from cpm_kernels.library import cuda, cudart
    if torch.cuda.is_available():
        printx("CUDA is available")
        try:
            current_device = torch.cuda.current_device()
            printx(f"Current CUDA device index: {current_device}")
            printx(f"PyTorch version: {torch.__version__}")
            printx(f"CUDA available: {torch.cuda.is_available()}")
            printx(f"CUDA version: {torch.version.cuda}")
            printx(f"cuDNN version: {torch.backends.cudnn.version()}")
            printx(
                f"device memory: {torch.cuda.get_device_properties(0).total_memory / 1073741824:.2f}GB(target: {1.4e+10 / 1073741824:.2f}GB)")
            torch.cuda.init()
            torch.cuda.set_device(current_device)
            cudart.cudaSetDevice(current_device)
            curr_device = cudart.cudaGetDevice()

            printx(f"cudart curr_device: {curr_device}")
        except Exception as e:
            printx(f"CUDA device index not found: {str(e)}")
            import traceback
            traceback.print_exc()
    else:
        printx("CUDA is not available")


def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.settimeout(1)
            s.connect(("localhost", port))
            return True
        except (socket.timeout, ConnectionRefusedError):
            # 如果连接失败，说明端口未被占用
            return False

printx(f"{settings.port}端口是否被占用:{is_port_in_use(settings.port)}");

class CounterLock:
    def __init__(self):
        self.lock = threading.Lock()
        self.waiting_threads = 0
        self.waiting_threads_lock = threading.Lock()

    def acquire(self):
        with self.waiting_threads_lock:
            self.waiting_threads += 1
        acquired = self.lock.acquire()

    def release(self):
        self.lock.release()
        with self.waiting_threads_lock:
            self.waiting_threads -= 1

    def get_waiting_threads(self):
        with self.waiting_threads_lock:
            return self.waiting_threads

    def __enter__(self):  # 实现 __enter__() 方法，用于在 with 语句的开始获取锁
        self.acquire()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):  # 实现 __exit__() 方法，用于在 with 语句的结束释放锁
        self.release()


def allowCROS():
    response.set_header('Access-Control-Allow-Origin', '*')
    response.add_header('Access-Control-Allow-Methods', 'POST,OPTIONS')
    response.add_header('Access-Control-Allow-Headers',
                        'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token')


app = FastAPI(title="Wenda",
              description="Wenda API",
              version="1.0.0",
              # docs_url=None,
              # redoc_url=None,
              openapi_url="/api/v1/openapi.json",
              docs_url="/api/v1/docs",
              redoc_url="/api/v1/redoc")
