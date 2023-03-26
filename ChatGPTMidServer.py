import os
import sys
import openai
from datetime import datetime
import Misc.MTFileUtils as MTFileUtils
import Misc.MTStringUtils as MTStringUtils
from flask import Flask, request
from Misc.MTConfigIni import GMTConfig


app = Flask(__name__)

class ChatSession:
    Key = ''
    RawKey = ''
    IpAddr = ''
    UserName = ''
    CreateTime = datetime.now()
    LastActiveTime = datetime.now()
    ContextMessages = []
    ContextSize = 10
    LogFile = ''

    def __init__(self) -> None:
        self.Key = ''
        self.RawKey = ''
        self.IpAddr = ''
        self.UserName = ''
        self.CreateTime = datetime.now()
        self.LastActiveTime = datetime.now()
        self.ContextMessages = []
        self.ContextSize = 10
        self.LogFile = ''        
        pass


    def AddUserMessage(self, msgstr:str):
        onemsg = {"role": "user", "content": msgstr}
        self.ContextMessages.append(onemsg)

        logstr = ''
        logstr += "===================================================================\n"
        logstr += f"UserSay: {msgstr}\n"
        logstr += "-------------------------------------------------------------------\n"
        MTFileUtils.AppendText(self.LogFile, logstr)
        pass


    def AddRspMessage(self, role:str, msgstr:str):
        onemsg = {"role": role, "content": msgstr}
        self.ContextMessages.append(onemsg)

        logstr = ''
        logstr += f"ChatGPT[{role}]: {msgstr}\n"
        logstr += "-------------------------------------------------------------------\n"
        MTFileUtils.AppendText(self.LogFile, logstr)
        pass
        

    def LoopMessage(self):
        oldmsgcnt = len(self.ContextMessages)
        if oldmsgcnt > self.ContextSize:
            #print("Now MessageNum:", oldmsgcnt)
            #print("Max MessageNum:", self.ContextSize)
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
    LogDir = ''
    Debug = False

    def __init__(self) -> None:
        self.AllSessions = dict()
        self.LogDir = ''
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
        result.LogFile = self.LogDir + f"/{result.RawKey}.log"
        result.Key = MTStringUtils.Base64StringEncode(result.RawKey)
        MTFileUtils.MakeSureParentDir(result.LogFile)
        self.AllSessions[result.Key] = result

        logstr = ""
        logstr += "===================================================================\n"
        logstr += f"Session.IpAddr = {result.IpAddr}\n"
        logstr += f"Session.UserName = {result.UserName}\n"
        logstr += f"Session.CreateTime = {result.CreateTime}\n"
        logstr += f"Session.Key = {result.Key}\n"
        logstr += f"Session.LogFile = {result.LogFile}\n"
        logstr += "===================================================================\n"

        print(logstr)
        MTFileUtils.AppendText(result.LogFile, logstr)

        return result




def ChatAPI(session:ChatSession, usermsg:str)->str:
    session.AddUserMessage(usermsg)
    response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=session.ContextMessages)
    rspmsg = response.choices[0].message
    session.AddRspMessage(rspmsg.role, rspmsg.content)
    session.LoopMessage()
    return rspmsg.content



def ChatDebug(session:ChatSession, usermsg:str)->str:
    print(f"ChatDebug() [{session.IpAddr}][{session.Key}][{session.UserName}]: {usermsg}")
    
    session.AddUserMessage(usermsg)
    session.AddRspMessage('rspmsg.role', 'rspmsg.content')
    session.LoopMessage()
    
    if chatmgr.Debug:
        return 'this is debug mode!'
    else:
        return 'api_key is empty!'
    pass


def GetErrorReturn(key:str, errstr:str)->str:
    return '{"key":"' + key + '", "error":"' + errstr + '"}'

def GetNormalReturn(key:str, role:str, content:str)->str:
    return "{" + f'"key":"{key}", "role":"{role}", "content":"{content}"' + "}"




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
    

chatmgr = ChatSessionManager()
if __name__ == '__main__':
    cmdpath = sys.argv[0]
    basedir = os.path.dirname(cmdpath)
    if basedir == '':
        basedir = os.curdir
    pass

    chatmgr.LogDir = basedir + '/session'

    GMTConfig.Load(basedir + "/ChatGPTMidServer.ini")
    # debug
    debug = GMTConfig.GetItemValue("Default", "debug")
    chatmgr.Debug = True if debug == '1' else False
    print("Debug =", chatmgr.Debug)

    # api_key
    openai.api_key = GMTConfig.GetItemValue("Default", "api_key")
    if openai.api_key == '':
        print('api_key is empty')
    pass
    # port
    port = GMTConfig.GetItemValue("Default", "port")
    if port == '' : port = 4540
    else: port = int(port)

    # run
    app.run(host='0.0.0.0', port=port)

    pass
    