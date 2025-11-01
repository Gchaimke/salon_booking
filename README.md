# Salon booking service

This project based on Django framework

## In current project will be implemented modules
- Booking system
- Reports
- Google Calendar sync ( Please read gcalendar_sync/README.md )

## Installation
```
git clone https://github.com/Gchaimke/some_jango.git
cd folder
python -m venv venv
.\venv\Scripts\activate.bat
```
# OR
```
call venv/Scripts/activate
pip install -r requirements.txt
```
## Django admin
django-admin
### Generate new project
```
django-admin startproject mysite
```
### Generate new app
```
python manage.py startapp polls
```

## Django migrate
```
python manage.py makemigrations booking
python manage.py migrate
```

## Django create superuser
```
python manage.py createsuperuser
```

## Django run non-production server
```
python manage.py runserver
```

## Django run tests
python manage.py test booking
