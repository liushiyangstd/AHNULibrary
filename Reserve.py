import requests
import json
import smtplib
import datetime
import logging
from wxpusher import WxPusher
TOMORROW = str(datetime.date.today() + datetime.timedelta(days=1))
TODAY = str(datetime.date.today())

# 请求头
header = {
    # 设定报文头
    'Host': 'libzwxt.ahnu.edu.cn',
    'Origin': 'http://libzwxt.ahnu.edu.cn',
    'Referer': 'http://libzwxt.ahnu.edu.cn/SeatWx/Seat.aspx?fid=3&sid=1438',
    # 'User-Agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36",
    'User-Agent': "Mozilla/5.0 (Linux; Android 12; M2006J10C Build/SP1A.210812.016; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/107.0.5304.141 Mobile Safari/537.36 XWEB/5061 MMWEBSDK/20230303 MMWEBID/534 MicroMessenger/8.0.34.2340(0x2800225D) WeChat/arm64 Weixin NetType/4G Language/zh_CN ABI/arm64;",
    'X-AjaxPro-Method': 'AddOrder',
    "Connection": "close",
}

INFO = {

    # 预约日期
    'atDate': TOMORROW,
    # 开始时间
    'st': "",
    # 结束时间
    'et': "",
    # 日志保存位置
    'fileloc': ''

}

# 微信推送信息
WEIXIN_INFO = {

    # summer
    'summary': '预约座位信息',
    # 座位编号
    'sid': "",
    # 座位字母编号
    'seatnames':"",
    # 座位编号对应规则
    'whichone':0
}

# 加载json文件配置
with open('SeatReservationINFO.json') as file:
    file_contents = file.read()
    info = json.loads(file_contents)
    INFO.update(info)
    # print(parsed_json)

with open('WEIXIN.json') as file:
    file_contents = file.read()
    info = json.loads(file_contents)
    WEIXIN_INFO.update(info)

# 处理开始和结束时间
# 开始时间
INFO['st'] = TOMORROW + str(INFO['dayst'])
# 结束时间
INFO['et'] = TOMORROW + str(INFO['dayet'])

class Reserve:
    def __init__(self, **kwargs):
        self.info = kwargs
        self.session = requests.Session()
        logging.basicConfig(filename=self.info['fileloc'], level=logging.DEBUG,
                            format=' %(asctime)self.session - %(levelname)self.session- %(message)self.session')

    def reserve(self):
        self.login()
        try:
            self.info['sid'],whichone = self.convert(self.info['sid'])
            # 记录对应规则
            WEIXIN_INFO['whichone'] = whichone
            if whichone == 0:
                logging.info("请输入正确的座位，只能预约2,3,4楼的自习室")
            # 开始预约
            logging.info('begin to reserve...')
            header = {
                # 设定报文头
                'Host': 'libzwxt.ahnu.edu.cn',
                'Origin': 'http://libzwxt.ahnu.edu.cn',
                'Referer': 'http://libzwxt.ahnu.edu.cn/SeatWx/Seat.aspx?fid=3&sid=1438',
                'User-Agent': "Mozilla/5.0 (Linux; Android 12; M2006J10C Build/SP1A.210812.016; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/107.0.5304.141 Mobile Safari/537.36 XWEB/5061 MMWEBSDK/20230303 MMWEBID/534 MicroMessenger/8.0.34.2340(0x2800225D) WeChat/arm64 Weixin NetType/4G Language/zh_CN ABI/arm64;",
                'X-AjaxPro-Method': 'AddOrder',
            }
            reserveUrl = 'http://libzwxt.ahnu.edu.cn/SeatWx/ajaxpro/SeatManage.Seat,SeatManage.ashx'
            reserverData = {
                'atDate': self.info['atDate'],
                'sid': self.info['sid'],
                'st': self.info['st'],
                'et': self.info['et'],
            }

            # 尝试进行预约
            reserve = self.session.post(reserveUrl, data=json.dumps(reserverData), headers=header)
            if '成功' in reserve.text:
                logging.info(reserve.text)
                logging.info('reserve successfully! Your seat id is {0}'.format(self.info['sid']))
                WEIXIN_INFO['sid'] = self.info['sid']
                winxin = WINXIN(**WEIXIN_INFO)
                winxin.send()

            while '预约成功' not in reserve.text:
                # 预约未成功，再次尝试
                reserve = self.session.post(reserveUrl, data=json.dumps(reserverData), headers=header)


                if "预约成功" in reserve.text:
                    # 预约完成
                    logging.info(reserve.text)
                    # logging.info('reserve successfully! Your seat id is {0}'.format(self.info['sid']))
                    WEIXIN_INFO['sid'] = self.info['sid']
                    winxin = WINXIN(**WEIXIN_INFO)
                    winxin.send()

                # 服务器时间不一致
                if '提前' in reserve.text:
                    logging.warning(reserve.text)
                    continue
                elif '冲突' or '重复' in reserve.text:
                    # 时间和其他人有冲突，顺延下一个座位
                    logging.warning(reserve.text)
                    logging.warning('Appointment failed, trying to reserve another seat...')
                    self.info['sid'] = str(int(self.info['sid']) + 1)
                    reserverData['sid'] = self.info['sid']
                    print(self.info['sid'])
                    continue
                elif '二次' in reserve.text:
                    logging.info(reserve.text)
                    break
                elif '成功' in reserve.text:
                    # 预约完成
                    logging.info(reserve.text)
                    # logging.info('reserve successfully! Your seat id is {0}'.format(self.info['sid']))
                    WEIXIN_INFO['sid'] = self.info['sid']
                    winxin = WINXIN(**WEIXIN_INFO)
                    winxin.send()
                    break
                else:
                    logging.info(reserve.text)
                    logging.error('未知原因，未预约成功，请检查日志及数据设置！！！')


        except BaseException as e:
            logging.error(e)

    def login(self):
        logging.info('''
                    start  with self.info['account']:{0}, self.info['password']:{1}, seatid:{2}. From {3} to {4}.'''
                     .format(self.info['account'], self.info['password'], self.info['sid'], self.info['st'],
                             self.info['et']))

        # 开始登陆
        postUrl = 'http://libzwxt.ahnu.edu.cn/SeatWx/login.aspx'
        postData = {
            '__VIEWSTATE': '/wEPDwULLTE0MTcxNzMyMjZkZAl5GTLNAO7jkaD1B+BbDzJTZe4WiME3RzNDU4obNxXE',
            '__VIEWSTATEGENERATOR': 'F2D227C8',
            '__EVENTVALIDATION': '/wEWBQK1odvtBQLyj/OQAgKXtYSMCgKM54rGBgKj48j5D4sJr7QMZnQ4zS9tzQuQ1arifvSWo1qu0EsBRnWwz6pw',
            'tbUserName': self.info['account'],
            'tbPassWord': self.info['password'],
            'Button1': '登 录',
            'hfurl': ''
        }

        login = self.session.post(postUrl, data=postData)

        if '个人中心' in login.content.decode():
            logging.info('login successfully!')

    @staticmethod
    def convert(seat_code):  # nsk3004
        sid = 0
        # 记录是哪个规则映射的
        whichone = 0
        if seat_code[:3] == 'nzr':
            sid = int(seat_code[3:]) + 437
            whichone = 1
        elif seat_code[:3] == 'nsk' and seat_code[3] == '1':
            sid = int(seat_code[3:]) + 95
            whichone = 2
        elif seat_code[:3] == 'nsk' and seat_code[3] == '3':
            sid = int(seat_code[3:]) - 2477
            whichone = 3
        elif seat_code[:3] == 'nsk' and seat_code[3] == '2':
            sid = int(seat_code[3:]) - 1177
            whichone = 4
        elif seat_code[:3] == 'nbz':
            sid = int(seat_code[3:])
            whichone = 5
        elif seat_code[:3] == 'nbk':
            sid = int(seat_code[3:])
            whichone = 6
        elif seat_code[:3] == 'ndz':
            sid = int(seat_code[3:]) + 2875
            whichone = 7
        # 三楼公共阅览室东
        elif seat_code[:5] == 'ngg3e':
            number = int(seat_code[5:])
            if number < 89:
                sid = number + 2433
                whichone = 8
            else:
                sid = number - 89 + 2682
                whichone = 9
        elif seat_code[:5] == 'ngg3w':
            number = int(seat_code[5:])
            sid = number + 2521
            whichone = 10
        elif seat_code[:5] == 'ngg4e':
            number = int(seat_code[5:])
            if number < 33:
                sid = number + 2617
                whichone = 11
            else:
                sid = number - 33 + 2754
                whichone = 12
        elif seat_code[:5] == 'ngg4w':
            number = int(seat_code[5:])
            if number < 33:
                sid = number + 2649
                whichone = 13
            elif 33 <= number <= 96:
                sid = number - 33 + 2690
                whichone = 14
            else:
                sid = number - 97 + 3143
                whichone = 15
        return sid, whichone

