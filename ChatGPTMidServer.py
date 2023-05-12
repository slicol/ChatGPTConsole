import logging
import os
import sys
import time
import openai
import requests
from datetime import datetime
import Misc.MTFileUtils as MTFileUtils
import Misc.MTStringUtils as MTStringUtils
from flask import Flask, request,make_response
from flask_cors import CORS  # 引入CORS
from Misc.MTConfigIni import GMTConfig
import urllib.parse
from flask import abort
from flask import render_template
from Misc import MTLogUtils

app = Flask(__name__)
CORS(app)  # 设置CORS

class ChatSession:
    Key = ''
    RawKey = ''
    IpAddr = ''
    UserName = ''
    CreateTime = datetime.now()
    LastActiveTime = datetime.now()
    ContextMessages = []
    ContextSize = 10
    
    def __init__(self) -> None:
        self.Key = ''
        self.RawKey = ''
        self.IpAddr = ''
        self.UserName = ''
        self.CreateTime = datetime.now()
        self.LastActiveTime = datetime.now()
        self.ContextMessages = []
        self.ContextSize = 10
        pass


    def AddUserMessage(self, msgstr:str):
        onemsg = {"role": "user", "content": msgstr}
        self.ContextMessages.append(onemsg)

        pass


    def AddRspMessage(self, role:str, msgstr:str):
        onemsg = {"role": role, "content": msgstr}
        self.ContextMessages.append(onemsg)
        pass
        

    def LoopMessage(self):
        oldmsgcnt = len(self.ContextMessages)
        if oldmsgcnt > self.ContextSize:
            #logging.info("Now MessageNum: %d", oldmsgcnt)
            #logging.info("Max MessageNum: %d", self.ContextSize)
            newqueue = []
            for i in range(oldmsgcnt - self.ContextSize, oldmsgcnt):
                newqueue.append(self.ContextMessages[i])
            pass
            self.ContextMessages = newqueue
        pass

    def __str__(self) -> str:
        return f'Key:{self.Key},UserName:{self.UserName},IpAddr:{self.IpAddr}'
        pass


class ChatSessionManager:
    AllSessions = dict()
    Debug = False

    def __init__(self) -> None:
        self.AllSessions = dict()
        self.Debug = False        
        pass

    def GetSession(self, key:str)->ChatSession:
        result = self.AllSessions.get(key)
        if result != None:
            result.LastActiveTime = datetime.now()
        pass
        return result

    def CreateSession(self, ipaddr:str, username:str)->ChatSession:
        result = ChatSession()
        result.IpAddr = ipaddr
        result.UserName = username
        result.CreateTime = datetime.now()
        timestr = result.CreateTime.strftime("%Y-%m-%d_%H-%M-%S")
        index = len(self.AllSessions)
        result.RawKey = f"Chat.{username}.{timestr}.{index}"
        result.Key = MTStringUtils.Base64StringEncode(result.RawKey)
        self.AllSessions[result.Key] = result

        logstr = ""
        logstr += "===================================================================\n"
        logstr += f"Session.IpAddr = {result.IpAddr}\n"
        logstr += f"Session.UserName = {result.UserName}\n"
        logstr += f"Session.CreateTime = {result.CreateTime}\n"
        logstr += f"Session.Key = {result.Key}\n"
        logstr += "===================================================================\n"

        logging.info("CreateSession() \n%s", logstr)

        return result




def ChatAPI(session:ChatSession, usermsg:str)->str:
    session.AddUserMessage(usermsg)
    rspmsg = {"role":'bot','content':''}
    try:
        logging.info('ChatAPI() usermsg = %s', usermsg)
        response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=session.ContextMessages)
        rspmsg = response.choices[0].message
    except Exception as e:
        logging.error('ChatAPI() error = %s', e)
        return str(e)
    pass
    session.AddRspMessage(rspmsg.role, rspmsg.content)
    session.LoopMessage()
    logging.info('ChatAPI() response success!')
    return rspmsg.content



