import json


def Decode(jstr:str, obj:any):
    jobj = json.loads(jstr)
    Dict2Object(jobj, obj)
    pass

def Dict2Object(d:dict, obj:any):
    for name in [name for name in dir(obj) if not name.startswith('_')]:
        if name not in d:
            pass
        else:
            prop = getattr(obj, name)
            prop = UpdatePropValue(prop, d[name])
            setattr(obj, name, prop)
        pass
    pass


def UpdatePropValue(prop:any, val:any):
    if str(type(prop)).__contains__('.'):
        # prop is a object of custom class
        Dict2Object(val, prop)
    elif str(type(prop)) == "<class 'list'>":
        # prop is a list
        if prop.__len__() == 0:
            # list is empty, can't confirm element type
            prop = val
        else:
            # list has elements
            elmtype = type(prop[0])
            prop.clear()
            for elmval in val:
                elmobj = elmtype()
                elmobj = UpdatePropValue(elmobj, elmval)
                prop.append(elmobj)
            pass
        pass
    else:
        prop = val
    pass
    return prop