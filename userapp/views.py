from django.shortcuts import render,redirect,get_object_or_404
from django.contrib import messages
from adminapp.models import *
from datetime import date
import urllib.request
import urllib.parse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import random
from django.contrib.auth import logout
from django.core.mail import send_mail
import os
import random
from django.conf import settings
from userapp.models import *
from adminapp.models import *


# Create your views here.

def user_logout(request):
    logout(request)
    messages.info(request, "Logout Successfully ")
    return redirect("user_login")


# Create your views here.




EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')






def generate_otp(length=4):
    otp = "".join(random.choices("0123456789", k=length))
    return otp



def index(request):
    return render(request,"user/index.html")


def about(request):
    return render(request,"user/about.html")

def pending_users(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        password = request.POST.get('password')
        email = request.POST.get('email')
        address = request.POST.get('address')
        contact = request.POST.get('number')
        image = request.FILES.get('photo')
        print(name, password, email, address, contact, image)

        # Generate OTP
        otp_number = random.randint(1000, 9999)
        print(f"Generated OTP: {otp_number}")

        try:
            # Create a user
            user = UserDetails.objects.create(
                user_name=name,
                user_password=password,
                email=email,
                address=address,
                phone_number=contact,
                photo=image,
                otp_num=otp_number,
            )
            user.save()
            request.session["user_email"] = user.email
            request.session["name"] = user.user_name
            request.session.modified = True
            print(f"Email stored in session: {request.session.get('user_email')}")

            # Send OTP email
            subject = "Your OTP for Account Verification"
            message = f"""
            Dear {name},

            Thank you for registering on our platform. Your OTP for account verification is:

            {otp_number}

            Please use this code to verify your account.

            Best regards,
            Smokeaware Team
            """
            from_email = settings.EMAIL_HOST_USER
            recipient_list = [email]
            send_mail(subject, message, from_email, recipient_list, fail_silently=False)
            messages.success(request, 'User registered successfully. OTP sent to your email.')
            return redirect('otp_verification')
           

        except Exception as e:
            print(f"Error creating user: {e}")
            messages.error(request, 'Failed to register user. Please try again.')
            return redirect('pending_users')

    return render(request, 'user/register-users.html')

def otp_verification(request):
    user_email = request.session.get('user_email')  # Use .get() to avoid KeyError
    if not user_email:
        messages.error(request, "Session expired. Please log in again.")
        return redirect("user_login")
    
    try:
        user_o = UserDetails.objects.get(email=user_email)
    except UserDetails.DoesNotExist:
        messages.error(request, "User not found. Please register again.")
        return redirect("pending_users")

    if request.method == 'POST':
        user_otp = request.POST.get('otp')
        if int(user_otp) == user_o.otp_num:
            user_o.Otp_Status = 'verified'
            user_o.save()
            messages.success(request, "OTP verification successful.")
            return redirect("user_login")
        else:
            messages.error(request, "Invalid OTP.")
            return redirect("otp_verification")

    return render(request, "user/otp_verification.html")


def user_login(request):
    if request.method == 'POST':
        user_email = request.POST.get('email')
        user_password = request.POST.get('password')

        try:
            user_data = UserDetails.objects.get(email=user_email)
        except UserDetails.DoesNotExist:
            messages.error(request, "User does not exist. Please register.")
            return redirect("pending_users")

        if user_data.user_password == user_password:
            if user_data.Otp_Status == 'verified':
                if user_data.status == 'accepted':
                    request.session['user_id'] = user_data.id
                    request.session['user_email'] = user_data.email  # Store session
                    messages.success(request, "Login successful.")
                    return redirect("user_dashboard")
                else:
                    messages.info(request, "Your account is still pending approval.")
                    return redirect("user_login")
            else:
                messages.warning(request, "Please verify your OTP first.")
                request.session['user_email'] = user_data.email
                return redirect("otp_verification")
        else:
            messages.error(request, "Incorrect credentials.")
            return redirect("user_login")

    return render(request, "user/user-login.html")






from django.utils.datastructures import MultiValueDictKeyError


def user_profile(req):
    user_email = req.session["user_email"]
    user = UserDetails.objects.get(email = user_email)
    if req.method == 'POST':
        user_name = req.POST.get('name')
        user_password = req.POST.get('password')
        user_phone = req.POST.get('phone')
        user_email = req.POST.get('email')
        user_address = req.POST.get("add")
        
        # user_img = request.POST.get("userimg")
        
        user.user_name = user_name
        user.user_password = user_password
        user.address = user_address
        user.phone_number = user_phone
        user.email=user_email
       

        if len(req.FILES) != 0:
            image = req.FILES['profilepic']
            user.photo = image
            user.user_name = user_name
            user.phone_number = user_phone
            user.email=user_email
            user.address = user_address
            user.save()
            messages.success(req, 'Updated SUccessfully...!')
        else:
            user.user_name = user_name
            user.phone_number = user_phone
            user.save()
            messages.success(req, 'Updated SUccessfully...!')
            
    context = {"i":user}
    
    return render(req, 'user/user-profile.html', context)




def admin_login(request):
    if request.method == 'POST':
        username = request.POST.get('name')
        password = request.POST.get('password')
        if username == 'admin' and password == 'admin':
            messages.success(request, 'Login Successful')
            return redirect('admin_dashboard')
        else:
            messages.error(request, 'Invalid Login Credentials')
            return redirect('admin_login')
    return render(request,"user/admin-login.html")


def contact(request):
    return render(request,"user/contact.html")


def pay_fine(request, id):
    details = FineRecord.objects.get(pk=id)
    request.session['details'] = id
    print(details.fine_amount,"hererererer")
    return render(request, "user/payment.html", {'details': details})


def user_dashboard(request):
    return render(request,"user/user-dashboard.html")


def view_and_pay(request):
    user_id = request.session.get('user_id_after_login')
    user = get_object_or_404(UserDetails, id=user_id)
    pending_fines = FineRecord.objects.filter(user=user, user_response='Pending')

    return render(request, "user/view-pay.html", {'pending_fines': pending_fines})


def payment(request):
    return render(request,"user/payment.html")









import pickle
from django.shortcuts import render
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

# Path to the dataset and machine learning model
DATASET_PATH = "detection/weather_clean.csv"
MODELS_PATH = 'detection/rfc_w.pkl'

# Weather class mapping with descriptions
WEATHER_CLASSES = {
    0: (
        "Fog", 
        """
        **Weather Beauty:** Fog creates a mystical and serene atmosphere, often making landscapes look dreamy and enchanting. It's a great time for photography enthusiasts to capture nature's beauty in its most mysterious form.
        
        **Precautions:** Drive carefully, use fog lights, and avoid high-speed driving. Ensure your vehicle's headlights are on low beam to avoid glare.
        """
    ),
    1: (
        "Cloudy", 
        """
        **Weather Beauty:** Cloudy skies add a dramatic touch to the horizon, creating a cozy and calm environment. It's a perfect time to enjoy a cup of coffee while gazing at the sky.
        
        **Precautions:** It might rain, so keep an umbrella or raincoat handy. Wear waterproof shoes to avoid discomfort if it starts drizzling.
        """
    ),
    2: (
        "Rain", 
        """
        **Weather Beauty:** Rain brings freshness to the air and rejuvenates nature. The sound of raindrops can be soothing, and the sight of wet greenery is truly refreshing.
        
        **Precautions:** Wear waterproof clothing and avoid slippery surfaces. Carry an umbrella or raincoat, and avoid low-lying areas prone to waterlogging.
        """
    ),
    3: (
        "Clear", 
        """
        **Weather Beauty:** Clear skies offer bright sunlight, making it an ideal day for outdoor activities like picnics, hiking, or simply enjoying nature's beauty. The vibrant blue sky uplifts your mood.
        
        **Precautions:** Stay hydrated if it's warm. Use sunscreen to protect your skin from UV rays, and wear sunglasses to shield your eyes.
        """
    ),
    4: (
        "Snow", 
        """
        **Weather Beauty:** Snow transforms landscapes into a winter wonderland with its pristine white beauty. It's perfect for activities like skiing, snowball fights, or simply enjoying the serene snowfall.
        
        **Precautions:** Wear warm clothes, including gloves and boots, to stay protected from the cold. Be cautious while driving or walking on icy roads to avoid accidents.
        """
    ),
    5: (
        "Drizzle", 
        """
        **Weather Beauty:** Drizzle creates a light and romantic ambiance, perfect for taking a walk or enjoying the soft pitter-patter of raindrops. The cool breeze adds to the charm of this weather.
        
        **Precautions:** Carry a light umbrella or raincoat. Avoid staying out too long if it's chilly, as prolonged exposure might make you uncomfortable.
        """
    ),
    6: (
        "Haze", 
        """
        **Weather Beauty:** Haze gives the surroundings a muted and soft appearance, creating an almost surreal view of distant objects. It can make mornings look calm and peaceful.
        
        **Precautions:** Avoid outdoor activities if you have respiratory issues or allergies. Use air purifiers indoors and wear a mask if stepping outside is necessary.
        """
    ),
    7: (
        "Thunderstorms", 
        """
        **Weather Beauty:** Thunderstorms showcase nature's raw power with dramatic lightning strikes and roaring thunder. For some, it's an awe-inspiring spectacle of nature's energy.
        
        **Precautions:** Stay indoors during thunderstorms. Avoid open areas, tall trees, or metal objects that can attract lightning. Unplug electronic devices to prevent damage from power surges.
        """
    )
}









import requests
from django.shortcuts import render
from datetime import datetime

def weather(request):
    weather_data = None
    error_message = None  # Set the error_message to None by default in case there's no error
    if request.method == 'POST':
        location = request.POST.get('location')
        date_str = request.POST.get('date')
        time_str = request.POST.get('hour')

        print(f"Location: {location}")
        print(f"Date selected: {date_str}")
        print(f"Time selected: {time_str}")

        if not time_str:
            print("Error: Time is missing from the form submission.")
            error_message = "Please select an hour."
            return render(request, 'user/user-weather.html', {'error_message': error_message})

        # Handle time and date conversion
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            time_obj = datetime.strptime(time_str, '%H:%M').time()
            print(f"Parsed date: {date_obj}")
            print(f"Parsed time: {time_obj}")

            # Combine date and time to form a datetime object
            selected_datetime = datetime.combine(date_obj, time_obj)
            print(f"Selected datetime: {selected_datetime}")
        except ValueError as e:
            print(f"Error parsing date or time: {e}")
            error_message = "Invalid date or time format."
            return render(request, 'user/user-weather.html', {'error_message': error_message})

        # OpenWeatherMap API endpoint for 5-day forecast
        api_key = '8bc00b70a23cc182c2cf8d34cce0d184'
        url = f'http://api.openweathermap.org/data/2.5/forecast?q={location}&appid={api_key}&units=metric'

        response = requests.get(url)
        data = response.json()

        print(f"API Response: {data}")  # Debugging the API response

        if data.get('cod') == '200':
            # Find the forecast for the selected date and time
            for forecast in data['list']:
                forecast_date = datetime.utcfromtimestamp(forecast['dt'])
                print(f"Forecast date and time: {forecast_date}")

                if forecast_date.date() == selected_datetime.date() and forecast_date.hour == selected_datetime.hour:
                    # Convert temperature to Fahrenheit
                    temperature_celsius = forecast['main']['temp']
                    temperature_fahrenheit = (temperature_celsius * 9/5) + 32
                    weather_data = {
                        'city_name': data['city']['name'],
                        'date': forecast_date.strftime('%Y-%m-%d'),
                        'time': forecast_date.strftime('%H:%M'),
                        'temperature_celsius': temperature_celsius,
                        'temperature_fahrenheit': temperature_fahrenheit,
                        'weather_description': forecast['weather'][0]['description'],
                        'humidity': forecast['main']['humidity'],
                        'wind_speed': forecast['wind']['speed'],
                        'visibility': forecast.get('visibility', 'N/A'),
                        'rain': forecast.get('rain', {}).get('3h', 'N/A'),
                        'snow': forecast.get('snow', {}).get('3h', 'N/A'),
                    }

                    # Print all weather data details
                    print(f"Weather Data for {weather_data['city_name']} on {weather_data['date']} at {weather_data['time']}:")
                    print(f"Temperature (Celsius): {weather_data['temperature_celsius']}")
                    print(f"Temperature (Fahrenheit): {weather_data['temperature_fahrenheit']}")
                    print(f"Weather description: {weather_data['weather_description']}")
                    print(f"Humidity: {weather_data['humidity']}")
                    print(f"Wind Speed: {weather_data['wind_speed']}")
                    print(f"Visibility: {weather_data['visibility']}")
                    print(f"Rain (last 3 hours): {weather_data['rain']}")
                    print(f"Snow (last 3 hours): {weather_data['snow']}")
                    break

    return render(request, 'user/user-weather.html', {'weather_data': weather_data, 'error_message': error_message})





def weather_location(location, predicted_weather, description):
    # Get all users with the same address (location)
    users_in_location = UserDetails.objects.filter(address=location)

    # Prepare the subject and message
    subject = f"weather Prediction: - {predicted_weather}"
    message = f"Dear User, \n\nYour location has a predicted weather  of {predicted_weather}. \nPrediction Description: {description}\n\nStay safe!"

    # Get sender email from settings
    from_email = settings.EMAIL_HOST_USER

    # Extract emails of all users in the same location
    recipient_list = users_in_location.values_list('email', flat=True)

    if recipient_list:
        # Send the email to all the users in the same location
        send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=recipient_list,
            fail_silently=False,
        )
    else:
        print(f"No users found in the location: {location}")

