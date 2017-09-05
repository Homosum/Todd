#!/usr/bin/env py
# coding: utf-8

from wxbot import *
import ConfigParser
import json
import threading
import thread
# from time import sleep
import time
import datetime
import schedule
import urllib2,urllib
import math

class TulingWXBot(WXBot):
    def __init__(self):
        WXBot.__init__(self)

        self.tuling_key = ""
        self.robot_switch = True
        self.weather_url='https://free-api.heweather.com/v5/'
        self.weather_key='1e3f5a5ec59844f49d6d554341f9f2a5'

        try:
            cf = ConfigParser.ConfigParser()
            cf.read('conf.ini')
            self.tuling_key = cf.get('main', 'key')
        except Exception:
            pass
        print 'tuling_key:', self.tuling_key

    def tuling_auto_reply(self, uid, msg):
        if self.tuling_key:
            url = "http://www.tuling123.com/openapi/api"
            user_id = uid.replace('@', '')[:30]
            print '------msg----\n'
            print msg
            print '-------msg----\n'
            body = {'key': self.tuling_key, 'info':msg.encode('utf8'), 'userid': user_id}
            print '------body------\n'
            print body
            print '-------body------\n'
            r = requests.post(url, data=body)
            respond = json.loads(r.text)
            result = ''
            if respond['code'] == 100000:
                result = respond['text'].replace('<br>', '  ')
                result = result.replace(u'\xa0', u' ')
            elif respond['code'] == 200000:
                result = respond['url']
            elif respond['code'] == 302000:
                for k in respond['list']:
                    result = result + u"【" + k['source'] + u"】 " +\
                        k['article'] + "\t" + k['detailurl'] + "\n"
            else:
                result = respond['text'].replace('<br>', '  ')
                result = result.replace(u'\xa0', u' ')
            if  uid in  self.get_all_contact_uid():
                if self.get_contact_name(uid)['nickname'] ==u'虫二':
                    result=u'小仙女哦，'+result
                if self.get_contact_name(uid)['nickname']==u'少年达':
                    result=u'屁股达哦，'+result
                if self.get_contact_name(uid)['nickname']==u'怪兽曈':
                    result=u'曈曈小仙女哦，'+result
                if self.get_contact_name(uid)['nickname'] == u'好气':
                    result = u'小公主哦，' + result
                if self.get_contact_name(uid)['nickname'] == u'鲜肉水饺':
                    result = u'小可爱哦，' + result
                if self.get_contact_name(uid)['nickname'] == u'一只废毒。':
                    result = u'小仙女哦，' + result
                if self.get_contact_name(uid)['nickname'] == u'敦敦是个大敦敦':
                    result = u'长宝宝哦，' + result
                if self.get_contact_name(uid)['nickname'] == u'Andy':
                    result = u'宝宝，' + result
                if self.get_contact_name(uid)['nickname'] == u'雨中之神':
                    result = u'江哥哥，' + result
            print '    ROBOT:', result
            return result
        else:
            return u"知道啦"

    def auto_switch(self, msg):
        msg_data = msg['content']['data']
        stop_cmd = [u'退下', u'走开', u'关闭', u'关掉', u'休息', u'滚开',u'退朝',u'开工']
        start_cmd = [u'出来', u'启动', u'工作',u'上朝',u'放假']
        if self.robot_switch:
            for i in stop_cmd:
                if i == msg_data:
                    self.robot_switch = False
                    self.send_msg_by_uid(u'[Robot]' + u'机器人已关闭！', msg['to_user_id'])
        else:
            for i in start_cmd:
                if i == msg_data:
                    self.robot_switch = True
                    self.send_msg_by_uid(u'[Robot]' + u'机器人已开启！', msg['to_user_id'])

    def handle_msg_all(self, msg):
        if not self.robot_switch and msg['msg_type_id'] != 1:
            return
        if msg['msg_type_id'] == 1 and msg['content']['type'] == 0:  # reply to self
            self.auto_switch(msg)
        elif msg['msg_type_id'] == 4 and msg['content']['type'] == 0:  # text message from contact
            print self.get_contact_name(msg['user']['id'])
            if self.get_contact_name(msg['user']['id']) == u'Homosum':
                self.auto_switch(msg)
            if self.get_contact_name(msg['user']['id']) == u'怪兽曈' and msg['content']['data'] == u'想你':
                self.send_msg(u'怪兽曈',self.daojishi(u'怪兽曈'))
                return
            self.send_msg(u'怪兽曈', self.daojishi(u'怪兽曈'))
            # self.send_msg_by_uid(self.tuling_auto_reply(msg['user']['id'], msg['content']['data']), msg['user']['id'])
        elif msg['msg_type_id']==4 and msg['content']['type']==10:
            self.send_msg(self.get_contact_name(msg['user']['id'])['nickname'],u'怀孕了大家一起帮你解决，撤回了干什么？')
        elif msg['msg_type_id'] == 3 and msg['content']['type'] == 0:  # group text message
            if self.get_contact_name(msg['user']['id']) == u'怪兽曈' and msg['content']['data'] == u'想你':
                self.send_msg(u'怪兽曈',self.daojishi(u'怪兽曈'))
                return
            if 'detail' in msg['content']:
                my_names = self.get_group_member_name(msg['user']['id'], self.my_account['UserName'])
                if my_names is None:
                    my_names = {}
                if 'NickName' in self.my_account and self.my_account['NickName']:
                    my_names['nickname2'] = self.my_account['NickName']
                if 'RemarkName' in self.my_account and self.my_account['RemarkName']:
                    my_names['remark_name2'] = self.my_account['RemarkName']

                is_at_me = False
                for detail in msg['content']['detail']:
                    if detail['type'] == 'at':
                        for k in my_names:
                            if my_names[k] and my_names[k] == detail['value']:
                                is_at_me = True
                                break
                if is_at_me:
                    src_name = msg['content']['user']['name']
                    reply = 'to ' + src_name + ': '
                    if msg['content']['type'] == 0:  # text message
                        reply += self.tuling_auto_reply(msg['content']['user']['id'], msg['content']['desc'])
                    else:
                        reply += u"对不起，只认字，其他杂七杂八的我都不认识，,,Ծ‸Ծ,,"
                    self.send_msg_by_uid(reply, msg['user']['id'])
        elif msg['msg_type_id']==3 and msg['content']['type']==10:
            src_name = msg['content']['user']['name']
            self.send_msg_by_uid(src_name+u'，怀孕了大家一起帮你解决，撤回干什么？',msg['user']['id'])
    def scheduleRun(self):
        # for contact in self.contact_list:
        #     print contact
            # if 'NickName' in contact and contact['NickName'] == u'Homosum':
            #     self.send_msg(contact['NickName'], contact['City'] + u'天气')
        # self.send_msg(u'Homosum',u'加油哦')
        # self.test()
        schedule.every().day.at("7:30").do(self.send_weather,u'虫二')
        schedule.every().day.at("7:30").do(self.send_weather, u'Andy')
        schedule.every().day.at("7:30").do(self.send_weather, u'怪兽曈')
        schedule.every().day.at("7:30").do(self.send_weather, u'Homosum')
        schedule.every().day.at("7:30").do(self.send_weather, u'敦敦是个大敦敦')
        schedule.every().day.at("7:30").do(self.send_weather, u'一只废毒。','赣州')
        schedule.every().day.at("7:30").do(self.send_weather, u'雨中之神','东莞')
        schedule.every().day.at("7:30").do(self.send_weather, u'鲜肉水饺','宁波')
        schedule.every().day.at('16:00').do(self.send_msg,u'Andy',u'保持健康，要多喝水哦~')
        schedule.every().day.at('16:00').do(self.send_msg, u'Homosum', u'保持健康，要多喝水哦~')
        schedule.every().day.at('16:00').do(self.send_msg, u'敦敦是个大敦敦', u'保持健康，要多喝水哦~')
        schedule.every().day.at('16:00').do(self.send_msg, u'虫二', u'保持健康，要多喝水哦~')
        schedule.every().day.at('16:00').do(self.send_msg, u'怪兽曈', u'保持健康，要多喝水哦~')
        schedule.every().day.at('16:00').do(self.send_msg, u'雨中之神', u'保持健康，要多喝水哦~')
        schedule.every().day.at('16:00').do(self.send_msg, u'鲜肉水饺', u'保持健康，要多喝水哦~')
        schedule.every().day.at('16:00').do(self.send_msg, u'一只废毒。', u'保持健康，要多喝水哦~')

        # schedule.every(1).minutes.do(self.send_msg,u'Homosum',u'每分钟一次')
        # schedule.every(1).minutes.do(self.send_weather,u'Homosum')
        print '-----shedule-------'





    def get_all_contact_uid(self):
        all_uid=[]
        for contact in self.contact_list:
            all_uid.insert(0,contact['UserName'])
        return all_uid


    def daojishi(self,name):
        now = datetime.datetime.now()
        endTime = datetime.datetime(2017,9,17,10,0,0,0)
        dev = (endTime-now).seconds+(endTime-now).days*24*3600
        print dev
        result_time = self.changeTime(dev)
        result_ = u'距离相会还有 %s ' % result_time
        self.send_weather(name,result_)


    def changeTime(self,allTime):
        day = 24 * 60 * 60
        hour = 60 * 60
        min = 60
        if allTime < 60:
            return u"%d 秒" % math.ceil(allTime)
        elif allTime > day:
            days = divmod(allTime, day)
            return u"%d 天, %s" % (int(days[0]), self.changeTime(days[1]))
        elif allTime > hour:
            hours = divmod(allTime, hour)
            return u'%d 小时, %s' % (int(hours[0]), self.changeTime(hours[1]))
        else:
            mins = divmod(allTime, min)
            return u"%d 分钟, %d 秒" % (int(mins[0]), math.ceil(mins[1]))


    def send_weather(self,name,City=None):
        if  City==None:
            for contact in self.contact_list:
                if  'NickName' in contact and contact['NickName']==name:
                    if contact['City']!='':
                        city=contact['City'].encode('utf-8')
                        self.send_msg(name,self.get_weather_of_city(city))
        else:
            self.send_msg(name,City)

    def get_weather_of_city(self,city):
        parme_dict={'key':self.weather_key,'city':city}
        parme_data=urllib.urlencode(parme_dict)
        url=self.weather_url+'weather'
        req=urllib2.Request(url,parme_data)
        response=urllib2.urlopen(req)
        weather_msg=response.read()
        print weather_msg
        weather_dict=json.loads(weather_msg)
        l_dict = weather_dict['HeWeather5'][0]
        fomart = u'Todd来打卡了，%s今天白天%s，夜晚%s。%s~%s℃。%s%s'
        # 网站的请求参数里，一般支持utf-8和ascii，不支持unicode，所以传参时不用u; 返回的json里，因为用了u,所以在format里要保持编码格式一直，所以要用u
        values = (l_dict['basic']['city'], l_dict['daily_forecast'][0]['cond']['txt_d'],
                  l_dict['daily_forecast'][0]['cond']['txt_n'], l_dict['daily_forecast'][0]['tmp']['min'],
                  l_dict['daily_forecast'][0]['tmp']['max'], l_dict['suggestion']['drsg']['txt'],
                  l_dict['suggestion']['flu']['txt'])
        str_ = fomart % values
        return str_

    def add_font_name(self,name,word):
        result=word
        if name == u'虫二':
            result = u'小仙女哦，' + result
        if name == u'少年达':
            result = u'屁股达哦，' + result
        if name == u'怪兽曈':
            result = u'曈曈小仙女哦，' + result
        if name == u'好气':
            result = u'小公主哦，' + result
        if name == u'鲜肉水饺':
            result = u'小可爱哦，' + result
        if name == u'一只废毒。':
            result = u'小仙女哦，' + result
        if name == u'敦敦是个大敦敦':
            result = u'长宝宝哦，' + result
        if name == u'Andy':
            result = u'宝宝，' + result
        if name == u'雨中之神':
            result = u'江哥哥，' + result
        if name == u'Homosum':
            result = u'爸爸，' + result
        return result



def main():
    bot = TulingWXBot()
    bot.DEBUG = True
    bot.conf['qr'] = 'png'
    bot.run()


if __name__ == '__main__':
    main()

