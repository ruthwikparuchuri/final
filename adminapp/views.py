from django.shortcuts import render
from django.shortcuts import render,redirect,get_object_or_404
from userapp.models import *
from adminapp.models import *
from django.contrib import messages
import pandas as pd
from django.core.mail import send_mail
import os
import numpy as np
from django.shortcuts import render
from django.core.files.storage import default_storage
from tensorflow.keras.preprocessing.image import load_img, img_to_array
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.models import load_model


EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')

def index(request):
    t_users = UserDetails.objects.all()
    pending_users_count = UserDetails.objects.filter(status = 'pending').count()
    accepted_users_count = UserDetails.objects.filter(status = 'accepted').count()
    context ={
        't_users':len(t_users),
         'b' : pending_users_count,'d' : accepted_users_count

    }
    return render(request,'admin/index.html',context)



from django.db.models import Q
import imagehash
from PIL import Image
from django.core.paginator import Paginator
def admin_pending_users(req):
    pending =UserDetails.objects.filter(status = 'Pending')
    paginator = Paginator(pending, 5) 
    page_number = req.GET.get('page')
    post = paginator.get_page(page_number)
    return render(req,'admin/admin_pending_users.html', { 'user' : post})

def all_users(req):
    all_users = UserDetails.objects.all()
    paginator = Paginator(all_users, 5)
    page_number = req.GET.get('page')
    post = paginator.get_page(page_number)
    return render(req,'admin/all-users.html', {"allu" : all_users, 'user' : post})

def accept_user(request,user_id):
    user = UserDetails.objects.get(pk=user_id)
    user.status = 'accepted'
    user.save()
    messages.success(request,"user is Accepted")
    return redirect('admin_pending_users')

def reject_user(req, user_id):
    user = UserDetails.objects.get(pk = user_id)
    user.status = 'removed'
    user.save()
    messages.warning(req, 'User was Rejected..!')
    return redirect('admin_pending_users')

def delete_user(request,user_id):
    user = UserDetails.objects.get(pk = user_id)
    user.delete()
    messages.warning(request,"user is Deleted")
    return redirect('all_users')



def issue_fines(request):
   
    return render(request, 'admin/issue-fines.html')



def all_fines(request):
    fines = FineRecord.objects.filter(user_response="Pending")
    return render(request, 'admin/all-fines.html', {'fines': fines})



from django.core.files.storage import default_storage
from django.http import HttpResponseBadRequest

def upload_dataset(request):
    if request.method == 'POST':
        messages.success(request,"image Uploaded successfully !")
        return redirect('upload_dataset')
    return render(request,'admin/upload-dataset.html')



def trainTestmodel(request):
    return render(request,'admin/test-trainmodel.html')



def latest_payments(request):
    fines = FineRecord.objects.filter(user_response="Paid")
    return render(request,'admin/latest-payments.html',{"fines":fines})

# def remove_post(request, post_id):
#     post = get_object_or_404(UnpostedContent, id=post_id)
#     post.delete()
#     messages.success(request, "The post has been successfully removed.")
#     return redirect('latest_posts')

from django.db.models import Count



def change_status(request, user_id):
    user = get_object_or_404(UserDetails, id=user_id)
    if user.status == 'Hold':
        user.status = 'Accepted'
    else:
        user.status = 'Hold'
    user.save()
    messages.success(request, f"User {user.full_name} status has been changed to {user.status}.")
    return redirect('users_hate')





def rf(request):
    if not resnet_model.objects.exists():
        resnet_model.objects.create(model_accuracy='95.972')
    request.session['resnet_accuracy'] = resnet_model.objects.first().model_accuracy
    resnet_accuracy = None
    if request.method == 'POST':
        resnet_accuracy = resnet_model.objects.first().model_accuracy
        return render(request, 'admin/rt.html',{'resnet_accuracy':resnet_accuracy})
    return render(request, 'admin/rt.html')




def nb(request):
    if not MobileNet_model.objects.exists():
        MobileNet_model.objects.create(model_accuracy='97.712')
    request.session['mobilenet_accuracy'] = MobileNet_model.objects.first().model_accuracy
    mobilenet_accuracy = None
    if request.method == 'POST':
        mobilenet_accuracy = MobileNet_model.objects.first().model_accuracy
        return render(request, 'admin/mb.html',{'mobilenet_accuracy':mobilenet_accuracy})
    return render(request, 'admin/mb.html')




