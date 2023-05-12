import os
import sys
import requests
import urllib.parse
import logging
from Misc.MTConfigIni import GMTConfig
from Misc import MTLogUtils
from Misc import MTProcessUtils
import time


def CheckHeartBeat(host:str)->bool:
    logging.info('CheckHeartBeat() .................................................')
    params = urllib.parse.urlencode({'msg': 'heartbeat'})
    url = f'{host}/Echo?%s' % params
    try:
        rsp = requests.get(url, verify=False)
    except Exception as e:
        logging.error('CheckHeartBeat() Exception: %s', str(e))
        return False
    pass
    return True


def RestartApp(app_path:str):
    app_path = app_path.replace('\\','/')
    app_name = os.path.basename(app_path)
    MTProcessUtils.KillProcesses(app_name)
    MTProcessUtils.ExecuteCommandInNewConsole([app_path])
    




if __name__ == '__main__':
    MTLogUtils.InitLoggerAuto(__file__)
    
    cmdpath = sys.argv[0]
    cmdpath = os.path.realpath(cmdpath)
    basedir = os.path.dirname(cmdpath)
    if basedir == '':
        basedir = os.curdir
    pass
    basedir = basedir.replace('\\','/')
    GMTConfig.Load(basedir + "/ChatGPTMidServer.ini")

    # ssl
    ssl = GMTConfig.GetItemValue("Default", "ssl")
    bUseSSL = True if ssl == '1' else False
    logging.info("bUseSSL = %s", bUseSSL)

    # port
    port = GMTConfig.GetItemValueInt("Default", "port")
    if port == 0 : 
        if bUseSSL: port = 443
        else: port = 80
    pass    
    
    # host
    if bUseSSL:
        host = 'https://127.0.0.1:' + str(port)
    else:
        host = 'http://127.0.0.1:' + str(port)
    pass
    logging.info("host = %s", host)

    # watchdog
    watch_interval = GMTConfig.GetItemValueInt("Watchdog", 'interval')
    watch_app_path = GMTConfig.GetItemValue("Watchdog", 'app_path')
    app_full_path = basedir + watch_app_path
    logging.info("watch_interval = %s", watch_interval)
    logging.info("watch_app_path = %s", app_full_path)

    
    while(True):
        if CheckHeartBeat(host) == False:
            RestartApp(app_full_path)
        pass
        time.sleep(watch_interval)
    pass
    