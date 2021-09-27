from . import url
templates = {
    'register':'''Culoudへようこそ。

本サービスへのご登録ありがとうございます。
以下のURLへアクセスして認証してください。
'''+f'https://{url.url}/verify/'+'''{verify_token}
'''
}

def send(email, text):
    print(f'to:<{email}>')
    print(text)
def send_template(email, template_name, *args, **kwargs):
    text = templates[template_name].format(**kwargs)
    send(email, text)