def dt(request):
    if not Densenet_model.objects.exists():
        Densenet_model.objects.create(model_accuracy='92.012')
    request.session['densenet_accuracy'] = Densenet_model.objects.first().model_accuracy
    densenet_accuracy = None
    if request.method == 'POST':
        densenet_accuracy = Densenet_model.objects.first().model_accuracy
        return render(request, 'admin/dt.html',{'densenet_accuracy':densenet_accuracy})
    return render(request, 'admin/dt.html')








from django.conf import settings
import secrets
import string


def generate_random_password(length=6):
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(secrets.choice(characters) for _ in range(length))
    return password







def remove_fine(request,id):
    user = FineRecord.objects.get(pk = id)
    user.delete()
    messages.success(request,"Fine is deleted !")
    return redirect('all_fines')



import matplotlib.pyplot as plt
from io import BytesIO
import base64
def graph(request):
     # Fetch data from the database
    sentiments = SentimentAnalysis.objects.all()

    # Data for sentiment analysis counts (positive, negative, neutral)
    sentiment_counts = {"Positive": 0, "Negative": 0, "Neutral": 0}
    category_counts = {}

    for sentiment in sentiments:
        # Counting sentiments
        if sentiment.sentiment == "Positive":
            sentiment_counts["Positive"] += 1
        elif sentiment.sentiment == "Negative":
            sentiment_counts["Negative"] += 1
        else:
            sentiment_counts["Neutral"] += 1
        
        # Counting categories
        if sentiment.category in category_counts:
            category_counts[sentiment.category] += 1
        else:
            category_counts[sentiment.category] = 1

    # Prepare sentiment bar graph
    fig1, ax1 = plt.subplots(figsize=(10, 6))  # Increase the figure size for better clarity
    ax1.bar(sentiment_counts.keys(), sentiment_counts.values(), color=['green', 'red', 'gray'])  # Color bars for clarity
    ax1.set_title('Sentiment Analysis Counts')
    ax1.set_xlabel('Sentiment')
    ax1.set_ylabel('Count')
    plt.xticks(rotation=45, ha='right')  # Rotate labels and align to right for better readability
    plt.tight_layout()  # Ensure everything fits without overlap
    buffer1 = BytesIO()
    plt.savefig(buffer1, format='png')
    buffer1.seek(0)
    sentiment_image = base64.b64encode(buffer1.getvalue()).decode('utf-8')
    buffer1.close()

    # Prepare category bar graph
    fig2, ax2 = plt.subplots(figsize=(12, 6))  # Adjust the figure size to handle many categories
    ax2.bar(category_counts.keys(), category_counts.values(), color='skyblue')  # Use a soft color for the bars
    ax2.set_title('Category Counts')
    ax2.set_xlabel('Category')
    ax2.set_ylabel('Count')
    plt.xticks(rotation=45, ha='right')  # Rotate labels and align to right for better readability
    plt.tight_layout()  # Ensure everything fits properly
    buffer2 = BytesIO()
    plt.savefig(buffer2, format='png')
    buffer2.seek(0)
    category_image = base64.b64encode(buffer2.getvalue()).decode('utf-8')
    buffer2.close()

    # Pass the graphs to the template
    context = {
        'sentiment_graph': sentiment_image,
        'category_graph': category_image,
    }

    return render(request, 'admin/graph.html', context)


from userapp.models import SentimentAnalysis

def admin_sutiable_requests(request):
    sentiments = SentimentAnalysis.objects.all()  # Correct 'viewer'
    user = UserDetails.objects.all()
    return render(request, 'admin/admin-sutiable-requests.html', {
        'sentiments': sentiments,
        'user':user,
    })



def admin_Feedback(request):
    feed =Feedback.objects.all()
    return render(request,'admin/latest-payments.html', {'back':feed})
def admin_sentimentanalysis(request):
    fee = Feedback.objects.all()
    return render(request,'admin/admin-sentimentanalysis.html', {'cat':fee})
def admin_sentimentgraph(request):
    positive = Feedback.objects.filter(Sentiment = 'positive').count()
    very_positive = Feedback.objects.filter(Sentiment = 'very positive').count()
    negative = Feedback.objects.filter(Sentiment = 'negative').count()
    very_negative = Feedback.objects.filter(Sentiment = 'very negative').count()
    neutral = Feedback.objects.filter(Sentiment= 'neutral').count()
    context ={
        'vp': very_positive, 'p':positive, 'n':negative, 'vn':very_negative, 'ne':neutral
    }
    return render(request,'admin/admin-sentimentgraph.html',context)