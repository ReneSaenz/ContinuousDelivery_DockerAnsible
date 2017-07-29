# Creating a Multi-Container Environment using Docker Compose

To create an environment involving several containers, we could create each container, and then linking them together manually. However, a better solution is to use docker compose. Docker compose allows us to create a multi-container environment in a declarative, easy to understand format, and then use `docker-compose` commands to orchestrate the environment.

## Creating a Docker Compose File

Let create a docker compose file in the same location as our Dockerfile of the *Development Image*.
```
$ cd todobackend/docker/dev
```
The standard convention in creating a docker compose file is `docker-compose.yml`.

The anatomy of the docker compose yaml file
```
app:                               <-- service called "app" (aka container)
  image: myorg/mycontainer:latest  <-- Image the service is based on
  links:
    - db
  volumes:                         <-- List of volumes to mount
    - /path/to/host:/path  
  volumes_from:                    <-- volume containers to attach
    - cache
  environment:                     <-- environment variables
    - MYSQL_DB:
...

db:
  image: mysql                     <-- another service called "db" (another container)
```

In our case, we will define a "test" service
```
test:
  build: ../../
  dockerfile: docker/dev/Dockerfile
  volumes_from:
    - cache
  links:
    - db
  environment:
    DJANGO_SETTINGS_MODULE: todobackend.settings.test
    MYSQL_HOST: db
    MYSQL_USER: root
    MYSQL_PASSWORD: password
    TEST_OUTPUT_DIR: /reports
```

Notice the `build` section. We need to set the right build context in order for the script to be found. We next define the Dockerfile to build, which must be expressed relative the to build context.
Next, we attach the `cache` volume just like we did before.

We need to create a link to the database service, and we will call it "db".
This will allow the test service to be able to resolve the hostname "db" by adding an entry to the `/etc/hosts` file. Finally, we define the environment variables we will pass to the container at runtime.

Next, we create the cache service we manually created before.
```
cache:
  build: ../../
  dockerfile: docker/dev/Dockerfile
  volumes:
    - /tmp/cache:/cache
    - /build
  entrypoint: "true"
```

### Running Tests using Docker Compose

To run the tests using docker compose, do the following
```
$ cd todobackend/docker/dev
$ docker-compose up test
```
At the end of the run, we will get an error.
```
test_1 | conn = Database.connect(**conn_params)
test_1 | File "/appenv/local/lib/python2.7/site-packages/MySQLdb/__init__.py", line 81, in Connect
test_1 | return Connection(*args, **kwargs)
test_1 | File "/appenv/local/lib/python2.7/site-packages/MySQLdb/connections.py", line 193, in __init__
test_1 | super(Connection, self).__init__(*args, **kwargs2)
test_1 | django.db.utils.OperationalError: (2003, "Can't connect to MySQL server on 'db' (111)")
dev_test_1 exited with code 1
```

Lets troubleshoot what happened. Lets see what has been created by `docker-compose`
```
$ docker-compose ps
   Name                  Command               State     Ports
----------------------------------------------------------------
dev_cache_1   true                             Exit 0
dev_db_1      docker-entrypoint.sh mysqld      Up       3306/tcp
dev_test_1    test.sh python manage.py t ...   Exit 0
```

We can see that the "db" service is running with the port we specified.
Lets explore even more.
```
$ docker-compose logs db
Attaching to dev_db_1
db_1 | Initializing database
db_1 | MySQL init process done. Ready for start up.
db_1 | Database initialized
db_1 | MySQL init process in progress...
```
The service is up and running. Lets run the test again.
```
$ docker-compose up test
test_1 | Ensure we can create a new todo item
test_1 | - item has correct title
test_1 | - item was created
test_1 | - received 201 created status code
test_1 | - received location header hyperlink
test_1 |
test_1 | Ensure we can delete all todo items
test_1 | - all items were deleted
test_1 | - received 204 no content status code
test_1 |
test_1 | Ensure we can delete a todo item
test_1 | - received 204 no content status code
test_1 | - the item was deleted
test_1 |
test_1 | Ensure we can update an existing todo item using PATCH
test_1 | - item was updated
test_1 | - received 200 ok status code
test_1 |
test_1 | Ensure we can update an existing todo item using PUT
test_1 | - item was updated
test_1 | - received 200 created status code
test_1 |
test_1 | ------------------------------------------------------
test_1 | XML: /reports/unittests.xml
test_1 | Name                              Stmts   Miss  Cover
test_1 | -----------------------------------------------------
test_1 | todo/__init__.py                      0      0   100%
test_1 | todo/admin.py                         1      1     0%
test_1 | todo/migrations/0001_initial.py       6      0   100%
test_1 | todo/migrations/__init__.py           0      0   100%
test_1 | todo/models.py                        6      6     0%
test_1 | todo/serializers.py                   7      0   100%
test_1 | todo/urls.py                          6      0   100%
test_1 | todo/views.py                        17      0   100%
test_1 | -----------------------------------------------------
test_1 | TOTAL                                43      7    84%
test_1 | ------------------------------------------------------
test_1 | Ran 12 tests in 0.286s
test_1 |
test_1 | OK
test_1 |
test_1 | nosetests --verbosity=2 --nologcapture --with-coverage --cover-package=todo --with-spec --spec-color --with-xunit --xunit-file=/reports/unittests.xml --cover-xml --cover-xml-file=/reports/coverage.xml
test_1 | Creating test database for alias 'default'...
test_1 | Destroying test database for alias 'default'...
dev_test_1 exited with code 0
```
This time all the test ran successfully. This indicates a race condition.
The problem is that the db services takes longer to initialize and be ready.
The "test" service attempts to connect before it finishes, so it fails.
Even if we created a link to the "db" service to start the "db" service before the "test" service, `docker-compose` does not wait for the service to finish.
And instead, it starts the "test" service immediately after the "db" service.

