# -*- coding: utf-8 -*-
from wordpress_xmlrpc import Client
from wordpress_xmlrpc.compat import xmlrpc_client
from wordpress_xmlrpc.methods import posts,media
import re
import random
import datetime
import pytz
import base64
import qrcode

#SS配置
#password = 'yourpassword'
#ip_address = 'serverip'

#SSR配置
ip_address = 'serverip'
password = base64.urlsafe_b64encode(('yourpassword').encode(encoding="utf-8")).decode().replace('=','')
protocol = 'auth_chain_a'
method = 'none'
obfs = 'tls1.2_ticket_auth'
obfsparam = ''
remarks = 'alaya'
group = 'moe'

#获取时间
nowtime = datetime.datetime.now(pytz.timezone('Asia/Shanghai'))
print("现在时间:"+nowtime.strftime('%Y-%m-%d %H:%M:%S'))
#文件路径

_ssConfigPath = "/etc/shadowsocks.json"
_iptabelPath = "/etc/sysconfig/iptables"
_firewalldPath = "/etc/firewalld/zones/public.xml"

logPath="updateLog.txt"

#编辑SS配置文件
txt= open(_ssConfigPath,"r")
conifgtext = txt.read()
txt.close()

randomnum = random.randint(30000,50000).__str__()
pattern = '\"server_port\":([0-9]+),'
replacetext='\"server_port\":' + randomnum + ','
lastport = re.search(pattern, conifgtext).group(1)

txt= open(_ssConfigPath,"w")
txt.write(re.sub(pattern,replacetext, conifgtext))
txt.close()
print("修改SS配置文件成功！")
print("配置端口:" + lastport)

#编辑防火墙配置文件
txt= open(_firewalldPath,"r")
conifgtext=txt.read()
txt.close()

pattern1 = '<port protocol=\"tcp\" port=\"' + lastport + '\"/>'
replacetext1 = '<port protocol=\"tcp\" port=\"' + randomnum + '\"/>'

pattern2 = '<port protocol=\"udp\" port=\"' + lastport + '\"/>'
replacetext2 = '<port protocol=\"udp\" port=\"' + randomnum + '\"/>'

conifgtext = re.sub(pattern1,replacetext1, conifgtext)
conifgtext = re.sub(pattern2,replacetext2, conifgtext)

txt= open(_firewalldPath,"w")
txt.write(conifgtext)
txt.close()
print("修改防火墙文件成功！\n")

#SSlink
#base64_str = ('aes-256-cfb:' + password + '@' + ip_address +':' + randomnum).encode(encoding="utf-8")
#encodestr = base64.b64encode(base64_str)
#shareqrcode_str = 'ss://' + encodestr.decode()

#SSRlink
main_part = ip_address + ":" + randomnum + ":" + protocol + ":" + method + ":" + obfs + ":" + password
param_str = 'obfsparam=' + base64.urlsafe_b64encode(obfsparam.encode(encoding="utf-8")).decode().replace('=','')\
+'&remarks=' + base64.urlsafe_b64encode(remarks.encode(encoding="utf-8")).decode().replace('=','')\
+'&group=' + base64.urlsafe_b64encode(group.encode(encoding="utf-8")).decode().replace('=','')

shareqrcode_str = "ssr://"+base64.urlsafe_b64encode((main_part + "/?" + param_str).encode(encoding="utf-8")).decode().replace('=','');


#生成二维码
qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_M,
    box_size=8,
    border=4,
)
filename = 'qrcode.png'
qr.add_data(shareqrcode_str)
qr.make(fit=True)
img = qr.make_image()
img.save(filename)
print(shareqrcode_str)

####################
#获取服务器
client = Client("http://www.alaya.moe/xmlrpc.php","WordPressUserName","WordPressPassword")


#上传二维码
data = {
        'name': 'qrcode' + nowtime.strftime('%Y-%m-%d') + '.jpg',
        'type': 'image/jpeg',  # mimetype
}

with open(filename, 'rb') as img:
        data['bits'] = xmlrpc_client.Binary(img.read())

response = client.call(media.UploadFile(data))

#更新wordpress文章
post = client.call(posts.GetPost(171))

post.title = '科学上网账号('+nowtime.strftime('%Y-%m-%d %H')+'点更新)'

pattern = '服务器端口：(\d+)'
replacetext = '服务器端口：' + randomnum
post.content = re.sub(pattern,replacetext, post.content)

pattern = '最新更新时间:([\d -/:]+)'
replacetext = '最新更新时间: '+ nowtime.strftime('%Y-%m-%d %H:%M:%S')
post.content = re.sub(pattern,replacetext, post.content)

# 更新快捷导入
pattern = "\[<img src=\"http://www.alaya.moe/wp-content/uploads/2017/03/import.png\"/>\]\((.+)\)"
replacetext = "[<img src=\"http://www.alaya.moe/wp-content/uploads/2017/03/import.png\"/>]("+shareqrcode_str+")"
post.content = re.sub(pattern,replacetext, post.content)

pattern = '<img src="(.+)" alt="二维码" />'
replacetext = '<img src="'+ response['url']+'" alt="二维码" />'
post.content = re.sub(pattern,replacetext, post.content)

post.thumbnail = response['id']

client.call(posts.EditPost(171,post))

print("wordpess文章更新成功！")
print("新的端口号:"+randomnum)

#写入记录
logfile=open(logPath,'a')
logfile.write('更新时间: '+ nowtime.strftime('%Y-%m-%d %H:%M:%S' )+ ' ' +randomnum + '\n')
logfile.close()
