import os
import signal
import subprocess
import psutil
import logging


def FindAllPIDs(name:str)->list:
    pids = []
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] == name:
            pid = proc.info['pid']
            pids.append(pid)
        pass
    pass
    return pids


def FindFirstPID(name:str)->int:
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] == name:
            pid = proc.info['pid']
            return int(pid)
        pass
    pass
    return 0


def KillProcesses(name:str)->int:
    pids = FindAllPIDs(name)
    for pid in pids:
        logging.info('KillProcesses() pid = %d', pid)
        os.kill(pid, signal.SIGTERM)
    pass
    return len(pids)


def ExecuteCommandInNewConsole(cmdline:list)->str:
    logging.info("ExecuteCommandInNewConsole() cmdline = %s", cmdline)
    result = ''
    try:
        CREATE_NEW_CONSOLE = 0x00000010
        result = subprocess.Popen(cmdline, creationflags=CREATE_NEW_CONSOLE)
        logging.info("ExecuteCommandInNewConsole() result = %s", result)
    except Exception as e:
        logging.error('ExecuteCommandInNewConsole() Exception: %s', str(e))
    pass
    return str(result)
