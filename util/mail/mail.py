
def send(email, text):
    print(f'to:<{email}>')
    print(text)

def send_template(email, template_name, *args, **kwargs):
    f=open(f'{template_name}.html','r')
    text = f.read()
    text = text.format(**kwargs)
    send(email, text)