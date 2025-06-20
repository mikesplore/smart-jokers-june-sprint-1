# PythonAnywhere Deployment Guide

## 1. Sign up for PythonAnywhere
- Go to [PythonAnywhere](https://www.pythonanywhere.com/) and sign up for an account.
- The free tier is sufficient for starting out.

## 2. Upload Your Code

### Using Git
```bash
# On PythonAnywhere bash console
git clone https://github.com/mikesplore/smart-jokers-june-sprint-1.git smart-jokers
# Replace 'mikesplore' with your actual GitHub username
```

### Using Manual Upload
- Create a ZIP archive of your project on your local machine.
- From the PythonAnywhere dashboard, go to **Files** and upload your ZIP.
- Unzip the file in your PythonAnywhere directory:
```bash
unzip yourarchive.zip -d smart-jokers
```

## 3. Create a Virtual Environment
```bash
# On PythonAnywhere bash console
cd ~/smart-jokers
python3.10 -m venv venv  # Use python3.10 explicitly on PythonAnywhere
source venv/bin/activate
pip install --upgrade pip  # Ensure pip is up to date
pip install -r requirements.txt 
```

## 4. Set Up Your Web App
- Go to the **Web** tab in the PythonAnywhere dashboard.
- Click **"Add a new web app"**.
- Choose **"Manual configuration"** (not "Django").
- Select **Python 3.10** (or the version that matches your local environment).
- For the path, enter: `/home/mikesplore/smart-jokers`

## 5. Configure Your WSGI File
- In the **Web** tab, click on the WSGI configuration file link.
- Replace the contents with:
    ```python
    import os
    import sys

    # Add your project directory to the sys.path
    path = '/home/mikesplore/smart-jokers'
    if path not in sys.path:
        sys.path.insert(0, path)

    # Set environment variable to tell Django where your settings.py is
    os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'

    # Set up Django
    from django.core.wsgi import get_wsgi_application
    application = get_wsgi_application()
    ```

## 6. Configure Static and Media Files

- In the **Web** tab, under **"Static files"**:
  
  > Note: If your project doesn't use static files yet, you may still want to set this up for future use.
  
  - For Django admin interface static files:
    - URL: `/static/admin/`  
      Directory: `/home/mikesplore/smart-jokers/venv/lib/python3.10/site-packages/django/contrib/admin/static/admin`

  - If you have project-specific static files:
    - URL: `/static/`  
      Directory: `/home/mikesplore/smart-jokers/static`
    
  - If you need media file uploads:
    - URL: `/media/`  
      Directory: `/home/mikesplore/smart-jokers/media`

## 7. Update `settings.py` for Deployment

**You can do this using bash:**

```bash
nano ~/smart-jokers/config/settings.py
```

**Add or update the following lines:**

At the top (if not already present):
```python
import os
```

Somewhere in your settings (usually near the bottom):
```python
# Static files configuration
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# If you need media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Security settings for production
ALLOWED_HOSTS = ['mikesplore.pythonanywhere.com']
DEBUG = False
```

> These changes are required for Django to serve your site correctly on PythonAnywhere.
> If your project doesn't currently use static files, this setup will still be useful for Django admin interface.

**Save and exit nano:**  
- Press `Ctrl+O` to save, `Enter` to confirm, and `Ctrl+X` to exit.

---

## 8. Set Up Database and Admin User

```bash
cd ~/smart-jokers
python manage.py migrate
python manage.py createsuperuser  # Follow prompts to create an admin user
```

## 9. Collect Static Files

```bash
python manage.py collectstatic
```

## 10. Configure Virtual Environment in PythonAnywhere
- In the **Web** tab, set the path to your virtual environment:
    ```
    /home/mikesplore/smart-jokers/venv
    ```

## 11. Reload Your Web App
- Click the **"Reload"** button in the Web tab.

## 12. Visit Your Site
- Your site should now be live at:  
  [https://mikesplore.pythonanywhere.com](https://mikesplore.pythonanywhere.com)

---

## Useful Bash Commands

### Remove a Directory and All Its Contents

```bash
rm -r directory_name      # Recursive delete (will prompt for confirmation)
rm -rf directory_name     # Force recursive delete (no prompt)
```
> Be careful: this operation is irreversible.

### Change Port While Running Django Development Server

By default, Django runs on port 8000. To change the port (and optionally the IP address):

```bash
python manage.py runserver 8080
# or
python manage.py runserver 0.0.0.0:8080
```

---

## PythonAnywhere-Specific Configuration Summary

### WSGI Configuration
```python
import os
import sys

path = '/home/mikesplore/smart-jokers'
if path not in sys.path:
    sys.path.insert(0, path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

### Static Files
- URL: `/static/` → `/home/mikesplore/smart-jokers/static`
- URL: `/media/` → `/home/mikesplore/smart-jokers/media`

### Virtual Environment Path
- `/home/mikesplore/smart-jokers/venv`

### Your Site URL
- [https://mikesplore.pythonanywhere.com](https://mikesplore.pythonanywhere.com)

---

## Troubleshooting

- Check the error logs in the Web tab.
- Make sure `DEBUG = False` in `settings.py` for production.
- Ensure `ALLOWED_HOSTS` includes `'mikesplore.pythonanywhere.com'`.
- Verify your database configuration.
- If you see "no virtual environment detected," make sure you created it with the correct Python version and set the path in the Web tab.