from os import getenv

domain = getenv('DOMAIN')
if getenv('PROTOCOL') and getenv('PROTOCOL') == 'https':
    url = f'https://{domain}/'
else:
    url = f'http://{domain}/'