#### Solving how to wait for a dependent service to initialize

Docker compose does not have in-build mechanism for race conditions.
So we will solve it by using a *helper service* or an *agent Service*
The *agent service* will probe the "db" service and wait until it finish Initializing and is ready for connections. We will create an ansible docker image for our *agent service*. This container will run an ansible playbook.

We will create a new directory in the root folder of our project.
```
$ cd todobackend
$ mkdir docker-ansible
```

We will create generic container with Ansible.
The Dockerfile to produce that image, contains has the following parts.

Installs the latest stable version of ansible
```
# Install Ansible
RUN apt-get update -qy && \
    apt-get install -qy software-properties-common && \
    apt-add-repository -y ppa:ansible/ansible && \
    apt-get update -qy && \
    apt-get install -qy ansible
```

Creates an ansible volume and set the working directory to the ansible volume
```
# Add volume for Ansible playbooks
VOLUME /ansible
WORKDIR /ansible
```

Executes the ansible playbook command
```
# Entrypoint
ENTRYPOINT ["ansible-playbook"]
CMD ["site.yml"]
```

Lets build this container.
```
$ cd docker-ansible
$ docker build -t renesaenz/ansible .
```

We also need to create a folder called `ansible` under the `todobackend` folder.
```
$ cd todobackend
$ mkdir ansible
$ tree -L 1
.
├── ansible
├── docker
├── scripts
├── src
└── venv

5 directories, 0 files
```
Under the `ansible` folder, we will create a playbook called `probe.yml`.
Our playbook will have the ansible tasks to probe the `db` service and see
if it is ready for connections.

Now we need to modify our `docker-compose` file and add the agent service.
```
agent:
  image: renesaenz/ansible
  volumes:
    - ../../ansible/probe.yml:/ansible/site.yml
  links:
    - db
  environment:
    PROBE_HOST: "db"
    PROBE_PORT: "3306"
  command: ["probe.yml"]
```

Lets try out our helper agent
Go to the Docker development image directory
```
$ cd todobackend/docker/dev
$ tree
.
├── Dockerfile
└── docker-compose.yml
```

Then, execute the following to clean up
```
$ docker-compose kill

$ docker-compose rm -f
Going to remove dev_test_1, dev_cache_1, dev_db_1
Removing dev_test_1 ... done
Removing dev_cache_1 ... done
Removing dev_db_1 ... done
```
Now that we have cleaned the previous services created by `docker-compose`,
we can start from new.
```
$ docker-compose up agent
Creating dev_db_1
Creating dev_agent_1
...
agent_1 | PLAY RECAP *********************************************************************
agent_1 | localhost  : ok=3  changed=0  unreachable=0  failed=0
```

It will create the "db" service and will run the helper agent.

We can now run our tests
```
$ docker-compose up test
dev_db_1 is up-to-date
Creating dev_cache_1 ...
Creating dev_cache_1 ... done
Creating dev_test_1 ...
Creating dev_test_1 ... done
Attaching to dev_test_1
...
test_1     | ----------------------------------------------------------------------
test_1     | XML: /reports/unittests.xml
test_1     | Name                              Stmts   Miss  Cover
test_1     | -----------------------------------------------------
test_1     | todo/__init__.py                      0      0   100%
test_1     | todo/admin.py                         1      1     0%
test_1     | todo/migrations/0001_initial.py       6      0   100%
test_1     | todo/migrations/__init__.py           0      0   100%
test_1     | todo/models.py                        6      6     0%
test_1     | todo/serializers.py                   7      0   100%
test_1     | todo/urls.py                          6      0   100%
test_1     | todo/views.py                        17      0   100%
test_1     | -----------------------------------------------------
test_1     | TOTAL                                43      7    84%
test_1     | ----------------------------------------------------------------------
test_1     | Ran 12 tests in 0.298s
test_1     |
test_1     | OK
test_1     |
test_1     | nosetests --verbosity=2 --nologcapture --with-coverage --cover-package=todo --with-spec --spec-color --with-xunit --xunit-file=/reports/unittests.xml --cover-xml --cover-xml-file=/reports/coverage.xml
test_1     | Creating test database for alias 'default'...
test_1     | Destroying test database for alias 'default'...
dev_test_1 exited with code 0
```
And our tests run successfully every time now, since we have assured the "db" service is up and running and ready for connections.
