# Creating a Docker Development Image

This lab is based on the [Base Image](creating_docker_base_image.md) lab.

The *Development Image* will be used exclusively on the continuous delivery workflow, so we will not be publishing the development image.
Instead, we will build the *Development Image* dynamically on each time we invoke the workflow.

This means we can store the *Development Image* Dockerfile and related resources, next to our application's source code.

First, go to the main directory of the application source code.
```
$ cd todobackend
$ tree -L 1
.
├── src
└── venv

2 directories, 0 files
```
Next, create a docker subfolder where the Dockerfile will be located.
```
$ mkdir -p docker/dev/
$ cd docker/dev
$ touch Dockerfile
```

The *Development Image* is based on the *Base Image* created on the previous lab. We need to reflect that in our Dockerfile
```
FROM renesaenz/todobackend-base:latest
```

The *Development Image* will be used for two purposes.

1. Unit/integration tests
2. Building application artifacts.

These two activities will require that the image has access to the application source code and to be able to compile any python  package dependencies that install from source distributions.
So we need to include this section on the Dockerfile
```
# Install dev/build dependencies
RUN apt-get update && \
    apt-get install -qy python-dev libmysqlclient-dev
```
Next, the code to activate the virtual environment and install python wheel package. Python wheels are python applications that we will build later on.
```
# Activate virtual environment and install wheel support
RUN . /appenv/bin/activate && \
    pip install wheel --upgrade
```

We then set several environment variables that outputs to a predefined folder `/wheelhouse`
```
# PIP environment variables (NOTE: must be set after installing wheel)
ENV WHEELHOUSE=/wheelhouse PIP_WHEEL_DIR=/wheelhouse PIP_FIND_LINKS=/wheelhouse XDG_CACHE_HOME=/cache

# OUTPUT: Build artifacts (Wheels) are output here
VOLUME /wheelhouse
```

Next, we create a new entry point called `test.sh`. This entry script is similar to the one for *Base Image*. Execept that it has an additional step to install python requirements.
```
# Install application test requirements
pip install -r requirements_test.txt
```
*__NOTE:__* Notice the `-r` flag. This will allow the developer to specify the requirements in a text file.

This step install all of the third party package dependencies. Which are require to run and test the application.


Next, we specify the instruction of the Dockerfile of the new entry-point script. This will override the entry point of the base image. Notice that the parent entry-point script is available, if we want to use it.
We also set a default command that we pass to the entry-point test script.
```
# Set defaults for entrypoint and command string
ENTRYPOINT ["test.sh"]
CMD ["python", "manage.py", "test", "--noinput"]
```

Finally, we copy our application source code into the container, in a folder called `/application` and set it to be the working directory.
```
# Add application source
COPY src /application
WORKDIR /application
```
*__NOTE:__* Noticed we specified the copying of source code as the last step in building the image. This is because application source code, is what will typically change more often when we run our workflow.

This will offer best performace as the first layers are cached and not changed.
Only the bottom layers (source code layers are rebuilt)

Docker Image layers

- Parent Image layers
- `RUN apt-get install -qy python-dev`<br>
...
- `CMD ["python", "manage.py", "test", "--noinput"]`
- *`COPY src /application`*
- *`WORKDIR /application`*

### Creating Application Requirements Files

In python development, it is common to create requirement text files for different configuration needs such as testing. We usually store those under `src` source directory of our application. With this approach, we can specify in `requirements.txt` base package dependencies. And test package dependencies to be specify in another file `requirement_test.txt`.

To create these file, perform the following.<br>
Activate the virtual environment
```
$ cd todobackend
$ source venv/bin/activate
$ cd src
$ pip freeze > requirements.txt
```
The command `pip freeze > requirements.txt` will output all of the requirements of the application into `requirements.txt`. This is the output.
```
$ more requirements.txt
colorama==0.3.9
coverage==4.4.1
Django==1.11.3
django-cors-headers==2.1.0
django-nose==1.4.4
djangorestframework==3.6.3
MySQL-python==1.2.5
nose==1.3.7
pinocchio==0.4.2
pytz==2017.2
```

We need to manually separate the test and base requirements ourselves.
First, copy the requirements for testing in a different file called `requirements_test.txt`.
```
-r requirements.txt
colorama==0.3.9
coverage==4.4.1
Django==1.11.3
django-cors-headers==2.1.0
django-nose==1.4.4
djangorestframework==3.6.3
MySQL-python==1.2.5
nose==1.3.7
pinocchio==0.4.2
```
Noticed we included the base requirements are installed by the first line.
We can now cleanup the `requirements.txt` file without test packages.
```
$ cat requirements.txt
Django==1.11.3
django-cors-headers==2.1.0
djangorestframework==3.6.3
MySQL-python==1.2.5
pytz==2017.2
```
### Testing the Development Image

Lets first build the container from the development Dockerfile. Set your position in the root of the application.
```
$ cd todobackend
$ tree -L 1
.
├── docker
├── scripts
├── src
└── venv
```

