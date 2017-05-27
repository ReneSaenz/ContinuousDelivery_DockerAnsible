# Windows Project Setup

Once you have your environment all setup, perform the following.

#### Create Django project template

Select a project location and perform the following.

`$ django-admin startproject todobackend`

This will create a project skeleton for you.

Among the things it creates:
- _manage.py_ Management utility to perform various project tasks
- _todobackend_ folder, refered as the django root folder.
It is the main python package for the application.

Inside the _todobackend_ folder, you will find the following.
- _settings.py_ Includes configuration settings for the project
- _urls.py_ specify how to route http requests
- _wsgi.py_ provides the means for connect to an external webserver such as apache or nginx to pipeline http requests in response to the application.


At this point, we need to reorganize the project tree structure. This is important for the _Continuous Delivery_ workflow. <br>
We want to have clean separation between app code and CD tooling that will be built. Perform the following.
```
$ cd todobackend
$ mkdir src
$ mv manage.py src
$ mv todobackend src
```

At this point, this is our initial project setup, so we can use _git_ to commit.

Inside the project folder, create a python virtual environment in a folder called *`venv`*
```
$ cd todobackend
$ virtualenv venv
```
In order to NOT have the virtual environment as part of the *git* repo, we flag the *`venv`* folder in the *.gitignore* file.

We can now activate the virtual environment.

Active the environment

```
$ source venv/bin/activate
```

You should see the prompt change, indicating we are operating in the virtual environment.

```
(venv) todobackend$
```

At this point, we can install all of the software our application needs.
_NOTE:_ This might seem strange since we previously install these two.
They were installed at the system level and not at the virtual environment level.
```
(venv) todobackend$ pip install pip --upgrade
```

Install django in the virtual environment
```
(venv) todobackend$ pip install django==1.9
```

Install Django REST support
```
(venv) todobackend$ pip install djangorestframework==3.3
```

Install Django CORS (Cross origin hearder) support

```
(venv) todobackend$ pip install django-cors-headers==1.1
```

Add an "app"  in Django terminology. The "app" will be called *todo*

```
(venv) src$ cd src
(venv) src$ python manage.py startapp todo
```


This will create the *todo* app

```
│   manage.py
│
├───todo
│   │   admin.py
│   │   apps.py
│   │   models.py
│   │   tests.py
│   │   views.py
│   │   __init__.py
│   │
│   └───migrations
│           __init__.py
│
└───todobackend
    │   settings.py
    │   urls.py
    │   wsgi.py
    │   __init__.py
    │
    └───__pycache__
            settings.cpython-36.pyc
            __init__.cpython-36.pyc
```

In order to include *todo*  app in the main project, we need to modify the _settings.py_ file under _todobackend_ directory.<br>
Go to the _INSTALLED_APPS_ section and add the following packages.

```
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'todo'
]
```

Configure the *cors headers* as a middleware component.
_NOTE:_ Order is important!
```
MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
```

Add the following to the end of _settings.py_ file. <br>
_NOTE:_ Do not do this in a production environment
```
# CORS settings

CORS_ORIGIN_ALLOW_ALL = True
```
