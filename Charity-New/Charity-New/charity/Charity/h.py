import random,string
num=string.digits
temp=''.join(random.choice(num) for i in range(6))
print(temp)