def final_payment(request):
    if request.method == 'POST':
        fine_record_id = request.POST.get('fine_record_id')
        if fine_record_id:
            fine_record = get_object_or_404(FineRecord, pk=fine_record_id)
            fine_record.user_response = 'Paid'
            fine_record.paid_at = timezone.now()
            fine_record.save()
            subject = "Fine Payment Confirmation"
            message = f"""
            Dear {fine_record.user.user_name},
            We are pleased to inform you that your fine has been successfully paid. Below are the details of the fine:
            - Fine Amount: {fine_record.fine_amount}
            - Date Issued: {fine_record.issued_at.strftime('%Y-%m-%d %H:%M:%S')}
            - Payment Date: {fine_record.paid_at.strftime('%Y-%m-%d %H:%M:%S')}
            Thank you for your prompt payment. If you have any questions or require further information, please contact us.
            Best regards,
            Smokedetection Team
            """
            from_email = settings.EMAIL_HOST_USER
            recipient_list = [fine_record.user.email]
            send_mail(subject, message, from_email, recipient_list, fail_silently=False)
            messages.success(request, 'Payment successful!')
        else:
            messages.error(request, 'Invalid request. No record ID provided.')
    else:
        messages.error(request, 'Invalid request method.')

    return redirect('view_and_pay')
    
    

