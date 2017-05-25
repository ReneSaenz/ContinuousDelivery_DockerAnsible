# Windows Project Setup

Once you have your environment all setup, perform the following.

#### Create Django project template

Select a project location and perform the following.

`c:\django-admin startproject todobackend`

This will create a project skeleton for you.

Among the things it creates:
- _manage.py_ Management utility to perform various project tasks
- _todobackend_ folder, refered as the django root folder.
It is the main python package for the application.

Inside the _todobackend_ folder, you will find the following.
- _settings.py_ Includes configuration settings for the project
- _urls.py_ specify how to route http requests
- _wsgi.py_ provides the means for connect to an external webserver such as apache or nginx to pipeline http requests in response to the application.


At this point, we need to reorganize the project tree structure. This is important for the _Continuous Delivery_ workflow. We want to have clean separation between app code and CD tooling that will be built. Perform the following.
```
c:\cd todobackend
c:\mkdir src
c:\mv manage.py src
c:\mv todobackend src
``` 
