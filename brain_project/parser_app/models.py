from django.db import models
from django.db.models import JSONField



class Phone(models.Model):
    # 1. Основные данные (важные поля)
    product_name = models.CharField(max_length=255, null=True)
    colors = JSONField(null=True, blank=True)
    memory_capacity = JSONField(null=True, blank=True)
    manufacturer = models.CharField(max_length=255, null=True)   
    price = models.CharField(max_length=100, null=True)    
    promotional_price = models.CharField(max_length=100, null=True)      
    product_code = models.CharField(max_length=255, null=True, unique=True)
    number_of_reviews = models.CharField(max_length=255, null=True)   
    screen_diagonal = models.CharField(max_length=255, null=True)         
    display_resolution = models.CharField(max_length=50, null=True)       
    characteristics = JSONField(null=True, blank=True)                   


    photos = JSONField(null=True, blank=True, help_text="Ссылки на все фото товара")  
    link = models.URLField(null=True, blank=True)            
    status = models.CharField(max_length=50, default="New", null=True)  # Статус обработки: New → Done

    def __str__(self):
        return f"Phone: {self.product_name or 'Unnamed Phone'}, Colors: {', '.join(self.colors or [])}, Memory: {', '.join(self.memory_capacity or [])}, Manufacturer: {self.manufacturer or 'Unknown'}, Price: {self.price or 'N/A'}, Product Code: {self.product_code or 'N/A'}"



# python manage.py makemigrations

# python manage.py migrate