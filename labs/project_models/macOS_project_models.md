# Project Web Service


### Data Model

After the code change for models and thus, the model defined, we can now Create
our schema for our model in the DB.<br>
Python comes with an Object Relational Mapper (ORM) out-of-the-box that
requires minimal configuration.

To create the DB schema for the model, execute.
```
(venv) src$ python manage.py makemigrations todo
```
This will create a _migrations_ subfolder under the _todo_ app

```
C:.
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
│   ├───migrations
│   │   │   0001_initial.py
│   │   │   __init__.py
│   │   │
│   │   └───__pycache__
│   │           __init__.cpython-36.pyc
│   │
│   └───__pycache__
│           admin.cpython-36.pyc
│           models.cpython-36.pyc
│           __init__.cpython-36.pyc
│
└───todobackend
    │   settings.py
    │   urls.py
    │   wsgi.py
    │   __init__.py
    │
    └───__pycache__
            settings.cpython-36.pyc
            urls.cpython-36.pyc
            __init__.cpython-36.pyc
```

To apply the migrations to the DB, execute

```
(venv) src$ python manage.py migrate
```

It will use a local SQLite DB, located in the project root.


### Serializers

For more info, refer to django [serializers](http://www.djsngo-rest-framework.org/api-guide/serializers)

Create file _serializers.py_ under the _todo_ directory.


### views

For more info, refer to django [views](http://www.djsngo-rest-framework.org/api-guide/views)

Edit the _views.py_ file under the _todo_ diretory


### Configuring Routing

Routing determines how the application will handle incoming requests
based on the requested URL.

in Django, routing system is first configured centrally in the _urls.py_ file
automatically created when the application was created.

Routing is configured using regular expressions.

Create file _urls.py_ under the _todo_ app diretory

### Test Drive the application

```
(venv) src$ python manage.py runserver
```
