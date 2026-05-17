# Cursory AIP - Production Deployment Configuration (PythonAnywhere)
# This WSGI file acts as the bridge between the web server and our Django app.

import os
import sys

# 1. Define the path to the Cursory AIP core project directory
# This ensures the server knows where our Django apps (campaign, payments, etc.) live
project_home = '/home/yourusername/cursory_AIP/payment_project'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# 2. Set the environment variable to point to our secure settings file
os.environ['DJANGO_SETTINGS_MODULE'] = 'core.settings'

# 3. Initialize and serve the Django application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

# Security Note: 
# Static files (CSS, JS, Banners) are routed separately via the PythonAnywhere web tab.
# Sensitive keys (SECRET_KEY, EMAIL_HOST_PASSWORD) are managed via environment variables.
5. Save (Commit) Karein: Paste karne ke baad, hare rang ke "Commit changes" button par click karein.
