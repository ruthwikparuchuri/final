from django.db import models

# Create your models here.
class WeatherPrediction(models.Model):
    temperature = models.FloatField()
    dew_point_temp = models.FloatField()
    relative_humidity = models.IntegerField()
    wind_speed = models.FloatField()
    visibility = models.FloatField()
    pressure = models.FloatField()
    year = models.IntegerField()
    month = models.IntegerField()
    day = models.IntegerField()
    predicted_weather = models.CharField(max_length=50)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.predicted_weather} on {self.year}-{self.month}-{self.day}"


class FloodPrediction(models.Model):
    monsoon_intensity = models.IntegerField()
    topography_drainage = models.IntegerField()
    river_management = models.IntegerField()
    deforestation = models.IntegerField()
    urbanization = models.IntegerField()
    climate_change = models.IntegerField()
    dams_quality = models.IntegerField()
    siltation = models.IntegerField()
    agricultural_practices = models.IntegerField()
    encroachments = models.IntegerField()
    ineffective_disaster_preparedness = models.IntegerField()
    drainage_systems = models.IntegerField()
    coastal_vulnerability = models.IntegerField()
    landslides = models.IntegerField()
    watersheds = models.IntegerField()
    deteriorating_infrastructure = models.IntegerField()
    population_score = models.IntegerField()
    wetland_loss = models.IntegerField()
    inadequate_planning = models.IntegerField()
    political_factors = models.IntegerField()
    prediction_value = models.FloatField()  # Predicted flood severity value
    description = models.TextField()  # Description of the prediction
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Flood Risk: {self.prediction_value} - {self.description[:50]}"


class EarthquakePrediction(models.Model):
    cdi = models.FloatField()  # Community Determined Intensity
    nst = models.IntegerField()  # Number of stations reporting
    depth = models.FloatField()  # Depth of the earthquake
    magnitude = models.FloatField()  # Magnitude of the earthquake
    latitude = models.FloatField()  # Latitude of the epicenter
    longitude = models.FloatField()  # Longitude of the epicenter
    year = models.IntegerField()  # Year of the earthquake
    predicted_magnitude_class = models.CharField(max_length=50)  # Predicted magnitude class
    description = models.TextField()  # Description of the magnitude class
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp for when the prediction was made

    def __str__(self):
        return f"{self.predicted_magnitude_class} - {self.magnitude} (Year: {self.year})"

class SentimentAnalysis(models.Model):
    s_id = models.AutoField(primary_key=True)
    message = models.TextField()
    sentiment = models.CharField(max_length=50)
    category = models.CharField(max_length=50)
    def __str__(self):
        return f"{self.message} - {self.sentiment} - {self.category}"




    



class Conversation(models.Model):
    user_message = models.TextField()
    bot_response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def _str_(self):
        return f"User: {self.user_message[:50]}..."