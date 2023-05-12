from datetime import datetime
import logging
import os
import re

def InitLoggerAuto(main_file:str):
    print("MainFile:", main_file)
    main_file = main_file.replace("\\", "/")
    R_TempDir = re.compile('/Temp/.*?\.py')
    result = R_TempDir.search(main_file)
    if not result:
        basedir = os.path.dirname(os.path.realpath(main_file))
    else:
        basedir = os.getcwd()
    pass

    print("BaseDir:", basedir)
    appname = os.path.basename(main_file)
    pos = appname.rfind('.')
    if pos > 0: appname = appname[:pos]
    InitLogger(basedir, appname)

def InitLogger(basedir:str,appname:str):
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger('root')
    logger.setLevel(logging.INFO)

    # 创建一个输出到文件的handler
    curtime = datetime.now()
    timestr = curtime.strftime("%Y-%m-%d_%H-%M-%S")
    
    logdir = basedir + '/log'
    logfile = logdir + "/" + appname  + "_" + timestr + ".log"
    if not os.path.exists(logdir):
        os.makedirs(logdir)
    pass

    file_handler = logging.FileHandler(logfile, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)

    # 配置日志格式
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    pass