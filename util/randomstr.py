import random, string

def randomstr(n):
   return ''.join(random.choices(string.ascii_letters + string.digits, k=n))