from asyncio.events import set_child_watcher
from contextlib import ContextDecorator
from random import random
import re
import sys
from typing import Counter
sys.path.append(".")
from social_robot.bot import Robot
from social_robot.config import PhoneConfig
from social_robot.devices.phone import Phone
from linkedin.phone import linkedin_element_selector
from linkedin.phone import linkedin_url
import os
import string
from urllib.request import urlretrieve

class LinkedinNurture(Robot):
    device : Phone
    def __init__(self, devices: Phone, config: PhoneConfig) -> None:
        super().__init__(devices, config)

    def register(self):
        self.device.flush_app()
        self.device.launch_app()
        # TODO 注册代码
        self.device.click('//*[@resource-id="com.linkedin.android:id/growth_prereg_fragment_join_button"]')
        self.device.typing('//*[@resource-id="com.linkedin.android:id/growth_join_split_form_full_name"]','李四')
        self.device.click('//*[@resource-id="com.linkedin.android:id/growth_join_split_form_join_button"]')
        self.device.typing('//*[@resource-id="com.linkedin.android:id/growth_join_split_form_email_address"]',self.device.storage['phone'])
        self.device.click('//*[@resource-id="com.linkedin.android:id/growth_join_split_form_join_button"]')
        self.device.typing('//*[@resource-id="com.linkedin.android:id/growth_join_split_form_password"]',self.device.storage['phone_password'])
        self.device.click('//*[@resource-id="com.linkedin.android:id/growth_join_split_form_join_button"]')
        # 谷歌图片验证
        # 手机验证码验证,测试时候用这个方法收不到验证码，改用实体手机卡完成注册流程
        code = self.device.receive_sms()
        self.device.typing('//*[@resource-id="input__phone_verification_pin"]',code['verify'])
        self.device.click('//*[@resource-id="register-phone-submit-button"]')
        # 跳过地区选择
        self.device.click('//*[@resource-id="com.linkedin.android:id/growth_onboarding_navigation_bottom_button"]')
        self.device.typing('//*[@resource-id="com.linkedin.android:id/growth_onboarding_position_job_title_input"]','经理')
        self.device.click('//*[@resource-id="com.linkedin.android:id/type_ahead_result_view"]/android.widget.LinearLayout[1]')
        self.device.click('//*[@resource-id="com.linkedin.android:id/growth_onboarding_position_experience_input"]')
        self.device.click('//*[@resource-id="com.linkedin.android:id/bottom_sheet_recyclerview"]/android.widget.RadioButton[4]')
        self.device.typing('//*[@resource-id="com.linkedin.android:id/growth_onboarding_position_company_input"]','农业')
        self.device.click('//*[@resource-id="com.linkedin.android:id/type_ahead_result_view"]/android.widget.RelativeLayout[1]')
        self.device.click('//*[@resource-id="com.linkedin.android:id/growth_onboarding_navigation_top_button"]')
        self.device.click('//*[@resource-id="com.linkedin.android:id/growth_onboarding_navigation_bottom_button"]')
        self.device.click('//*[@resource-id="com.linkedin.android:id/growth_onboarding_job_intent_cta_not_now"]')
        self.device.click('//*[@resource-id="com.linkedin.android:id/growth_onboarding_navigation_bottom_button"]')
        self.device.click('//*[@resource-id="com.linkedin.android:id/growth_onboarding_navigation_bottom_button"]')
        self.device.click('//*[@resource-id="com.linkedin.android:id/onboarding_follow_footer_finish_button"]')
        return super().register()

    def login(self):
        # TODO 登陆代码
        self.device.flush_app()
        self.device.launch_app()
        self.device.click(linkedin_element_selector.LOGIN_BUTTON)
        #防止因为输入法导致第一次输入失败
        self.device.typing('//*[@resource-id="com.linkedin.android:id/growth_login_join_fragment_email_address"]',' ')
        self.device.typing('//*[@resource-id="com.linkedin.android:id/growth_login_join_fragment_email_address"]',self.device.storage['phone'])
        self.device.typing('//*[@resource-id="com.linkedin.android:id/growth_login_join_fragment_password"]',self.device.storage['phone_password'])
        self.device.click(linkedin_element_selector.LOGIN_VERIFY_BUTTON)
        if self.device.wait_element('//*[@text="帐号暂时无法使用。更多信息，请前往领英帮助中心。"]'):
            print('the account has been banned')
            return 0
        elif self.device.wait_element('//*[@text="抱歉，用户名不正确。请再试一次。"]') or self.device.wait_element('//*[@text="抱歉，密码不正确。请再试一次或点击“忘记密码”。"]'):
            print('the account or password is wrong')
        else:
            #用于处理有时候点击搜索框会弹出是否采用搜索建议影响后续操作的问题
            self.device.click('//*[@resource-id="com.linkedin.android:id/search_open_bar_box"]')
            if self.device.wait_element('//*[@resource-id="android:id/button1"]'):
                self.device.click('//*[@resource-id="android:id/button1"]')
            #保证登录的时候在主界面
            self.device.jump('https://www.linkedin.com/')
            print('login successfully')
            return super().login()

    def logout(self):
        # TODO 登出代码
        self.gotohomepage()
        self.device.click('//*[@resource-id="com.linkedin.android:id/me_launcher_container"]')
        self.device.click('//*[@resource-id="com.linkedin.android:id/interests_panel_view_settings"]')
        self.device.slide((0.467, 0.893),(0.532, 0.438))
        self.device.click('//*[@resource-id="sign_out"]')
        return 0

    def visit(self):
        # TODO 前往网页代码
        if person_params['action_target_type'] == 'random':
            self.gotorandhomepage()
        else:
            self.device.jump(self.device.storage['action_target_link'])
        return 0

    def like(self):
        # TODO 点赞代码
        if person_params['action_target_type'] == 'random':
            self.gotorandpage()
        else:
            self.visit()
        self.device.click(linkedin_element_selector.LIKE_BUTTON)
        self.gotohomepage()
        return 0

    def gotohomepage(self):
        # TODO 前往自己主页代码
        self.device.close()
        self.device.jump('https://www.linkedin.com/')
        return 0

    def comment(self):
        # TODO 评论代码
        if person_params['action_target_type'] == 'random':
            self.gotorandpage()
        else:
            self.visit()
        self.device.click(linkedin_element_selector.COMMENT_BUTTON)
        self.device.typing('//*[@resource-id="com.linkedin.android:id/feed_comment_bar_reply"]',self.device.storage['text']['content'])
        self.device.click('//*[@resource-id="com.linkedin.android:id/feed_comment_bar_send"]')
        self.gotohomepage()
        return 0

    def follow(self):
        # TODO 关注代码
        if person_params['action_target_type'] == 'random':
            self.gotorandhomepage()
        else:
            self.visit()
        #判断是否已经关注过用户
        if(self.device.wait_element('//*[@text="关注"]')):
            self.device.click(linkedin_element_selector.FOLLOW_BUTTON)
            self.gotohomepage()
        else:
            print('you have followed this user')
            self.gotohomepage()
        return 0

    def repost(self):
        # TODO 转发代码
        if person_params['action_target_type'] == 'random':
            self.gotorandpage()
        else:
            self.visit()
        self.device.click(linkedin_element_selector.REPOST_BUTTON)
        if self.device.storage['text']['theme']:
            self.device.storage['text']['theme']='#'+self.device.storage['text']['theme']+' '
        self.device.typing('//*[@resource-id="com.linkedin.android:id/share_compose_text_input_entities"]',self.device.storage['text']['theme']+self.device.storage['text']['content'])
        self.device.click('//*[@resource-id="com.linkedin.android:id/share_compose_post_button"]')
        count = 0
        while(not self.device.wait_element(linkedin_element_selector.DISMISS_BUTTON) and count<3):
            self.device.wait_element(linkedin_element_selector.DISMISS_BUTTON)
            count+=1
        if count<3:
            print('repost successfully')
        else:
            print('repost failed')
        self.gotohomepage()
        return 0

    def download(self,url):
        # TODO 下载图片和视频代码
        # 下载图片/视频到本地，再转到手机的相册目录下
        # 格式参考https://post-1302194850.cos.ap-chengdu.myqcloud.com/763cc1ce-282a-4cfb-9afd-76859ea4fbed?png
        os.makedirs('./linkedin/source/',exist_ok=True)
        filename=url.split('/')[-1]
        filename=filename.replace('?','.')
        urlretrieve(url, './linkedin/source/'+filename)
        # 放在照相机目录下，方便linkedin识别到图片、视频
        self.device.context.push('./linkedin/source/'+filename,"/sdcard/DCIM/Camera/")
        self.device.context.shell('adb -d shell am broadcast -a android.intent.action.MEDIA_SCANNER_SCAN_FILE -d file:///sdcard/DCIM/Camera')
        return filename

    def delete(self,url):
        # TODO 删除图片视频代码
        # 由于下载的图片或者视频在相册的摆放位置是按原视频时间排序，而选择是第一个，所以这里在每次执行完之后都会删除，防止一个视频一直出现在最开始
        filename=url.split('/')[-1]
        filename=filename.replace('?','.')
        self.device.context.shell('rm -f /sdcard/DCIM/Camera/'+filename) 
        self.device.context.shell('adb -d shell am broadcast -a android.intent.action.MEDIA_SCANNER_SCAN_FILE -d file:///sdcard/DCIM/Camera')
        return 0

    def post(self,type=None):
        # TODO 发帖代码
        if type=='text':
            self.__text_post()
        if type=='image':
            self.__image_post()
        if type=='video':
            self.__video_post()
        return 0

    def __text_post(self):
        # TODO 文字发帖代码
        self.device.click('//*[@resource-id="com.linkedin.android:id/tab_post"]')
        if self.device.storage['text']['theme']:
            self.device.storage['text']['theme']='#'+self.device.storage['text']['theme']+' '
        self.device.typing('//*[@resource-id="com.linkedin.android:id/share_compose_text_input_entities"]',self.device.storage['text']['theme']+self.device.storage['text']['content'])
        self.device.click('//*[@resource-id="com.linkedin.android:id/share_compose_post_button"]')
        #发布成功会自动跳回主页，并且弹出成功发布的提示
        count = 0
        while(not self.device.wait_element(linkedin_element_selector.DISMISS_BUTTON) and count<3):
            self.device.wait_element(linkedin_element_selector.DISMISS_BUTTON)
            count+=1
        if count<3:
            self.device.click(linkedin_element_selector.DISMISS_BUTTON)
        else:
            print('text send failed')
        return 0

    def __image_post(self):
        # TODO 图片发帖代码
        if len(self.device.storage['download_url']['img_link']) == 1:
            self.download(self.device.storage['download_url']['img_link'][0])
            filename=self.device.storage['download_url']['img_link'][0].split('/')[-1]
            filename=filename.replace('?','.')
            self.device.context.shell('am start -a android.intent.action.VIEW -t "image/*" -d \"file:///storage/emulated/0/DCIM/Camera/%s\"'%filename)
            self.device.click('//*[@resource-id="android.miui:id/resolver_grid"]/android.widget.LinearLayout[1]')
            self.device.click('//*[@text="发送"]')
            self.device.click('//*[@resource-id="com.miui.gallery:id/chooser_recycler"]/android.widget.LinearLayout[4]/android.widget.ImageView[1]')
            if self.device.storage['text']['theme']:
                self.device.storage['text']['theme']='#'+self.device.storage['text']['theme']+' '
            self.device.typing('//*[@resource-id="com.linkedin.android:id/share_compose_text_input_entities"]',self.device.storage['theme']+self.device.storage['content'])
            self.device.click('//*[@resource-id="com.linkedin.android:id/share_compose_post_button"]')
            #发布成功会自动跳回主页，并且弹出成功发布的提示
            count = 0
            while(not self.device.wait_element(linkedin_element_selector.DISMISS_BUTTON) and count<3):
                self.device.wait_element(linkedin_element_selector.DISMISS_BUTTON)
                count+=1
            if count<3:
                self.device.click(linkedin_element_selector.DISMISS_BUTTON)
            else:
                print('image send failed')
            self.delete(self.device.storage['download_url']['img_link'][0])
            return 0
        elif len(self.device.storage['download_url']['img_link']) == 0:
            print('no img_url found')
            return 0
        else:
            image_list = []
            for i in range (len(self.device.storage['download_url']['img_link'])):
                self.download(str(self.device.storage['download_url']['img_link'][i]))
                image_list.append(self.download(str(self.device.storage['download_url']['img_link'][i])))
            print(image_list)
            self.gotohomepage()
            self.device.click('//*[@resource-id="com.linkedin.android:id/tab_post"]')
            self.device.click('//*[@text="添加照片"]')
            self.device.context.long_click(0.207, 0.387)
                #'//*[@resource-id="com.google.android.documentsui:id/dir_list"]/android.widget.LinearLayout[1]')
            for i in range(len(self.device.storage['download_url']['img_link'])):
                if i != (len(self.device.storage['download_url']['img_link'])-1):
                    self.device.click('//*[@resource-id="com.google.android.documentsui:id/dir_list"]/android.widget.LinearLayout[%s]'%(i+2))
            self.device.click('//*[@resource-id="com.google.android.documentsui:id/option_menu_search"]')
            self.device.click('//*[@resource-id="com.linkedin.android:id/image_review_done"]')
            if self.device.storage['text']['theme']:
                self.device.storage['text']['theme']='#'+self.device.storage['text']['theme']+' '
            self.device.typing('//*[@resource-id="com.linkedin.android:id/share_compose_text_input_entities"]',self.device.storage['text']['theme']+self.device.storage['text']['content'])
            self.device.click('//*[@resource-id="com.linkedin.android:id/share_compose_post_button"]')
            count = 0
            while(not self.device.wait_element(linkedin_element_selector.DISMISS_BUTTON) and count<3):
                self.device.wait_element(linkedin_element_selector.DISMISS_BUTTON)
                count+=1
            if count<3:
                self.device.click(linkedin_element_selector.DISMISS_BUTTON)
                print('image sent successfully')
            else:
                print('image sent failed')
            for i in range (len(image_list)):
                self.delete(str(image_list[i]))
            return 0

    def __video_post(self):
        # TODO 视频发帖代码
        # 发布视频必须要挂VPN才能成功
        self.download(self.device.storage['download_url']['video_link'][0])
        filename=self.device.storage['download_url']['video_link'][0].split('/')[-1]
        filename=filename.replace('?','.')
        self.device.context.shell('am start -a android.intent.action.VIEW -t "image/*" -d \"file:///storage/emulated/0/DCIM/Camera/%s\"'%filename)
        self.device.click('//*[@resource-id="android.miui:id/resolver_grid"]/android.widget.LinearLayout[1]')
        self.device.click('//*[@text="发送"]')
        self.device.click('//*[@resource-id="com.miui.gallery:id/chooser_recycler"]/android.widget.LinearLayout[4]/android.widget.ImageView[1]')
        if self.device.storage['text']['theme']:
            self.device.storage['text']['theme']='#'+self.device.storage['text']['theme']+' '
        self.device.typing('//*[@resource-id="com.linkedin.android:id/share_compose_text_input_entities"]',self.device.storage['text']['theme']+self.device.storage['text']['content'])
        self.device.click('//*[@resource-id="com.linkedin.android:id/share_compose_post_button"]')
        #视频上传速度比较慢，等待发布成功,发布成功会自动跳回主页，并且弹出成功发布的提示
        count = 0
        while(not self.device.wait_element(linkedin_element_selector.DISMISS_BUTTON) and count<3):
            self.device.wait_element(linkedin_element_selector.DISMISS_BUTTON)
            count+=1
        if(count<3):
            print('video sent successfully')
            self.device.click(linkedin_element_selector.DISMISS_BUTTON)
        else:
            print('video sent failed')
        self.delete(self.device.storage['download_url']['video_link'][0])
        return 0
    
    def gotorandhomepage(self):
        # TODO 访问随机主页代码
        #随机生成三个字符作为关键词来搜索相关的主页
        randomurl = ''.join(random.sample(['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z'],3))
        print(randomurl)
        self.gotohomepage()
        self.device.typing('//*[@resource-id="com.linkedin.android:id/search_bar_text"]',randomurl)
        self.device.click('//*[@resource-id="com.linkedin.android:id/search_typeahead_see_all_button"]')
        self.device.click('//*[@content-desc="筛选条件: 公司"]/..')
        #等待有权限关注的公司
        while(self.device.wait_element('//*[@resource-id="com.linkedin.android:id/search_empty_state_primary_action_button"]') or (not self.device.wait_element('//*[@resource-id="com.linkedin.android:id/search_cluster_expandable_list_view"]/android.view.ViewGroup[1]/android.widget.FrameLayout[1]/android.widget.LinearLayout[1]/android.widget.ImageButton[1]'))):
            randomurl = ''.join(random.sample(['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z'],3))
            print(randomurl)
            #self.device.click('//*[@resource-id="com.linkedin.android:id/search_empty_state_primary_action_button"]')
            self.device.jump('https://www.linkedin.com/in/')
            self.device.typing('//*[@resource-id="com.linkedin.android:id/search_bar_text"]',randomurl)
            self.device.click('//*[@resource-id="com.linkedin.android:id/search_typeahead_see_all_button"]')
            self.device.click('//*[@content-desc="筛选条件: 公司"]/..')
        self.device.click('//*[@resource-id="com.linkedin.android:id/search_cluster_expandable_list_view"]/android.view.ViewGroup[1]/android.widget.FrameLayout[1]/android.widget.LinearLayout[1]/android.widget.ImageButton[1]/../../..')
        #com.linkedin.android:id/search_entity_primary_action
        return 0

    def gotorandpage(self):
        # TODO 访问随机动态页面代码
        randomurl = ''.join(random.sample(['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z'],3))
        print(randomurl)
        self.gotohomepage()
        self.device.typing('//*[@resource-id="com.linkedin.android:id/search_bar_text"]',randomurl)
        self.device.click('//*[@resource-id="com.linkedin.android:id/search_typeahead_see_all_button"]')
        self.device.click('//*[@content-desc="筛选条件: 动态"]/..')
        #根据是否有编辑搜索的提示来判断是否有可以点击的动态
        while(self.device.wait_element('//*[@resource-id="com.linkedin.android:id/search_empty_state_primary_action_button"]')):
            randomurl = ''.join(random.sample(['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z'],3))
            print(randomurl)
            self.device.click('//*[@resource-id="com.linkedin.android:id/search_empty_state_primary_action_button"]')
            self.device.typing('//*[@resource-id="com.linkedin.android:id/search_bar_text"]',randomurl)
            self.device.click('//*[@resource-id="com.linkedin.android:id/search_typeahead_see_all_button"]')
        self.device.click('//*[@resource-id="com.linkedin.android:id/search_results_list"]/android.view.ViewGroup[1]')
        #如果是因为动态太长而导致没显示出点赞和评论等按钮，就向上滑动页面
        while(not self.device.wait_element(linkedin_element_selector.LIKE_BUTTON)):
            self.device.slide((0.538, 0.845),(0.569, 0.216))
        return 0

    def _check_params(self) -> bool:
        # 参数检测
        return super()._check_params()

    def is_logged(self) -> bool:
        # TODO 判断是否登录代码
        # 根据打开APP时是否有相应的按钮判断是否登录
        self.device.close()
        self.device.launch_app()
        if(self.device.wait_element('//*[@resource-id="com.linkedin.android:id/growth_prereg_fragment_join_button"]')or self.device.wait_element('//*[@resource-id="join_now"]')):
            print('not logged')
            return False
        else:
            print('have logged')
            return True

    def _logged(self):
        return super()._logged
    
    def test(self):
        self.device.click('//*[@resource-id="com.linkedin.android:id/search_open_bar_box"]')
        if self.device.wait_element('//*[@resource-id="android:id/button1"]'):
            self.device.click('//*[@resource-id="android:id/button1"]')
        self.device.typing('//*[@resource-id="com.linkedin.android:id/search_bar_edit_text"]','fadf')
        return 0