Then, build the image from the development Dockerimage.
```
$ docker build -t todobackend-dev -f docker/dev/Dockerfile .
```
Notice form where we executed the `docker build` command.
The Dockerfile references to the scripts folder. This folder is not in `docker/dev` so the context is wrong if we executed the docker build from there. In order to avoid the inclusion of the virtual environment in the container, we create a `.dockerignore` file (just like .gitignore) and we exclude the virtual environment directory `venv` from the build.

Lets now run a container from out *Development Image*

```
$ docker run --rm todobackend-dev
<lots of output of downloading>
............
----------------------------------------------------------------------
Ran 12 tests in 0.072s

OK
Creating test database for alias 'default'...
System check identified no issues (0 silenced).
Destroying test database for alias 'default'...
```

Now let time our test container
```
$ time docker run --rm todobackend-dev
............
----------------------------------------------------------------------
Ran 12 tests in 0.069s

OK
Creating test database for alias 'default'...
System check identified no issues (0 silenced).
Destroying test database for alias 'default'...
docker run --rm todobackend-dev  0.01s user 0.01s system 0% cpu 12.937 total
```
On average, it takes about 15 seconds. This is because each time we execute a bunch of `pip install` commands, because after we exit, we remove (destroy) the container.

### Reducing Testing Time

If you recall, we added an environment variable to our image `XDG_CACHE_HOME=/cache`.

If you see the output when building the image, the directory `/cache` is being used.

```
Building wheels for collected packages: MySQL-python, pinocchio
  Running setup.py bdist_wheel for MySQL-python: started
  Running setup.py bdist_wheel for MySQL-python: finished with status 'done'
  Stored in directory: /cache/pip/wheels/16/ed/55/f27783bb5ab1cb57c93f1f
  Running setup.py bdist_wheel for pinocchio: started
  Running setup.py bdist_wheel for pinocchio: finished with status 'done'
  Stored in directory: /cache/pip/wheels/ab/43/84/ba075171b712e03d94d14b
```
But when the container ends executing, it gets removed, along with the cache.
Thus, eliminating the benefit of caching.

#### Volume Containers

We need to persist the `/cache` folder between container runs. The best way to achieve this, is by creating a *volume container*. The *volume container* is a especial container that can share its volumes with other containers.

We can also mount volumes inside the *volume container* to a physical path inside the host. Therefore, the data in these mount volumes will persist when the attached containers are removed and destroyed. We can even destroy the *volume container* since the data is persisted in the host machine.

Lets create a *volume container* by using the docker command and specifying the volumes we want to expose.
```
$ cd todobackend
$ docker run -v /tmp/cache:/cache --entrypoint true --name cache todobackend-dev
```

 Note on the command that we are mapping the local host dir `/tmp/cache` to the container's volume `/cache`. Which means the data stored in `/tmp/cache` on the host will persist, even if we destroy the *volume container*.

 We override the entrypoint `--entrypoint true` to make the *volume container* exit immediately without doing anything.

 We also name the container `--name cache` to make it easy to reference when we run our tests.

 Noticed that we created our *volume container* from our development image. This approach ensures that all our users, groups and folder permission are consistent when we run our tests.

 Lets run our container again using the *volume container*.

```
$ docker run --rm --volumes-from cache todobackend-dev
............
----------------------------------------------------------------------
Ran 12 tests in 0.067s

OK
Creating test database for alias 'default'...
 System check identified no issues (0 silenced).
 Destroying test database for alias 'default'...
 docker run --rm --volumes-from cache todobackend-dev  0.01s user 0.01s system 0% cpu 8.213 total
```

We can see the improvement of time because we are using the persistent cache.

### Using Different Test Settings

You have noticed that we are running the base case tests. Recall that we created different settings.
```
$ cd todobackend/src/todobackend
$ tree
.
├── __init__.py
├── __init__.pyc
├── settings
│   ├── __init__.py
│   ├── __init__.pyc
│   ├── base.py
│   ├── base.pyc
│   ├── test.py
│   └── test.pyc
├── settings.pyc
├── urls.py
├── urls.pyc
├── wsgi.py
└── wsgi.pyc

1 directory, 13 files
```
So how can we change the test settings to use other than the default settings?

We need to change the settings and pass that to the container. We do this by setting the environment variable `DJANGO_SETTINGS_MODULE`
```
$ docker run --rm -e DJANGO_SETTINGS_MODULE=todobackend.settings.test \
--volumes-from cache todobackend-dev

<lots of output>

django.db.utils.OperationalError: (2002, "Can't connect to local MySQL server through socket '/var/run/mysqld/mysqld.sock' (2)")
```

Out test will fail since our `todobackend/src/todobackend/settings/test.py` file points to MySQL being installed on the localhost.<br>
*__NOTE:__* Our container is not running MySQL
```
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('MYSQL_DATABASE','todobackend'),
        'USER': os.environ.get('MYSQL_USER','todo'),
        'PASSWORD': os.environ.get('MYSQL_PASSWORD','password'),
        'HOST': os.environ.get('MYSQL_HOST','localhost'),
        'PORT': os.environ.get('MYSQL_PORT','3306'),
        'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
    }
}
```

We could install and run MySQL in our container, but we will be breaking a golden rule: Run a single process per container. So, the best solution is to create another container with MySQL and configure our test container to connect to the MySQL container. We will address this, with multi-container using `docker-compose` in the next lab.
