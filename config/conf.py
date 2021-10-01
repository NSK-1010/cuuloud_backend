import yaml
with open('config/config.yaml') as file:
    conf = yaml.safe_load(file)
db = conf.get('db')
web = conf.get('web')
smtp = conf.get('smtp')