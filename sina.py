#coding:utf-8
import execjs
import requests
import re
import json
import random

def compile_js():
    e=execjs.get('PHANTOMJS') #设置系统环境变量PHANTOMJS 值是phantomjs的exe的路径
    with open('weibo.js') as f:
        comp=e.compile(f.read())
        #print comp.call('get_name','15252461911')
        return comp
    
def get_su(name,comp):
    return comp.call('get_su',name)
    
def get_sp(pwd,nonce,servertime,rsaPubkey,comp):
    return comp.call('get_sp',pwd,nonce,servertime,rsaPubkey)
    
def get_prelogin_json(su,session):
    url = "https://login.sina.com.cn/sso/prelogin.php"

    querystring = {"entry":"weibo","callback":"sinaSSOController.preloginCallBack","su":su,"rsakt":"mod","checkpin":"1","client":"ssologin.js(v1.4.18)"}

    headers = {
        'host': "login.sina.com.cn",
        'connection': "keep-alive",
        'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
        'accept': "*/*",
        'referer': "http://weibo.com/",
        'accept-encoding': "gzip, deflate, sdch, br",
        'accept-language': "zh-CN,zh;q=0.8",
        'cache-control': "no-cache"
    }

    response = session.get(url, headers=headers, params=querystring)
    json_string=re.search(r'\((.*?)\)',response.text).group(1)
    json_dict=json.loads(json_string)
    print json_dict
    return json_dict
def get_img(pcid,session): #下载图片验证码
    url = "http://login.sina.com.cn/cgi/pin.php"
    querystring = {"pcid":pcid,'s':0,'r':''.join(random.sample('0123456789',8))}
    headers = {
        'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
        'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        'referer': "http://weibo.com/",
        'accept-encoding': "gzip, deflate",
        'accept-language': "zh-Hans-CN,zh-Hans;q=0.8,en-US;q=0.5,en;q=0.3"
    }
    response=session.get(url,headers=headers,params=querystring,stream=True)
    with open('door.png','wb') as f:
        for chunk in response.iter_content(1000):
            f.write(chunk)
    
def login(su,sp,json_dict,session):
    url = "http://login.sina.com.cn/sso/login.php"

    querystring = {"client":"ssologin.js(v1.4.18)"}

    payload = {
        'encoding':'UTF-8',
        'entry':'weibo',
        'from':'',
        'gateway':'1',
        'nonce':json_dict['nonce'],
        'pagerefer':'http://login.sina.com.cn/sso/logout.php?entry=miniblog&r=http%3A%2F%2Fweibo.com%2Flogout.php%3Fbackurl%3D%252F',
        'prelt':'212',
        'pwencode':'rsa2',
        'returntype':'META',
        'rsakv':json_dict['rsakv'],
        'savestate':7,
        'servertime':json_dict['servertime'],
        'service':'miniblog',
        'sp':sp,
        'sr':'1920*1080',
        'su':su,
        'url':'http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack',
        'useticket':1,
        'vsnf':1
    }
    headers = {
        'x-devtools-request-id': "11732.986",
        'origin': "http://weibo.com",
        'x-devtools-emulate-network-conditions-client-id': "eda6a578-8e3b-4e52-af4f-2ba8d90b4cff",
        'upgrade-insecure-requests': "1",
        'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
        'content-type': "application/x-www-form-urlencoded",
        'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        'referer': "http://weibo.com/",
        'accept-encoding': "gzip, deflate",
        'accept-language': "zh-CN,zh;q=0.8",
        'cache-control': "no-cache",
    }
    if(json_dict['showpin']==1): #如果prelogin返回的结果显示该账号登陆需要验证码，那么去加载验证码，post数据需要添加pcid和door
        get_img(json_dict['pcid'],session)
        door = raw_input(u'请输入验证码：\n'.encode('gbk'))#适配windows的命令行程序
        payload['pcid']=json_dict['pcid']
        payload['door']=door #手动输入的验证码
        
    response = session.post(url, data=payload, headers=headers, params=querystring)
    print response.encoding
    response.encoding='gbk'#requests猜测的编码不对，手动改编码方式
    print(response.text)
    try:
        redirect_url=re.search(r"replace\('(.*?)'\)",response.text).group(1)
        return redirect_url
    except Exception,e:
        print e
        print u'登陆失败'
        
def redirect(redirect_url,session):
    url = redirect_url
    headers = {
        'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
        'accept': "text/html, application/xhtml+xml, image/jxr, */*",
        'referer': "http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.18)",
        'accept-encoding': "gzip, deflate, br",
        'accept-language': "zh-Hans-CN,zh-Hans;q=0.8,en-US;q=0.5,en;q=0.3"
    }
    response=session.get(url,headers=headers)
    json_string=re.search(r'\((.*?)\)',response.text).group(1)
    ret_dict=json.loads(json_string)
    print ret_dict
    return ret_dict

def get_main(params,session):
    url = 'http://weibo.com/'
    headers = {
        'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
        'accept': "text/html, application/xhtml+xml, image/jxr, */*",
        'referer': "http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.18)",
        'accept-encoding': "gzip, deflate, br",
        'accept-language': "zh-Hans-CN,zh-Hans;q=0.8,en-US;q=0.5,en;q=0.3"
    }
    response=session.get(url,headers=headers,params=params)

if __name__=='__main__':
    username='*****' 
    pwd='****'
    comp=compile_js()
    session=requests.session()

    su=get_su(username,comp)
    json_dict=get_prelogin_json(su,session)#获取预登录信息
    sp=get_sp(pwd,json_dict['nonce'],json_dict['servertime'],json_dict['pubkey'],comp)
    print su,sp
    redirect_url=login(su,sp,json_dict,session)
    print redirect_url
    if redirect_url:#登陆成功
        print u'登陆成功'
        ret_dict=redirect(redirect_url,session)
        print ret_dict
        get_main(ret_dict['userinfo']['userdomain'][1:],session)