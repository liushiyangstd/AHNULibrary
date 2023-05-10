# AHNU座位预约脚本
> 使用Python完成图书馆自动预约座位（安徽师范大学（花津校区）敬文图书馆)
> **2023年5月10日完成。**

### 特别说明
1. 项目在此项目的基础上开发```  https://github.com/yangchnet/AHNUReserve  ```
2. 具体变化
> * 修改邮箱推送为微信推送
> * 增加了预约楼层，具体增加了图书馆2楼，图书馆3、4楼公共空间的座位（以前只可预约3、4楼的部分位置）
> * 修改了当该预约位置冲突时，无法预约下一个位置的BUG，本项目如果所预约位置与他人有冲突，会自动预约编号的下一个位置
> * 请注意上文的编号不是nskxxxx的编号，而是座位信息在传输中的编号，由于图书馆座位编号有些小小的混乱，所以可能会让预约位置和设置位置离得比较远，请在微信中及时查看

### 项目文件说明
* Reserve.py 主要程序
* SeatReservationINFO.json 座位信息配置程序
* WEIXIN.json 微信推送配置
* startup.bat 批处理文件，执行程序


### 所需Python的库
一般应该都有安装, 可用```  pip list  ```进行查看
* requests
* json
* smtplib
* datetime
* wxpusher（用于微信推送）
* logging

### 服务器部署
**根据我自己的实践，在window系统上可以执行。但在腾讯云Linux服务器上执行代码，无法连接到座位预约系统，但用此代码访问百度等网站都可以，具体原因未知（猜测是服务器设置了某些东西，但我自己没有测试）**

### 解决办法
1. 使用自己的window系统的电脑设置定时任务预约座位
2. 用window系统的服务器去执行定时任务，由于我的两个服务器都有项目，暂时没有机会尝试，如果有兴趣的可以尝试一下

### 使用自己的window系统的电脑设置定时任务预约座位
1. 首先使用把代码下载到你的电脑上

2. 修改```  SeatReservationINFO.json  ```的配置，该文件主要是关于预约信息的配置，根据下述指导填入你的信息（把```  xxx  ```替换为你自己的信息）
	```json
	{
        # 图书馆预约登录账号
        "account": "xxx",
        # 图书馆预约登录密码
        "password": "xxx",
        # 座位编号（例如ngg4e066）
        "sid": "xxx",
        # 预约时间（08:00 ~ 22:00 ）
        # 开始时间
        "dayst": " 14:40",
        # 结束时间
        "dayet": " 22:00"
    }
	```
3. 修改```  WEIXIN.json  ```的配置，该文件主要是关于微信推送信息的配置，根据下述指导填入你的信息（把```  xxx  ```替换为你自己的信息）
	```json
	{
        # 应用token（获取请看后文）
        "appToken": "xxx",

        # 用户UID（获取请看后文）
        "uids": [
        "xxx"
        ]
    }
	```
4. 请注意在配置完成后，删除所有#开头的行，也就是删除所有注释，因为这不符合json语法，只为提示填写哪些内容，就如下面代码段即可
	```json
	{
        "account": "xxx",
        "password": "xxx",
        "sid": "xxx",
        "dayst": " 14:40", 
        "dayet": " 22:00"
    }
	```

5. 修改批处理文件``` startup.bat ```
* 把cd后的目录换成自己电脑上对应的目录
* 此处执行所用的系统环境变量配置的python解释器，如果需要使用别的环境，请把具体执行的命令一行行写入即可
    ```bat
    cd E:\项目\图书馆座位预约\AHNUReserve-master\src
    python Reserve.py   
    ```
* 例如下面这个使用的anaconda创建的虚拟环境
     ```bat
    cd E:\项目\图书馆座位预约\AHNUReserve-master\src
    conda activate ML
    python Reserve.py
    ```
### 获取```  appToken  ```和```  uids  ```

#### 1. 创建自己的应用，获取```  appToken  ```和```  uids  ```
* 进入此[网站](https://wxpusher.dingliqc.com/docs/#/?apptokenid=%e6%b3%a8%e5%86%8c%e5%b9%b6%e4%b8%94%e5%88%9b%e5%bb%ba%e5%ba%94%e7%94%a8&id=%e6%b3%a8%e5%86%8c%e5%b9%b6%e4%b8%94%e5%88%9b%e5%bb%ba%e5%ba%94%e7%94%a8)根据指导创建应用并得到 ``` appToken```
* 微信扫码订阅应用
![本地路径](.\\img/wxpusher.png)

* 在WxPusher消息推送平台微信公众号内获取UID
![本地路径](.\\img/gongzonghao1.png)
![本地路径](.\\img/gongzonghao2.png)


#### 2. 使用我创建的应用，获取```  appToken  ```和```  uids  ```
* 关注WxPusher消息推送平台微信公众号
* 在微信中打开链接 ``` https://wxpusher.zjiecode.com/wxuser/?type=1&id=44774#/follow ```
* appToken填入```  AT_Cxj40nGcDr3fgjLe7oDlzyzE2EuITmWX  ```
* UID获取方式和前面说的一样
    

### Window上定时任务
1. 定时任务设置请根据该指导[点击](https://blog.csdn.net/xielifu/article/details/81016220)
2. ``` 关键说明 ```
> 1. 图中的程序或脚本选项选择下载文件中的``` startup.bat ```
> 2. 起始于参数是``` startup.bat ```保存的目录
3. ![本地路径](.\\img/dingshirenwu.png)


### 使用说明
1. 图书馆在晚23点到早上6点无法预约，请在设置定时任务注意开始任务的时间
2. startup.bat脚本内容可自己修改，请根据需要自己修改
3. 由于不是部署在服务器上，所以电脑需要整夜待机，这是一个问题
**有用请给个STAR，欢迎Fork**