def ChatDebug(session:ChatSession, usermsg:str)->str:
    logging.info(f"ChatDebug() [{session.IpAddr}][{session.Key}][{session.UserName}]: {usermsg}")
    
    session.AddUserMessage(usermsg)
    session.AddRspMessage('rspmsg.role', 'rspmsg.content')
    session.LoopMessage()
    
    if chatmgr.Debug:
        dbgmsg = MTFileUtils.ReadTextUtf8Sig('./DebugMessage.txt')
        return 'this is debug mode! you say:' + usermsg + ". <br> debug message:" + dbgmsg
    else:
        return 'api_key is empty!'
    pass


def GetErrorReturn(key:str, errstr:str)->str:
    return '{"key":"' + key + '", "error":"' + errstr + '"}'

def GetNormalReturn(key:str, role:str, content:str)->str:
    return "{" + f'"key":"{key}", "role":"{role}", "content":"{content}"' + "}"



def FetchFile(path:str, url:str)->str:
    logging.info("-------------------------------------------------------------------")    
    logging.info("FetchFile() %s -> %s ", url, path)
    try:
        rsp = requests.get(url, verify=False)
        if rsp.content != None:
            text = rsp.content.decode()
            
            f = open(path, 'wb')
            f.write(rsp.content)
            f.close()
            
            logging.info("FetchFile() Success, bytes = %d", len(text))
            return text
        pass
    except Exception as e:
        logging.error("FetchFile() Execption:\n %s",str(e))
        logging.info("-------------------------------------------------------------------")        
    pass
    return ''

#############################################################################
class WebCache:
    ChatGPTWeb = ''
    pki_validation_file = ''
    RobotsFile = ''
    WebIndexCache = {}

    def WebIndex(subpath:str)->str:
        result = WebCache.WebIndexCache.get(subpath)
        if result == None or chatmgr.Debug:
            path = './Web/' + subpath
            path = os.path.realpath(path)
            if os.path.exists(path):
                result = MTFileUtils.ReadText(path)
                WebCache.WebIndexCache[subpath] = result
            else:
                result = None
            pass
        pass
        return result

    def GetRobotsFile(bForceRefresh:bool = False)->str:
        if WebCache.RobotsFile == '' or bForceRefresh or chatmgr.Debug:
            path = './Web/robots.txt'
            path = os.path.realpath(path)
            WebCache.RobotsFile = MTFileUtils.ReadText(path)
        pass
        return WebCache.RobotsFile

    def GetChatGPTWeb(bForceRefresh:bool = False)->str:
        if WebCache.ChatGPTWeb == '' or bForceRefresh or chatmgr.Debug:
            path = './Web/ChatGPTWeb.html'
            path = os.path.realpath(path)
            WebCache.ChatGPTWeb = MTFileUtils.ReadText(path)
        pass
        return WebCache.ChatGPTWeb   

    def SyncCOS()->str:
        cos_url = GMTConfig.GetItemValue("WebMap", "ChatGPTWeb")
        data = FetchFile('./Web/ChatGPTWeb.html', cos_url)
        if data != '': 
            WebCache.ChatGPTWeb = data
        pass
        return "SyncCOS Okay!"

    pass

#############################################################################

@app.route('/robots.txt')
def Web_Robots():
    return WebCache.GetRobotsFile()    

@app.route('/')
def Web_Index():
    return WebCache.GetChatGPTWeb()

@app.errorhandler(404)
def not_found_error(error):
    return WebCache.WebIndex('404.html')
    
@app.route('/web/<path:subpath>')
def Web_WebIndex(subpath:str):
    result = WebCache.WebIndex(subpath)
    if result == None: 
        return abort(404)
    pass
    if subpath.endswith('.js'):
        response = make_response(result)
        response.headers['Content-Type'] = 'text/javascript'
        return response
    pass
    return result

@app.route('/BunnyGPT')
def Web_BunnyGPT():
    return WebCache.GetChatGPTWeb()

