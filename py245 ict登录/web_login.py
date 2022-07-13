import requests

USER_IP = ''
USERNAME = ''
PASSWORD = ''


session = requests.Session()
r = session.get('https://gw.ict.ac.cn/srun_portal_pc.php')
print (r.text)
payload = {'action':'login', 'ac_id':'1', 'user_ip': USER_IP, 'nas_ip':'', 'user_mac':'', 'url':'', 'username': USERNAME, 'password': PASSWORD}
r = session.post('https://gw.ict.ac.cn/srun_portal_pc.php', data=payload)
