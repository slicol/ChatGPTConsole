# ChatGPTConsole
ChatGPT的控制台代码和中转服务器代码

## ChatGPTConsole

负责实现一个基于控制台的交互窗口。有2种运行模式（在ChatGPTConsole.ini里配置）：
1. 直接模式（direct=1），用于已经翻墙的环境。只要配置好APIKey，就可以直接与OpenAI官方服务器交互。
2. 中转模式（direct=0），用于无法翻墙的环境。需要配置一个`中转服务器`(host=x.x.x.x:port)，通过中转服务器间接地与OpenAI官方服务器交互。

所有通过ChatGPTConsole交互的对话内容，都会写入本地目录下的日志文件中，以备有需要时进行回顾。

## ChatGPTGUI

负责实现一个基于QT的GUI版本。
与ChatGPTConsole共用配置文件：ChatGPTConsole.ini

## ChatGPTMidServer
负责实现上述所说的`中转服务器`，基于Flask框架实现，功能简单，代码可读。还实现了简单的Session机制，可以持续与ChatGPT交互的上下文。只需要在ChatGPTMidServer.ini里配置APIKey，即可开箱即用。

## ChatGPTMidServerWatchdog
负责实现中转服的监控，因为我们的逻辑可能有Bug，会造成中转服无法正常工作，Watchdog负责监控中转服是否正常工作，否则会强制重启中转服。在实际测试中，已经持续工作一个月，没有感觉到服务中断。

## Web/ChatGPTWeb.html
负责提供一个Web化的交互页面，可以方便在手机上打开使用。其中Web页面中使用的Host还是我的个人Host，如果自己部署，需要替换为自已的Host。

## Package.bate
用来将上述4个程序打包为Exe，以便可以独立发布。


## 最后
感谢 feat 大佬帮我将ChatGPTGUI开了一个头。
