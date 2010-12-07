#coding=utf-8
import os
import sys
import key
import web
from weibopy.auth import OAuthHandler
from weibopy.api import API
from jinja2 import Environment,FileSystemLoader

#日志对象
def initlog():
    import logging
    logger=logging.getLogger("sina_twitter")
    hd=logging.StreamHandler(sys.stdout)
    fmt = logging.Formatter('%(asctime)s %(levelname)s %(message)s') 
    hd.setFormatter(fmt)
    logger.addHandler(hd)
    logger.setLevel(logging.DEBUG)
    return logger

logger=initlog()

#url映射配置
urls = (
    '/', 'Index',
    '/callback','CallBack',
    '/logout','LogOut'
)

app=web.application(urls,globals())

if web.config.get('_session') is None:
    #web.py中有三种session机制，本应用采用session保存在本地文件的机制
    session = web.session.Session(app,web.session.DiskStore("sina_twitter"))
    web.config._session = session
else:
    session = web.config._session

#使用jinja2模板渲染文件
def render_template(template_name,**context):
    extensions=context.pop('extensions',[])
    globals=context.pop("globals",{})
    jinja_env=Environment(
        loader=FileSystemLoader(os.path.join(os.path.dirname(__file__),'templates')),
        extensions=extensions)   
    jinja_env.globals.update(globals)
    return jinja_env.get_template(template_name).render(context)

#首页
#首先从session中获取access_token，没有就转向新浪微博页面认证
#认证成功后将access_token保存在session中
class Index:    
    def GET(self):
        access_token=session.get('access_token',None)
        if not access_token:
            auth = OAuthHandler(key.CONSUME_KEY, key.CONSUME_SECRET,web.ctx.get('homedomain')+'/callback')
            #获得新浪微博的认证url地址
            auth_url = auth.get_authorization_url()
            logger.debug("认证地址为：%s"%auth_url)
            #在session中保存request_token，用于在新浪微博认证通过后换取access_token
            session.request_token=auth.request_token
            web.seeother(auth_url)
        else:
            auth = OAuthHandler(key.CONSUME_KEY, key.CONSUME_SECRET)
            auth.access_token=access_token
            api=API(auth)
            user=api.verify_credentials()
            friends=api.friends()
            return render_template('index.html',friends=friends,user=user)
            
#页面回调，新浪微博验证成功后会返回本页面
class CallBack:
    def GET(self):
        try:
            ins=web.input()
            oauth_verifier=ins.get('oauth_verifier',None)
            request_token=session.get('request_token',None)
            auth=OAuthHandler(key.CONSUME_KEY, key.CONSUME_SECRET)
            auth.request_token=request_token
            #通过oauth_verifier来获取access_token
            access_token=auth.get_access_token(oauth_verifier)
            session.access_token=access_token
            web.seeother("/")
        except Exception:
            web.header("Content-Type", "text/html;charset=utf-8")
            return ':-( 出错了'

#退出微博，返回到首页    
class LogOut:
    def GET(self):
        del session['access_token']
        del session['request_token']
        web.seeother('/')

if __name__=='__main__':
    logger.debug("web.py服务开始启动……")
    app.run()
    



