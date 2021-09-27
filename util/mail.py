from . import url
templates = {
    'register':'''
Culoudへようこそ。

本サービスへのご登録ありがとうございます。
以下のURLから認証されます。
'''+f'https://{url.url}/#/verify/'+'''{verify_token}
'''
}

def send(email, text):
    pass
def send_template(email, template_name, *args, **kwargs):
    text = templates[template_name].format(**kwargs)
    pass