import pickle
from django.shortcuts import render
from django.contrib import messages
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import numpy as np

# Path to the dataset and machine learning model
DATASET_PATH = "detection\flood_prediction\flood.csv"  # Update with your flood dataset path
MODEL_PATHSS = 'detection\linear.pkl'   # Update with your trained flood model pat


def get_flood_description(value):
    # Your existing function to map flood risk values to descriptions
    if value == 0.285:
        return "Low flood risk: Minimal water levels detected."
    elif value == 0.315:
        return "Low flood risk: Slight increase in water levels."
    elif value == 0.32:
        return "Low flood risk: Water levels remain manageable."
    elif value == 0.325:
        return "Low flood risk: No significant danger."
    elif value == 0.33:
        return "Low flood risk: Stable conditions."
    elif value == 0.335:
        return "Low flood risk: Slight monitoring required."
    elif value == 0.34:
        return "Low flood risk: Water levels are safe."
    elif value == 0.345:
        return "Low flood risk: No immediate action needed."
    elif value == 0.35:
        return "Low flood risk: Monitor regularly for changes."
    elif value == 0.355:
        return "Low flood risk: Stay informed about weather updates."
    elif value == 0.36:
        return "Low flood risk: Conditions are stable but monitor closely."
    elif value == 0.365:
        return "Low flood risk: Minimal concern, but stay alert."
    elif value == 0.37:
        return "Low flood risk: No immediate action required, but monitor conditions."
    elif value == 0.375:
        return "Low flood risk: Keep an eye on water levels in your area."
    elif value == 0.38:
        return "Low flood risk: Conditions are manageable, no action needed."
    elif value == 0.385:
        return "Low flood risk: Stay updated with local advisories."
    elif value == 0.39:
        return "Low flood risk: Monitor for any changes in water levels."

    # Medium range
    elif value == 0.395:
        return "Medium flood risk: Increased water levels, monitoring advised."
    elif value == 0.4:
        return "Medium flood risk: Prepare for potential localized flooding."
    elif value == 0.405:
        return "Medium flood risk: Rising water levels, stay alert and prepared."
    elif value == 0.41:
        return "Medium flood risk: Increased chance of flooding in low-lying areas."
    elif value == 0.415:
        return "Medium flood risk: Stay informed and prepare emergency supplies."
    elif value == 0.42:
        return "Medium flood risk: Potential for localized flooding, avoid unnecessary travel."
    elif value == 0.425:
        return "Medium flood risk: Rising water levels, monitor closely and prepare."
    elif value == 0.435:
        return "Medium flood risk: Be cautious in areas prone to flooding."
    elif value == 0.44:
        return "Medium flood risk: Flooding is possible; take precautionary measures."
    elif value == 0.445:
        return "Medium flood risk: Prepare for potential evacuation if necessary."
    elif value == 0.45:
        return "Medium flood risk: Rising water levels; avoid low-lying areas if possible."
    elif value == 0.455:
        return "Medium flood risk: Stay updated on weather forecasts and advisories."
    elif value == 0.46:
        return "Medium flood risk: Be ready to act if conditions worsen."
    elif value == 0.465:
        return "Medium flood risk: Monitor conditions and prepare emergency plans."
    elif value == 0.47:
        return "Medium flood risk: Localized flooding may occur; stay vigilant."

    # High range
    elif value == 0.605:
        return "High flood risk: Significant water levels, action required immediately."
    elif value == 0.61:
        return "High flood risk: Severe flooding likely; move to higher ground if needed."
    elif value == 0.615:
        return "High flood risk: Evacuate if advised by local authorities immediately."
    elif value == 0.625:
        return "High flood risk: Critical conditions; avoid all flooded areas completely."
    elif value == 0.63:
        return "High flood risk: Severe flooding expected; prioritize safety and evacuation plans."
    elif value == 0.635:
        return "High flood risk: Dangerous water levels; follow emergency protocols strictly."
    elif value == 0.64:
        return "High flood risk: Immediate action required; move to safe zones promptly."
    elif value == 0.645:
        return "High flood risk: Extreme flooding likely; ensure safety of all individuals."

    # Default case if the input doesn't match any predefined values
    else:
        return "No Flood Had Been Detected"


