# Salon booking service

This project based on Django framework
- Django: https://docs.djangoproject.com/en/5.2/

## In current project will be implemented modules
- Booking system
- Reports
- Google Calendar sync ( Please read gcalendar_sync/README.md )

## Installation
```
git clone https://github.com/Gchaimke/salon_booking.git
cd folder
python -m venv venv
.\venv\Scripts\activate.bat
# OR
call venv/Scripts/activate
pip install -r requirements.txt
```

### Django cheat-list
- Generate new project
```
django-admin startproject mysite
```

- Generate new app
```
python manage.py startapp polls
```

- Migrate
```
python manage.py makemigrations booking
python manage.py migrate
```

- Create superuser
```
python manage.py createsuperuser
```

- Run non-production server
```
python manage.py runserver
```

- Run tests
```
python manage.py test booking
```
