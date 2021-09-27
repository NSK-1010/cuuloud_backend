import yaml
with open('../.config/config.yaml') as file:
    conf = yaml.load(file)
db = conf.get('db')
web = conf.get('web')