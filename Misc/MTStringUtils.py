# Copyright 1998-2022 Tencent Games, Inc. All Rights Reserved.
#                            
# 一些常用的String处理函数
#@Slicol

import base64
import os
import sys

########################################################################
def TrimBracketContentRight(s:str, l:str, r:str, once:bool = False)->tuple:
    stack = 0
    pos_l = -1
    pos_r = -1
    for i in range(len(s)-1, 0, -1):
        t = s[i]
        if l != r:
            if t == r:
                if(pos_r == -1):
                    pos_r = i
                pass
                stack += 1
            elif t == l:
                stack -= 1
                if stack == 0:
                    pos_l = i
                    break
                pass
            pass
        else:
            if t == r:
                if stack == 0:
                    stack = 1
                    pos_r = i
                else:
                    stack = 0
                    pos_l = i
                    break
                pass
            pass
        pass
    pass

    if pos_l >= 0 and pos_r >= 0:
        d = s[pos_l: pos_r + 1]
        s = s[0:pos_l] + s[pos_r + 1:]
        if once == True:
            return (s,d)
        else:
            return TrimBracketContentRight(s, l, r, once)
        pass
    else:
        return (s, "")
    pass

########################################################################
def TrimQuotationMarks(s:str, l:str, r:str)->str:
    s = s.strip()
    if s.startswith(l) and s.endswith(r):
        s = s[1:len(s)-1]
    pass
    return s

########################################################################
def StringEndswith(str, suffix):
    if isinstance(suffix,list):
        for tmp in suffix:
            if str.endswith(tmp):
                return True
            pass
        pass
    else:
        return str.endswith(suffix)
    pass
    return False


########################################################################
def TrimSingleLineComment(line:str)->str:
    pos = line.find("//")
    if pos >= 0: line = line[0:pos]
    return line

def Base64StringEncode(rawstr:str)->str:
    if rawstr == None or rawstr == '': return ''
    return base64.b64encode(rawstr.encode("utf-8")).decode("utf-8")

def Base64StringDecode(base64str:str)->str:
    if base64str == None or base64str == '': return ''
    return base64.b64decode(base64str.encode("utf-8")).decode("utf-8")


