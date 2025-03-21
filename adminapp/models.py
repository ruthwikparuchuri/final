from django.db import models
from django.utils import timezone

# Create your models here.
class Dataset(models.Model):
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='datasets/')
    uploaded_at = models.DateTimeField(auto_now_add=True) 
  
    class Meta:
        db_table = 'dataset_table'


class UserDetails(models.Model):
    user_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    user_password = models.TextField(help_text='user_password', max_length=50)
    photo = models.ImageField(upload_to='user_photos/')
    address = models.TextField()
    phone_number = models.CharField(max_length=15)
    status = models.CharField(max_length=15, default='Pending')
    otp_num = models.IntegerField()  # Field to store generated OTP
    Otp_Status = models.TextField(default='pending', max_length=60, null=True)

    def __str__(self):
        return self.user_name

    



class FineRecord(models.Model):
    user = models.ForeignKey(UserDetails, on_delete=models.CASCADE, related_name='fines')
    fine_image = models.ImageField(upload_to='fine_images/')
    fine_amount = models.DecimalField(max_digits=10, decimal_places=2)
    issued_at = models.DateTimeField(default=timezone.now)
    paid_at = models.DateTimeField(default=timezone.now)
    user_response = models.CharField(max_length=50, default='Pending')

    def __str__(self):
        return f'Fine for {self.user.user_name} - Amount: {self.fine_amount}'
    



class Densenet_model(models.Model):
    S_No = models.AutoField(primary_key=True)
    model_accuracy = models.CharField(max_length=10, default='85.0') 

    class Meta:
        db_table = "Densenet_model"

class MobileNet_model(models.Model):
    S_No = models.AutoField(primary_key=True)
    model_accuracy = models.CharField(max_length=10, default='90.0')  

    class Meta:
        db_table = "MobileNet_model"

class resnet_model(models.Model):
    S_No = models.AutoField(primary_key=True)
    model_accuracy = models.CharField(max_length=10, default='88.0')  

    class Meta:
        db_table = "resnet_model"


class Feedback(models.Model):
    Feed_id = models.AutoField(primary_key=True)
    Rating=models.CharField(max_length=100,null=True)
    Review=models.CharField(max_length=225,null=True)
    Sentiment=models.CharField(max_length=100,null=True)
    Reviewer=models.ForeignKey(UserDetails, on_delete=models.CASCADE,null=True)
    datetime=models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'feedback_details'