from django.core.mail import send_mail
from django.conf import settings



def flood_prediction(req):
    if req.method == 'POST':
        # Collect input data from the form (without the location)
        monsoon_intensity = req.POST.get('monsoon_intensity')
        topography_drainage = req.POST.get('topography_drainage')
        deforestation = req.POST.get('deforestation')
        urbanization = req.POST.get('urbanization')
        siltation = req.POST.get('siltation')
        drainage_systems = req.POST.get('drainage_systems')

        # Convert inputs to appropriate data types
        input_data = [
            [
                int(monsoon_intensity), int(topography_drainage),
                int(deforestation), int(urbanization), int(siltation), 
                int(drainage_systems),
            ]
        ]

        # Load the trained machine learning model
        with open(MODEL_PATHSS, 'rb') as file:
            loaded_model = pickle.load(file)

            # Make a prediction using the model
            res = loaded_model.predict(input_data)  
            result_value = round(float(res[0]), 3)  

            # Get the description for the predicted result
            description = get_flood_description(result_value)

            # Display messages based on prediction
            messages.success(req, f"The predicted flood severity is {description}")

            print("Session Contents:", req.session.items())
            
            # Get the user's email and address
            user_email = req.session.get("user_email")
            if user_email:
                # Fetch the logged-in user's address from the database
                user = UserDetails.objects.get(email=user_email)
                user_address = user.address  # Get the address associated with the user

                # Check if flood prediction email has already been sent (store a flag in the session)
                if not req.session.get('flood_prediction_email_sent', False):
                    subject = f"Flood Severity Prediction: {result_value}"
                    message = f"Your flood prediction is {result_value}. A new flood prediction description: {description}"
                    from_email = settings.EMAIL_HOST_USER
                    recipient_list = [user_email]  # Use the user's email from session

                    send_mail(
                        subject=subject,
                        message=message,
                        from_email=from_email,
                        recipient_list=recipient_list,
                        fail_silently=False,
                    )

                    # Update session to prevent sending email again
                    req.session['flood_prediction_email_sent'] = True

                # Notify all users with the same location (address) about the flood prediction
                notify_users_in_location(user_address, result_value, description)

            else:
                messages.error(req, "User email not found in session.")

            context1 = {
                'prediction': result_value,
                'description': description,
            }

            # Render results on a specific page (e.g., user-flood.html)
            return render(req, "user/user-flood.html", context1)

    # Render initial page for input collection
    return render(req, "user/user-flood.html")