class WINXIN:
    def __init__(self, **kwargs):
        self.weixinInfo = kwargs

    # 对预约座位进行解码，映射成可以座位编号
    def decode(self,sid, whichone):  # nsk3004
        seatString = ''
        if whichone == 1:
            seatString = 'nzr' + str(sid - 4337)
        elif whichone == 2:
            seatString = 'nsk' + str(sid - 95)
        elif whichone == 3:
            seatString = 'nsk' + str(sid + 2477)
        elif whichone == 4:
            seatString = 'nsk' + str(sid + 1177)
        elif whichone == 5:
            seatString = 'nbz' + str(sid)
        elif whichone == 6:
            seatString = 'nbk' + str(sid)
        elif whichone == 7:
            seatString = 'ndz' + str(sid - 2875)
        elif whichone == 8:
            seatString = 'ngg3e' + str(sid - 2433)
        elif whichone == 9:
            seatString = 'ngg3e' + str(sid + 89 - 2682)
        elif whichone == 10:
            seatString = 'ngg3w' + str(sid - 2521)
        elif whichone == 11:
            seatString = 'ngg4e' + str(sid - 2617)
        elif whichone == 12:
            seatString = 'ngg4e' + str(sid + 33 - 2754)
        elif whichone == 13:
            seatString = 'ngg4w' + str(sid - 2649)
        elif whichone == 14:
            seatString = 'ngg4w' + str(sid - 2690 + 33)
        elif whichone == 15:
            seatString = 'ngg4w' + str(sid + 97 - 3143)
        return seatString

    def send(self):
        # 推送内容
        content =  "<body><p>尊敬的{0}：<p><p>您明天的座位已经预约完成！<p><p>预约座位编号：{1}<p><p>预约时间：{3}~{4}<p><body>".format(INFO['account'],self.decode(int(WEIXIN_INFO['sid']),self.weixinInfo['whichone']),INFO['atDate'],INFO['st'],INFO['et'])
        WxPusher.send_message(
            content=content,
            summary=self.weixinInfo['summary'],
            uids=self.weixinInfo['uids'],
            token=self.weixinInfo['appToken'],
            topic_ids=[]
        )
        logging.info('The message has been sent!')


if __name__ == '__main__':
    reserve = Reserve(**INFO)
    reserve.reserve()
