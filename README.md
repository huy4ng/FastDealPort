# FastDealPort
To deal a large number of ports fastly and detect the http service 

当我们在面对大量ip时，需要快速进行端口扫描，识别开放的服务。同时，在web渗透中需要识别http服务进行web测试，因此快速且如何尽可能多的获取http服务成为设计这一脚本的初衷。

需要用到masscan：

apt install masscan

脚本很简单，流程如下：

1.先使用subprocess执行masscan进行端口扫描，这里支持从文件倒入ip和直接输入ip段进行扫描，指定了2000的rate进行扫描，使用者根据需要可以进行修改，并将扫描结果以xml格式输出。

2.处理输出的xml文件，取出其中的ip和端口进行http和https的探测，并且针对不同的状态码进行分类，输出到对应的文件中。

使用方式：

从文本导入ip：

python FastDealPorts.py -i ips.txt -o ports.xml -t 10 

直接输入IP段:

python FastDealPorts.py -p 192.168.1.1/16 -o ports.xml -t 10