def notify_users_in_location(location, result_value, description):
    # Get all users with the same address (location)
    users_in_location = UserDetails.objects.filter(address=location)

    # Prepare the subject and message
    subject = f"Flood Prediction: Severity Value - {result_value}"
    message = f"Dear User, \n\nYour location has a predicted flood severity of {result_value}. \nPrediction Description: {description}\n\nStay safe!"

    # Get sender email from settings
    from_email = settings.EMAIL_HOST_USER

    # Extract emails of all users in the same location
    recipient_list = users_in_location.values_list('email', flat=True)

    if recipient_list:
        # Send the email to all the users in the same location
        send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=recipient_list,
            fail_silently=False,
        )
    else:
        print(f"No users found in the location: {location}")


import pickle
from django.shortcuts import render
from django.contrib import messages
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

# Path to the dataset and machine learning model
DATASET_PATH = "detection/earthquake/earth_clean.csv"
MODEL_PATH = 'detection/earthquake/xbg_earth.pkl'

# Earthquake magnitude class mapping with descriptions
MAGNITUDE_CLASSES = {
    0: (
        "Micro Earthquake",
        """
        **Description:** Micro earthquakes are very small events typically not felt by humans but recorded by seismographs.
        
        **Precautions:** No precautions needed.
        """
    ),
    1: (
        "Minor Earthquake",
        """
        **Description:** Minor earthquakes are small events often felt locally but rarely cause any damage.
        
        **Precautions:** Stay calm and avoid panic. No major actions required.
        """
    ),
    2: (
        "Light Earthquake",
        """
        **Description:** Light earthquakes may be felt by people but are unlikely to cause significant damage.
        
        **Precautions:** Be cautious of falling objects. Stay away from shelves or fragile items.
        """
    ),
    3: (
        "Moderate Earthquake",
        """
        **Description:** Moderate earthquakes can be felt over a larger area and may cause minor structural damage.
        
        **Precautions:** Avoid buildings with visible cracks. Stay in open areas if possible.
        """
    ),
    4: (
        "Strong Earthquake",
        """
        **Description:** Strong earthquakes can cause considerable damage in populated areas near the epicenter.
        
        **Precautions:** Follow evacuation plans. Seek shelter under sturdy furniture if indoors.
        """
    ),
    5: (
        "Major Earthquake",
        """
        **Description:** Major earthquakes release a large amount of energy and can cause widespread destruction.
        
        **Precautions:** Evacuate immediately if instructed. Avoid damaged buildings and infrastructure.
        """
    ),
    6: (
        "Great Earthquake (mwb)", 
        """
        **Description:** Great earthquakes are massive events capable of causing catastrophic destruction over large areas.
        
        **Precautions:** Widespread devastation and high risk of casualties.
        """
    ),
    7: (
        "Colossal Earthquake", 
        """
        **Description:** Colossal earthquakes are among the largest events, causing extreme destruction.
        
        **Precautions:** Extreme danger; follow all evacuation instructions.
        """
    ),
    8: (
        "Cataclysmic Earthquake", 
        """
        **Description:** Cataclysmic earthquakes are extremely rare and can reshape landscapes.
        
        **Precautions:** Highest level of danger; immediate evacuation required.
        """
    ),
}