@app.route('/SyncCOS')
def Web_SyncCOS():
    return WebCache.SyncCOS()

#############################################################################
@app.route('/Echo', methods=['GET'])
def Api_Echo():
    return request.args

#############################################################################
@app.route('/yousay_webapi', methods=['GET'])
def YouSay_WebAPI():
    key = request.args.get('key')
    usr = request.args.get('usr')
    msg = request.args.get('msg')

    if usr == None or usr == '': return GetErrorReturn(key, "UserName is Empty")
    if msg == None or msg == '': return GetErrorReturn(key, "Message is Empty")

    session = chatmgr.GetSession(key)
    if session == None:
        ipaddr = request.remote_addr
        session = chatmgr.CreateSession(ipaddr,usr)
    pass

    if chatmgr.Debug or openai.api_key == '':
        rspmsg = ChatDebug(session, msg)
    else:
        rspmsg = ChatAPI(session, msg)
    pass

    rspmsg = urllib.parse.quote(rspmsg)
    rspmsg = MTStringUtils.Base64StringEncode(rspmsg)
    return GetNormalReturn(session.Key, "bot", rspmsg)



@app.route('/yousay', methods=['GET'])
def YouSay():
    key = request.args.get('key')
    usr = request.args.get('usr')
    msg = request.args.get('msg')

    if usr == None or usr == '': return GetErrorReturn(key, "UserName is Empty")
    if msg == None or msg == '': return GetErrorReturn(key, "Message is Empty")

    session = chatmgr.GetSession(key)
    if session == None:
        ipaddr = request.remote_addr
        try:
            usr = MTStringUtils.Base64StringDecode(usr)
        except Exception:
            return GetErrorReturn(key, "UserName is Invalid")
        pass
        session = chatmgr.CreateSession(ipaddr,usr)
    pass

    try:
        msg = MTStringUtils.Base64StringDecode(msg)
    except Exception:
        return GetErrorReturn(session.Key, "Message is Invalid")
    pass

    if chatmgr.Debug or openai.api_key == '':
        rspmsg = ChatDebug(session, msg)
    else:
        rspmsg = ChatAPI(session, msg)
    pass

    rspmsg = MTStringUtils.Base64StringEncode(rspmsg)
    return GetNormalReturn(session.Key, "bot", rspmsg)
    
#############################################################################
chatmgr = ChatSessionManager()
if __name__ == '__main__':
    MTLogUtils.InitLoggerAuto(__file__)

    cmdpath = sys.argv[0]
    basedir = os.path.dirname(cmdpath)
    if basedir == '':
        basedir = os.curdir
    pass

    GMTConfig.Load(basedir + "/ChatGPTMidServer.ini")
    # debug
    debug = GMTConfig.GetItemValue("Default", "debug")
    chatmgr.Debug = True if debug == '1' else False
    logging.info("Debug = %s", chatmgr.Debug)

    # api_key
    openai.api_key = GMTConfig.GetItemValue("Default", "api_key")
    if openai.api_key == '':
        logging.info('api_key is empty')
    pass

    # ssl
    ssl = GMTConfig.GetItemValue("Default", "ssl")
    bUseSSL = True if ssl == '1' else False
    logging.info("bUseSSL = %s", bUseSSL)

    # port
    port = GMTConfig.GetItemValue("Default", "port")
    if port == '' : 
        if bUseSSL: port = '443'
        else: port = '80'    
    pass    
    port = int(port)

    ssl_crt = GMTConfig.GetItemValue("Default", "ssl_crt")
    ssl_key = GMTConfig.GetItemValue("Default", "ssl_key")
    logging.info("SSL-Crt = %s", ssl_crt)
    logging.info("SSL-Key = %s", ssl_key)

    # run
    if bUseSSL:
        ssl_context = (basedir + ssl_crt, basedir + ssl_key)
        app.run(host='0.0.0.0', port=port, ssl_context=ssl_context)
    else:
        app.run(host='0.0.0.0', port=port)
    pass

    pass
    