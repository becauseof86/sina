#coding:utf-8
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import Image
import StringIO
from ydm import ydm
import time

def crop_save_element(elem,browser):#验证码图片截取并保存
    loc  = elem.location
    size = elem.size
    left  = loc['x']
    top   = loc['y']
    width = size['width']
    height = size['height']
    box = (int(left), int(top), int(left+width), int(top+height))
    print box
    try:
        screenshot = browser.get_screenshot_as_png()
        img = Image.open(StringIO.StringIO(screenshot))
        box=tuple([i*2 for i in box]) #win10 200%更改文本 应用的大小 会造成bug 所以在此电脑上加了这个放大2倍
        area = img.crop(box)
        area.save('c:\mystuff\door.png')
    except Exception,e:
        print e
def login(username,password):
    browser=webdriver.Chrome() #chromedriver放入系统path或者 直接.Chrome('chromedriver路径')
    browser.maximize_window()
    browser.get('http://weibo.com/login.php')
    try:
        name_input = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, "//input[@id='loginname']")))
        name_input.clear()
        name_input.send_keys(username)
        password_input=browser.find_element_by_xpath("//input[@type='password' and @name='password']")
        password_input.send_keys(password)
        try: #验证码的元素是隐藏的 输入账号后 验证码会ajax加载并显示
            captcha = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, "//img[@width='95' and @height='34']")))
            crop_save_element(captcha,browser)
            #capcha.screenshot('c:\mystuff\door.png')
        except Exception,e:
            print e
            return
    except Exception,e:
        print e
        return
    #云打码
    ydm_username = 'becauseof86'
    ydm_password = 'Yundama1986'
    ydm_obj=ydm.YDMHttp(ydm_username,ydm_password,3510, '7281f8452aa559cdad6673684aa8f575')#账号密码以及推荐者信息
    uid=ydm_obj.login()
    print ydm_obj.balance()
    cid, result = ydm_obj.decode('c:\mystuff\door.png', 1005, 20)#验证码型号 超时
    print('cid: %s, result: %s' % (cid, result))
    if result:#识别失败的话 result=''
        code_input=browser.find_element_by_xpath("//input[@node-type='verifycode' and @name='verifycode']")
        code_input.send_keys(result)
        time.sleep(1) #有时候点登陆没反应 可能是太快了
        submit=browser.find_element_by_xpath("//a[@action-type='btn_submit' and @node-type='submitBtn']")
        submit.click()
        try: 
            weibo_name = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, "//div[@class='nameBox']/a[@class='name S_txt1']")))
            print u'微博名:%s' %weibo_name.text
            print browser.get_cookies()
        except Exception,e:
            print e
            return

    
if __name__=='__main__':
    login('15252461911','Dwj882193')