def earthquake(req):
    if req.method == 'POST':
        # Collect input data from the form
        magnitude = req.POST.get('magnitude')
        cdi = req.POST.get('cdi')
        nst = req.POST.get('nst')
        depth = req.POST.get('depth')
        latitude = req.POST.get('latitude')
        longitude = req.POST.get('longitude')
        year = req.POST.get('year')

        # Validate and convert inputs to appropriate data types
        try:
            # Check if any field is missing or empty
            if not all([magnitude, cdi, nst, depth, latitude, longitude, year]):
                messages.error(req, "All fields are required.")
                return render(req, "user/user-earthquake.html")

            # Convert inputs to appropriate data types
            magnitude = float(magnitude)
            cdi = float(cdi)
            nst = int(nst)
            depth = float(depth)
            latitude = float(latitude)
            longitude = float(longitude)
            year = int(year)

            # Prepare input data for prediction
            input_data = [[magnitude, cdi, nst, depth, latitude, longitude, year]]

            # Load trained machine learning model
            try:
                with open(MODEL_PATH, 'rb') as file:
                    loaded_model = pickle.load(file)

                # Make prediction
                try:
                    prediction = loaded_model.predict(input_data)
                    predicted_class = int(prediction[0])

                    # Get predicted class and description
                    predicted_category, description = MAGNITUDE_CLASSES.get(predicted_class, ("Unknown", "No description available."))

                    # Display messages based on prediction
                    messages.success(req, f"The predicted earthquake category is {predicted_category}.")
                    messages.info(req, description)

                    print("Session Contents:", req.session.items())
                    user_email = req.session.get("user_email")
                    
                    if user_email:
                                # Fetch the logged-in user's address from the database
                        user = UserDetails.objects.get(email=user_email)
                        user_address = user.address  # Get the address associated with the user

                        subject = f"Earthquake Prediction: {predicted_category}"
                        message = f"Your earthquake prediction is {predicted_category}. Description: {description}"
                        from_email = settings.EMAIL_HOST_USER
                        recipient_list = [user_email]  # Use user's email from session

                        send_mail(
                            subject=subject,
                            message=message,
                            from_email=from_email,
                            recipient_list=recipient_list,
                            fail_silently=False,
                        )
                               # Notify all users with the same location (address) about the flood prediction
                        earthquake_location(user_address, predicted_category, description)
                    else:
                        messages.error(req, "User email not found in session.")

                    context1 = {
                        'prediction': predicted_category,
                        'description': description,
                    }
                    # Render template with evaluation results
                    return render(req, "user/user-earthquake.html", context1)

                except Exception as e:
                    messages.error(req, f"Error making prediction: {str(e)}")
                    return render(req, "user/user-earthquake.html")

            except Exception as e:
                messages.error(req, f"Error loading model: {str(e)}")
                return render(req, "user/user-earthquake.html")

        except ValueError:
            messages.error(req, "Invalid input! Please ensure all fields are filled correctly.")
            return render(req, "user/user-earthquake.html")

    return render(req, "user/user-earthquake.html")


def earthquake_location(location, predicted_category, description):
    # Get all users with the same address (location)
    users_in_location = UserDetails.objects.filter(address=location)

    # Prepare the subject and message
    subject = f"Earthquake Prediction: {predicted_category}"
    message = f"Your earthquake prediction is {predicted_category}. Description: {description}"
                     
    # Get sender email from settings
    from_email = settings.EMAIL_HOST_USER

    # Extract emails of all users in the same location
    recipient_list = users_in_location.values_list('email', flat=True)

    if recipient_list:
        # Send the email to all the users in the same location
        send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=recipient_list,
            fail_silently=False,
        )
    else:
        print(f"No users found in the location: {location}")





 


import pickle
from django.shortcuts import render
from django.contrib import messages
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

# Path to the dataset and machine learning model
DATASET_PATH = "detection/tsunami/tsunami_dataset.csv"
MODEL_PATH = 'detection/tsunami/dtcf.pkl'

# Define classes for tsunami predictions
SUNAMI_CLASSES = {
    0: (
        "Earthquake Magnitude",
        """
        **Description:** This class considers the magnitude of the earthquake that triggered the tsunami. Earthquakes with higher magnitudes are more likely to generate significant tsunamis.
        
        **Precautions:** Monitor seismic activity closely. If a strong earthquake occurs, be prepared for a potential tsunami warning.
        """
    ),
    1: (
        "Ocean Depth",
        """
        **Description:** This class assesses the depth of the ocean where the earthquake occurred. Shallower waters can amplify tsunami waves.
        
        **Precautions:** Be cautious if you are in a coastal area with shallow waters. Follow evacuation orders promptly.
        """
    ),
    2: (
        "Proximity to Plate Boundary",
        """
        **Description:** This class evaluates how close the earthquake is to a tectonic plate boundary. Earthquakes near these boundaries are more likely to cause tsunamis.
        
        **Precautions:** If you live near a tectonic plate boundary, stay informed about seismic activity and be prepared for evacuations.
        """
    ),
    3: (
        "Seafloor Displacement",
        """
        **Description:** This class considers the amount of seafloor displacement caused by the earthquake. Greater displacement can lead to larger tsunamis.
        
        **Precautions:** If a significant seafloor displacement is detected, evacuate coastal areas immediately.
        """
    ),
    4: (
        "Coastal Population Density",
        """
        **Description:** This class assesses the population density of coastal areas that could be affected by a tsunami. Higher densities increase the risk of casualties.
        
        **Precautions:** In densely populated coastal areas, have evacuation plans in place and conduct regular drills.
        """
    ),
    5: (
        "Wave Energy",
        """
        **Description:** This class evaluates the energy of the tsunami waves. Higher energy waves cause more destruction.
        
        **Precautions:** If high-energy waves are predicted, evacuate immediately and seek higher ground.
        """
    ),
    6: (
        "Distance from Epicenter",
        """
        **Description:** This class considers how far the coastal area is from the earthquake epicenter. Closer distances increase the risk of tsunami impact.
        
        **Precautions:** If you are near the epicenter of a significant earthquake, be prepared for immediate evacuation.
        """
    ),
}

