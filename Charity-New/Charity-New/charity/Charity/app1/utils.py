import random,string
def generate_pass():
    num=string.digits
    temp=''.join(random.choice(num) for i in range(6))
    return temp