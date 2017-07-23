# MacOS Unit and Integration Testing

## Unit Tests

Implement all of your tests in a file __tests.py__ located under `src/todo`

To run your tests, execute the following command
```
$ cd todobackend/src
$ python manage.py test

Creating test database for alias 'default'...
............
----------------------------------------------------------------------
Ran 12 tests in 0.118s

OK
Destroying test database for alias 'default'...
```

Notice by the dots that all tests passed and a database was created and then destroyed for our tests. The database used is sqlite3 that ships with django.
```
$ ls -l
-rw-r--r--   1 135168 Jul 12 22:47 db.sqlite3
-rwxr-xr-x   1    254 Jul 12 20:48 manage.py
drwxr-xr-x  18    612 Jul 15 16:54 todo
drwxr-xr-x  10    340 Jul 12 22:42 todobackend
```

## Integration Tests

We need to verify the functionality between the model, serializer and view.
Writing integration tests is much more meaningful in terms of verifying functionality.

If using MySql as your proudction DB, we need to refactor how settings
are configured for the project, as we now need a new test configuration that uses MySql DB.

### Configuration Settings

Settings need to change according to the environment you are planning to run/test.

For example

- Test Settings
  - Host: localhost
  - Engine: sqlite3
  - Debug: true

- Release Settings
  - Host: db
  - DB: todobackend
  - Engine: MySql
  - Debug: true

- QA Environment Settings
  - Host: qasql01
  - Engine: MySql
  - DB: todobackend
  - Debug: true

- Prod Environment Settings
  - Host: proddb01
  - Engine: MySql
  - Debug: false

By default, there is a `src/todobackend/settings.py` file. This is not scalable and we will re-org our directory structure.

First, create a `settings` folder under the `todobackend` folder.
Then, create a `todobackend/settings/__init__.py` file, which marks the folder as a package. Then move the existing `setttings.py` into `todobackend/settings/base.py` file. This will serve as the base settings for our project.

```
$ tree
.
├── __init__.py
├── __init__.pyc
├── settings
│   ├── __init__.py
│   └── base.py
├── settings.pyc
├── urls.py
├── urls.pyc
├── wsgi.py
└── wsgi.pyc
```

In addition, we will use a `base.py` settings, which other settings will inherit.
Making it easier to create new settings. Furthermore, we will use environment variables, as the prefer mechanism to configure any parameters that need to change from environment to environment.

We need to update our `src/manage.py` script to locate the base settings of our project.
```
#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "todobackend.settings.base")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
```
Similarly, we need to change `src/todobackend/wsgi.py` file
```
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "todobackend.settings.base")

application = get_wsgi_application()
```

Now lets create new settings for our use of MySql and call them `src/todobackend/settings/test.py` and we override the settings in `src/todobackend/settings/base.py`

### Installing MySQL

We now need to install MySQL in our localhost to proceed with our integration.

Using brew to install.
```
$ brew install homebrew/versions/mysql56
$ mysql.server start
$ mysql_secure_installation
```

Once initialization is complete, I can login into MySQL. Create a new DB and create a new user and grant access to DB.
```
$ mysql -u root -p
mysql> CREATE DATABASE todobackend;
Query OK, 1 row affected (0.00 sec)

mysql> GRANT ALL PRIVILEGES ON *.* TO 'todo'@'localhost' identified by 'password';
Query OK, 0 rows affected (0.00 sec)
mysql> quit
Bye

$
```

We now need to install python mysql libraries.
```
$ pip install mysql-python
```

Now we can execute our tests against MySQL using the `src/todobackend/settings/test.py` file.

We can execute
```
$ export DJANGO_SETTINGS_MODULE=todobackend.settings.test
```

Or, we can use the settings flag

```
$ python manage.py test --settings=todobackend.settings.test

$ python manage.py test --settings=todobackend.settings.test
Creating test database for alias 'default'...
............
----------------------------------------------------------------------
Ran 12 tests in 0.139s

OK
Destroying test database for alias 'default'...


```

### Improving Test Output

We want to improve our tests so that they are easier to read and understand.
In addition, we would like to have reports to output to disk

```
$ pip install django-nose
$ pip install pinocchio
$ pip install coverage
```

We now need to update our `src/todobackend/settings/test.py` settings.
```
INSTALLED_APPS += ('django_nose', )
TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
TEST_OUTPUT_DIR = os.environ.get('TEST_OUTPUT_DIR','.')
NOSE_ARGS = [
  '--verbosity=2',                  # verbose output
  '--nologcapture',                 # don't output log capture
  '--with-coverage',                # activate coverage report
  '--cover-package=todo',           # coverage reports will apply to these packages
  '--with-spec',                    # spec style tests
  '--spec-color',
  '--with-xunit',                   # enable xunit plugin
  '--xunit-file=%s/unittests.xml' % TEST_OUTPUT_DIR,
  '--cover-xml',                    # produce XML coverage info
  '--cover-xml-file=%s/coverage.xml' % TEST_OUTPUT_DIR,
]
```

At this point, we are now ready to run our tests.
```
$ python manage.py test --settings=todobackend.settings.test
nosetests --verbosity=2 --nologcapture --with-coverage --cover-package=todo --with-spec --spec-color --with-xunit --xunit-file=./unittests.xml --cover-xml --cover-xml-file=./coverage.xml
Creating test database for alias 'default'...

Ensure we can create a new todo item
- item has correct title
- item was created
- received 201 created status code
- received location header hyperlink

Ensure we can delete all todo items
- all items were deleted
- received 204 no content status code

Ensure we can delete a todo item
- received 204 no content status code
- the item was deleted

Ensure we can update an existing todo item using PATCH
- item was updated
- received 200 ok status code

Ensure we can update an existing todo item using PUT
- item was updated
- received 200 created status code

----------------------------------------------------------------------
XML: code/todobackend/src/unittests.xml
Name                              Stmts   Miss  Cover
-----------------------------------------------------
todo/__init__.py                      0      0   100%
todo/admin.py                         1      1     0%
todo/migrations/0001_initial.py       6      0   100%
todo/migrations/__init__.py           0      0   100%
todo/models.py                        7      7     0%
todo/serializers.py                   7      0   100%
todo/urls.py                          6      0   100%
todo/views.py                        18      0   100%
-----------------------------------------------------
TOTAL                                45      8    82%
----------------------------------------------------------------------
Ran 12 tests in 0.146s

OK

Destroying test database for alias 'default'...

```