def Sunami(request):
    if request.method == 'POST':
        # Collect input data from the form
        earthquake_magnitude = request.POST.get('em')
        ocean_depth = request.POST.get('od')
        proximity_to_plate_boundary = request.POST.get('pb')
        seafloor_displacement = request.POST.get('sd')
        coastal_population_density = request.POST.get('cpd')
        wave_energy = request.POST.get('we')
        distance_from_epicenter = request.POST.get('dfe')

        # Validate and convert inputs to appropriate data types
        try:
            # Check if any field is missing or empty
            if not all([earthquake_magnitude, ocean_depth, proximity_to_plate_boundary, seafloor_displacement, coastal_population_density, wave_energy, distance_from_epicenter]):
                messages.error(request, "All fields are required.")
                return render(request, "user/user_tsunami.html")

            # Convert inputs to appropriate data types
            earthquake_magnitude = float(earthquake_magnitude)
            ocean_depth = float(ocean_depth)
            proximity_to_plate_boundary = float(proximity_to_plate_boundary)
            seafloor_displacement = float(seafloor_displacement)
            coastal_population_density = float(coastal_population_density)
            wave_energy = float(wave_energy)
            distance_from_epicenter = float(distance_from_epicenter)  # Changed to float for consistency

            # Prepare input data for prediction
            input_data = [[earthquake_magnitude, ocean_depth, proximity_to_plate_boundary, seafloor_displacement, coastal_population_density, wave_energy, distance_from_epicenter]]

            # Load trained machine learning model
            with open(MODEL_PATH, 'rb') as file:
                loaded_model = pickle.load(file)

                # Make a prediction using the model
                prediction = loaded_model.predict(input_data)  # Result will be in array format (e.g., array([3]))
                predicted_class = int(prediction[0])  # Extract integer value from array

                # Get predicted class and description
                predicted_category, description = SUNAMI_CLASSES.get(predicted_class, ("Unknown", "No description available."))

                # Display messages based on prediction
                messages.success(request, f"The predicted tsunami category is {predicted_category}.")
                messages.info(request, description)
                print("Session Contents:", request.session.items())
                user_email = request.session.get("user_email")
                if user_email:
                        # Fetch the logged-in user's address from the database
                    user = UserDetails.objects.get(email=user_email)
                    user_address = user.address  # Get the address associated with the user

                    subject = f"The predicted tsunami category is : {predicted_category}"
                    message = f"Your tsunami prediction is {predicted_category}. Description: {description}"
                    from_email = settings.EMAIL_HOST_USER
                    recipient_list = [user_email]  # Use user's email from session

                    send_mail(
                        subject=subject,
                        message=message,
                        from_email=from_email,
                        recipient_list=recipient_list,
                        fail_silently=False,
                    )
                    # Notify all users with the same location (address) about the sunami prediction
                    sunami_location(user_address, predicted_category, description)
                else:
                    messages.error(request, "User email not found in session.")
                context = {
                    'prediction': predicted_category,
                    'description': description,
                }

                return render(request, "user/user-sunami.html", context)

        except ValueError:
            messages.error(request, "Invalid input! Please ensure all fields are filled correctly.")
            return render(request, "user/user-sunami.html")
    return render(request, 'user/user-sunami.html')


def sunami_location(location, predicted_category, description):
    # Get all users with the same address (location)
    users_in_location = UserDetails.objects.filter(address=location)

    # Prepare the subject and message
    subject = f"The predicted tsunami category is : {predicted_category}"
    message = f"Your tsunami prediction is {predicted_category}. Description: {description}"                    
    # Get sender email from settings
    from_email = settings.EMAIL_HOST_USER

    # Extract emails of all users in the same location
    recipient_list = users_in_location.values_list('email', flat=True)

    if recipient_list:
        # Send the email to all the users in the same location
        send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=recipient_list,
            fail_silently=False,
        )
    else:
        print(f"No users found in the location: {location}")



import string
import secrets

def generate_random_password(length=6):
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(secrets.choice(characters) for _ in range(length))
    return password





from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk
from django.shortcuts import render

# Ensure VADER lexicon is downloaded
nltk.download('vader_lexicon')

# Define categories and related keywords
categories = {
    "Request": ["request", "need", "help"],
    "Offer": ["offer", "provide", "donate"],
    "Aid Related": ["aid", "relief", "support"],
    "Medical Help": ["medical", "doctor", "hospital"],
    "Medical Products": ["medicine", "equipment", "supplies"],
    "Search And Rescue": ["search", "rescue", "missing"],
    "Security": ["security", "safety", "protection"],
    "Military": ["military", "troops", "deployment"],
    "Child Alone": ["child", "alone", "lost"],
    "Water": ["water", "hydration", "drinking"],
    "Food": ["food", "hunger", "starving"],
    "Shelter": ["shelter", "home", "housing"],
    "Tools": ["tools", "equipment", "machinery"],
    "Hospitals": ["hospital", "clinic", "medical facility"],
    "Shops": ["shop", "store", "market"],
    "Aid Centers": ["aid center", "relief center", "support center"],
    "missing":["person","name","human","missed"],
    "Other Infrastructure": ["infrastructure", "roads", "bridges"],
    "Weather Related": ["weather", "storm", "flood"],
    "Floods": ["flood", "flooding", "overflow"],
    "Storm": ["storm", "hurricane", "cyclone"],
    "Fire": ["fire", "burning", "blaze"],
    "Earthquake": ["earthquake", "quake", "seismic"],
    "Cold": ["cold", "freezing", "hypothermia"],
    "Other Weather": ["weather", "climate", "temperature"],
    "Direct Report": ["report", "update", "situation"]
}


