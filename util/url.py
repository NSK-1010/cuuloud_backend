from config import conf

domain = conf.web.get('domain')
if conf.web.get('ssl'):
    url = f'https://{domain}/'
else:
    url = f'http://{domain}/'
