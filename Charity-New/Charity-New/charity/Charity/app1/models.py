from django.db import models


class Registeration(models.Model):
    name=models.CharField(max_length=30,null=True,blank=True)
    email=models.EmailField(null=True,blank=True)
    mobile=models.PositiveIntegerField(null=True,blank=True)
    password=models.CharField(max_length=8,null=True,blank=True)
    is_verified=models.BooleanField(default=False,null=True,blank=True)



class CategoryType(models.Model):
    name=models.CharField(max_length=50,null=True,blank=True)
    description=models.TextField(null=True,blank=True)
    image=models.ImageField(upload_to='donation/')


class Donation(models.Model):
    user=models.ForeignKey(Registeration,on_delete=models.CASCADE)
    category=models.ForeignKey(CategoryType,on_delete=models.CASCADE)
    Amount=models.IntegerField(null=True,blank=True)
    created_on=models.DateTimeField(auto_now_add=True,null=True,blank=True)

    def __str__(self):
        return str(self.Amount)


class Superuser(models.Model):
    name=models.CharField(max_length=30,null=True,blank=True)
    password=models.CharField(max_length=8,null=True,blank=True)

    def __str__(self):
        return self.name  