if __name__ == '__main__':
    from uuid import uuid1
    import random
    from faker import Faker
    f=Faker('en')

    person_params = {}
    person_params['first_name'] = f.first_name()
    person_params['last_name'] = f.last_name()
    person_params['username'] = person_params['first_name']+person_params['last_name']
    person_params['birth'] = f'{random.randint(1980,2001)}-{random.randint(1,12)}-{random.randint(1,28)}'
    person_params['password'] = f.password(12)
    person_params['platform'] = "linkedin"
    person_params['task_msg'] = f'{uuid1()}'
    person_params['gender']=f'{random.randint(0,1)}'
    person_params['action_target_link']='https://www.linkedin.com/school/peking-university/'
    person_params['text']={
        'theme':'fuck',
        'content':'fuck you'
    }
    person_params['action_target_type']='random'
    person_params['download_url']={
        'img_link':['https://post-1302194850.cos.ap-chengdu.myqcloud.com/763cc1ce-282a-4cfb-9afd-76859ea4fbed?png','https://data-1302194850.cos.ap-chengdu.myqcloud.com/1e294c62be13c875f3534f42f52d455c?png'],
        'video_link':['https://data-1302194850.cos.ap-chengdu.myqcloud.com/e10ece1d4b96c6aad46f6a86ab5a8da3?mp4']
    }

    person_params['email'] = {
        'email':'',
        'email_password':'',
        'email_server':''
    }
    person_params['phone']='+4407419654215'
    person_params['phone_password']='de87adf3'
    
    person_params['serial']=''
    phoneConfig = PhoneConfig(
        params=person_params,
        necessary=set(),
    )
    bot = LinkedinNurture(config=phoneConfig, devices=Phone)
    # bot.login()
    # bot.visit()
    # bot.register()
    # bot.follow()
    # bot.device.click('//*[@content-desc="筛选条件: 公司"]/..')
    # bot.logout()
    # bot.like()
    # bot.comment()
    # bot.download()
    # bot.delete()
    # bot._text_post()
    # bot._image_post()
    # bot._video_post()
    # bot.post('text')
    # bot.gotohomepage()
    # bot.repost()
    # bot.post('image')
    # bot.gotorandhomepage()
    # print(bot.test())
    bot.gotorandpage()
    # bot.post('video')
    # if bot.is_logged() == False:
    # bot.login()
    # bot.test()
    