def help_page(request):
    if request.method == 'POST':
        message = request.POST.get('userInput')
        # Perform sentiment analysis
        sia = SentimentIntensityAnalyzer()
        sentiment_scores = sia.polarity_scores(message)
        sentiment = "Positive" if sentiment_scores['compound'] > 0 else "Negative" if sentiment_scores['compound'] < 0 else "Neutral"
        
        # Categorize the message
        categorized = False
        for category, keywords in categories.items():
            for keyword in keywords:
                if keyword.lower() in message.lower():
                    categorized = True
                    category_match = category
                    break
            if categorized:
                break
        
        if not categorized:
            category_match = "Uncategorized"
        
        # Highlight related words in the message
        highlighted_message = message
        for category, keywords in categories.items():
            for keyword in keywords:
                highlighted_message = highlighted_message.replace(keyword, f"<mark>{keyword}</mark>")  # Add markup for highlighting
        
  
        # Save to database with the UserDetails instance in the viewer field
        SentimentAnalysis.objects.create(
            message=message,
            sentiment=sentiment,
            category=category_match,
           
        )
        
        # Display results
        context = {
            'sentiment': sentiment,
            'category': category_match,
            'message': highlighted_message
        }
        
        return render(request, 'user/help.html', context)
    
    return render(request, 'user/help.html')
import matplotlib.pyplot as plt
from io import BytesIO
import base64

def graphs(request):
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

    return render(request, 'user/bar-graph.html', context)








def satiable_requests(request):
    sentiments = SentimentAnalysis.objects.all()

    # Retrieve user details from the session
    user_email = request.session.get("user_email")
    name = request.session.get("name")
    
    # Print session data for debugging
    print(f"Session Data - user_email: {user_email}, name: {name}")
    print(f"Session Keys: {request.session.keys()}")  # Print all available session keys
    
    # Pass the sentiments queryset and session values to the template
    return render(request, 'user/satiable-requests.html', {
        'sentiments': sentiments,
        'user_email': user_email,
        'name': name
    })





from adminapp.models import UserDetails  # Make sure to import the UserDetails model

def feedback(request):
    user_email = request.session.get('user_email')
    if request.method == "POST":
        rating = request.POST.get("rating")
        review = request.POST.get("feedback")
        
        # Get the UserDetails instance using the user_id
        user_instance = UserDetails.objects.get(email=user_email)
        
        sid = SentimentIntensityAnalyzer()
        score = sid.polarity_scores(review)
        sentiment = None
        
        if score['compound'] > 0 and score['compound'] <= 0.5:
            sentiment = 'positive'
        elif score['compound'] >= 0.5:
            sentiment = 'very positive'
        elif score['compound'] < -0.5:
            sentiment = 'very negative'
        elif score['compound'] < 0 and score['compound'] >= -0.5:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        # Create the feedback record, passing the user instance to the Reviewer field
        Feedback.objects.create(Rating=rating, Review=review, Sentiment=sentiment, Reviewer=user_instance)
        messages.success(request, 'Feedback recorded')
        return redirect('feedback')
    
    return render(request, 'user/user-feedback.html')




import requests
import re
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .models import Conversation

@csrf_exempt  # Consider using CSRF protection in production
def user_chatbot(request):
    conversations = Conversation.objects.all().order_by('created_at')
    
    if request.method == 'POST':
        user_message = request.POST.get('message', '').strip()
        
        if user_message:
            # Call Perplexity API
            headers = {
                "Authorization": f"Bearer {settings.PERPLEXITY_API_KEY}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "sonar",
                "messages": [
                    {
                        "role": "system",
                        "content": "Extract the key points or main headlines from the following text. Please respond only with the headlines separated by commas. No external links, no symbols, no additional suggestions. Just the plain text."
                    },
                    {
                        "role": "user",
                        "content": user_message
                    }
                ]
            }
            
            try:
                response = requests.post(
                    "https://api.perplexity.ai/chat/completions",
                    json=payload,
                    headers=headers,
                    timeout=10  # Add a timeout for better error handling
                )
                
                bot_response = "Error: Could not get response from AI"
                
                if response.status_code == 200:
                    api_response = response.json()
                    if "choices" in api_response and len(api_response["choices"]) > 0:
                        bot_response = api_response['choices'][0]['message']['content']
                        
                        # Clean response (remove markdown bold and reference numbers)
                        bot_response = re.sub(r'\*\*(.*?)\*\*', r'\1', bot_response)  # Remove bold
                        bot_response = re.sub(r'\[\d+\]', '', bot_response)  # Remove reference numbers
                        
                        print(f"Bot Response (Before Saving): {bot_response}")
                else:
                    bot_response = f"Error: API returned status {response.status_code}"
                    
            except requests.RequestException as e:
                bot_response = f"Error: {str(e)}"

            # Save the conversation
            Conversation.objects.create(user_message=user_message, bot_response=bot_response)
            
            return redirect('chatbot')
    print(f"Conversations in Template: {list(conversations.values())}")
    return render(request, 'user/user-chatbot.html', {'conversations': conversations})