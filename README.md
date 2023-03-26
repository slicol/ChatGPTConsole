# ChatGPTConsole
ChatGPT的控制台代码和中转服务器代码

## ChatGPTConsole

负责实现一个基于控制台的交互窗口。有2种运行模式（在ChatGPTConsole.ini里配置）：
1. 直接模式（direct=1），用于已经翻墙的环境。只要配置好APIKey，就可以直接与OpenAI官方服务器交互。
2. 中转模式（direct=0），用于无法翻墙的环境。需要配置一个`中转服务器`(host=x.x.x.x:port)，通过中转服务器间接地与OpenAI官方服务器交互。

所有通过ChatGPTConsole交互的对话内容，都会写入本地目录下的日志文件中，以备有需要时进行回顾。

## ChatGPTMidServer
负责实现上述所说的`中转服务器`，基于Flask框架实现，功能简单，代码可读。还实现了简单的Session机制，可以持续与ChatGPT交互的上下文。只需要在ChatGPTMidServer.ini里配置APIKey，即可开箱即用。

所有通过ChatGPTMidServer生产的对话内容，都会写入服务器日志中，以备有需要时进行回顾。

## Package.bate
用来将上述2个程序打包为Exe，以便可以独立发布。


## 最后
求哪位大佬看到了，能够帮忙做一个GUI。
