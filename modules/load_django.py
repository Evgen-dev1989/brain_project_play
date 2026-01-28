import os
import sys
import django

# Додаємо шлях до проекту
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'brain_project')))

os.environ['DJANGO_SETTINGS_MODULE'] = 'brain_project.settings'

django.setup()