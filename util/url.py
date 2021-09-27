from util import conf

domain = conf.web.get('domain')
if conf.web.ssl:
    url = f'https://{domain}/'
else:
    url = f'http://{domain}/'
