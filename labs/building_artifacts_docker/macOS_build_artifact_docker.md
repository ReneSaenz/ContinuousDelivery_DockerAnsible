# Building Artifacts Using Docker

Review of the __Continuous Delivery Workflow__

1. Test. This was completed in the previous lab. When completed, it certifies that the application passed all of the unit tests and integration tests.
At this point, the application is ready to be encapsulated into an artifact.

2. Build. This step creates the application artifacts, that will then serve
as inputs for release and deploy steps.
3. Release
4. Deploy


## Build Workflow Using Docker

1. Create build environment -  Reuse test environment and create builder service.
2. Build Artifacts - Compile source and build python wheels.
3. Publish Artifacts. Publish locally - release stage inputs.

#### Application Artifact Types

There are 2 artifact types that server different purposes.

1. __Source Distribution__ Builds the source code of the application, adds some metadata and creates a deployable archive. This makes it easy to transport your source code, and extracted into the target machine. You will still need to compile the source code into a binary. Source distributions, are ideal for development purposes. They are not for production environments, as they require build and download dependencies, that will invalidate unit and integration testing that already been performed.
2. __Built Distribution__ Build the source code, downloads any dependencies and compiles the source code into a binary that is then packaged into a deployable format. Built distributions, creates an installable package that does not require any compilation or build step when de deploy the application.
This is ideal for general deployment of the application including production environments.

The standard python build distributions are called a
[python wheel](https://www.python.org/dev/psps/pep-0427/)

### Building Application Artifacts

##### Add package metadata to application
We need to add metadata, to describe how to build the artifact.
```
name = "todobackend"      <-- Package name
version = "0.1"           <-- Package version
install_requires = [      <-- Application dependencies
   "Django>=1.8.6",
   "MySQL-python>=1.25",
  ...                     <-- other settings
]
```
This metadata will be used by build tools, to create application artifacts.

By default, Django does not add any metadata to projects, so we will need to add our own metadata. In the python world, a file called `setup.py` located in the root, is the standard way to add metadata. Lets create it.
```
$ cd todobackend/src
$ touch setup.py
```
Edit `todobackend/src/setup.py` and use the `setup()` function to define the metadata for the application.
```
setup(
  name                 = "todobackend",
  version              = "0.1.0",
  description          = "Todobackend Django REST service",
  packages             = find_packages(),
  include_package_data = True,
  install_requires     = ["Django>=1.9,<2.0",
                          "django-cors-headers>=1.1.0",
                          "djangorestframework>=3.3.1",
                          "MySQL-python>=1.2.5",
                          "uwsgi>=2.0"],
  extras_require       = {
                            "test": [
                              "colorama>=0.3.3",
                              "coverage>=4.0.3",
                              "django-nose>=1.4.2",
                              "nose>=1.3.7",
                              "pinocchio>=0.4.2"
                            ]
                         }
  )
```
Notice the use of the `find_packages()` function to specify the application packages. This function will scan all subdirectories and include any folder, that has a `__init__.py` file in it as a package.

The `include_package_data` attribute, indicates to include the packages in the distribution.

The `install_requires` setting, contains the output when we executed `pip freeze` command. We need to then modify the `todobackend/src/requirements.txt` file and just enter a dot. This will indicate python to look at the requirements in `setup.py.`

The `extras_require` setting contains any extra packages that we need.
In this section, we can include all the packages we need to perform testing.
Just like the `requirements.txt` file, we do the same with `todobackend/src/requirements_test.txt` and modify it to this.
```
-e .[test]
```
The previous line tells `pip` to additionally install the "test" array of dependencies in the `extras_require` settings of `setup.py`

The question is if we need `requirements.txt` and `requirements_test.txt` since they are now pointers to `setup.py`. The answer is yes and we can read more about it in the article
[setup vs requirements](https://caremad.io/2013/07/setup-vs-requirement/)

There is another *optional* file called `MANIFEST.in` that is located in the same directory as `setup.py`. It specifies any additional files that you want to include in your application. This is useful for static assets like images.
In our case, we do not need it in our web service. For more information about this file, read the article for [The MANIFEST.in template](https://docs.python.org/2/distutils/sourcedist.html#the -manifest-in-template)


##### Test and Build Consistency
Ensuring consistency between the *Test Stage* and the *Build Stage* is critical requirement in our workflow. Meaning, the ***same*** code is being used in the test stage and the build stage. The same goes for any packages. They need to be the same package and version.

In our `setup.py` file, we relaxed our package dependencies setting a range for the package version, rather than a specific one. This can cause inconsistencies between the test stage and the build stage.

To solve this, we will create a *build cache*. Our test service will download dependencies to a cache folder. Then our test runs based on the *build cache*.
At the build stage, we will use the *build cache* that was used by our test service, rather than downloading the dependencies again.

The idea is that we create a snapshot of the dependencies, that can later be used. Guaranteeing consistency between *Test Stage* and *Build Stage*

##### Adding a Builder Service
Lets now implement our *build cache*. First, we need to modify entry-point script of our Docker development image `todobackend/docker/scripts/test.sh`
```
pip download -d /build -r requirements_test.txt --no-input

pip install --no-index -f /build -r requirements_test.txt
```
We also need to modify our development image, adding `/build` as a volume.
This volume will be shared between our *Test* and *Build* stages.
We modify `todobackend/docker/dev/Dockerfile`. Insert after `wheelhouse` volume.
```
# OUTPUT: Build cache
VOLUME /build
```
Now lets update our test environment specification, which is defined in `todobackend/docker/dev/docker-compose.yml` file.

First, lets add a volume to the *cache service*
```
cache:
  build: ../../
  dockerfile: docker/dev/Dockerfile
  volumes:
    - /tmp/cache:/cache
    - /build
  entrypoint: "true"
```
Because our *test service* is already obtaining volumes from our *cache service*, this will automatically mount the `/build` folder created in the *test service* to the `/build` folder in the *cache service*.
And by configuring the *builder service* to obtain volumes from the *cache service*, we will be able to share the *build cache*.

Lets create the *builder service*. This service will need all of the
development and build dependencies, so we use the same configuration as the development images.
```
test:
  build: ../../
  dockerfile: docker/dev/Dockerfile
  volumes_from:
    - cache
  links:
    - db
...

builder:
  build: ../../
  dockerfile: docker/dev/Dockerfile
  volumes:
    - ../../target:wheelhouse
  volumes_from:
    - cache
  entrypoint: "entrypoint.sh"
  command: ["pip", "wheel", "--no-index", "-f /build", "."]
```
Notice the `volume_from`. The *test service* populates during test stage with application source and dependencies. The *build service* consumes the cage during build stage.

Also notice the entrypoint section. We use the base image entrypoint script.
Which activates the virtual environment, without running `pip install`.
Then specify the command, which tells `pip` to install `wheels` with the `--no-index` option, to not download any dependencies externally. Instead, use the `/build` folder. The final parameter (dot) instructs to use `setup.py` located at the current directory.


##### Build and Publish Python Wheels

Since we modified our source code, modifying the *test service* to use  a *build cache*, we need to re-run the test stage to pickup these changes.
```
$ cd todobackend/docker/dev
$ docker-compose kill
$ docker-compose rm -f
$ docker-compose up agent
$ docker-compose up test
```
At a closer look at the output, we will see that there are no references to the `/build` folder. Furthermore, the development image is never rebuilt.
executing `docker images` we will see that the development image is not seconds old. Confirming that the image was not rebuild on the last `docker-compose` command. The `docker-compose up` command will always use a cache image if available.

To fix this, we should always run the `docker-compose build` command before we start our CD workflow, to ensure that any images that need to be built for the workflow, are up-to-date with the development image. And most importantly, the latest application source code.
For more information read [docker-compose build](https://docs.docker.com/compose/reference/build/)

Lets clean up again and try again
```
$ docker-compose kill
Killing dev_db_1 ... done
```

```
$ docker-compose rm -f
Going to remove dev_test_1, dev_cache_1, dev_agent_1, dev_db_1
Removing dev_test_1 ... done
Removing dev_cache_1 ... done
Removing dev_agent_1 ... done
Removing dev_db_1 ... done
```
```
$ docker-compose build
Building cache
...

Step 9/14 : COPY scripts/test.sh /usr/local/bin/test.sh
 ---> Using cache
 ---> 5cbc643c4791

...

Step 13/14 : COPY src /application
 ---> Using cache
 ---> 7193c6a5f8b3

```
Notice that we are executing the `test.sh` script (step 9). Our application source code is also being copied (step 13)

We can now run our agent and tests.
```
$ docker-compose up agent
```

```
$ docker-compose up test
...
test_1 | Obtaining file:///application (from -r requirements_test.txt (line 1))
test_1 | Saved /build/todobackend-0.1.0.zip

test_1 | Collecting django-cors-headers>=1.1.0 (from todobackend==0.1.0->-r requirements_test.txt (line 1))
test_1 | Using cached django_cors_headers-2.1.0-py2.py3-none-any.whl
test_1 | Saved /build/django_cors_headers-2.1.0-py2.py3-none-any.whl
test_1 | Collecting djangorestframework>=3.3.1 (from todobackend==0.1.0->-r requirements_test.txt (line 1))
test_1 | Using cached djangorestframework-3.6.3-py2.py3-none-any.whl
test_1 | Saved /build/djangorestframework-3.6.3-py2.py3-none-any.whl
test_1 | Collecting MySQL-python>=1.2.5 (from todobackend==0.1.0->-r requirements_test.txt (line 1))
test_1 | Using cached MySQL-python-1.2.5.zip
test_1 | Saved /build/MySQL-python-1.2.5.zip
...
test_1 | Installing collected packages: pytz, Django, django-cors-headers, djangorestframework, MySQL-python, uwsgi, colorama, coverage, nose, django-nose, pinocchio, todobackend
```
Notice that now our source code and dependencies are being saved in `/build` folder, which is later used to install them.

Now that our development image, and our tests are passing, we now can build our application artifacts using `docker-compose up builder` command.
```
$ docker-compose up builder
Starting dev_cache_1 ...
Starting dev_cache_1 ... done
Creating dev_builder_1 ...
Creating dev_builder_1 ... done
Attaching to dev_builder_1
builder_1 | Processing /application
builder_1 | Collecting Django<2.0,>=1.9 (from todobackend==0.1.0)
builder_1 |   Saved /wheelhouse/Django-1.11.3-py2.py3-none-any.whl
builder_1 | Collecting django-cors-headers>=1.1.0 (from todobackend==0.1.0)
builder_1 |   Saved /wheelhouse/django_cors_headers-2.1.0-py2.py3-none-any.whl
builder_1 | Collecting djangorestframework>=3.3.1 (from todobackend==0.1.0)
builder_1 |   Saved /wheelhouse/djangorestframework-3.6.3-py2.py3-none-any.whl
builder_1 | Collecting MySQL-python>=1.2.5 (from todobackend==0.1.0)
builder_1 |   Saved /wheelhouse/MySQL_python-1.2.5-cp27-cp27mu-linux_x86_64.whl
builder_1 | Collecting uwsgi>=2.0 (from todobackend==0.1.0)
builder_1 |   Saved /wheelhouse/uWSGI-2.0.15-cp27-cp27mu-linux_x86_64.whl
builder_1 | Collecting pytz (from Django<2.0,>=1.9->todobackend==0.1.0)
builder_1 |   Saved /wheelhouse/pytz-2017.2-py2.py3-none-any.whl
builder_1 | Skipping Django, due to already being wheel.
builder_1 | Skipping django-cors-headers, due to already being wheel.
builder_1 | Skipping djangorestframework, due to already being wheel.
builder_1 | Skipping MySQL-python, due to already being wheel.
builder_1 | Skipping uwsgi, due to already being wheel.
builder_1 | Skipping pytz, due to already being wheel.
builder_1 | Building wheels for collected packages: todobackend
builder_1 |   Running setup.py bdist_wheel for todobackend: started
builder_1 |   Running setup.py bdist_wheel for todobackend: finished with status 'done'
builder_1 | Stored in directory: /wheelhouse
builder_1 | Successfully built todobackend
dev_builder_1 exited with code 0

```
Notice how wheels are now being created in the `/wheelhouse` folder for all the application dependencies. Along with the wheel for our application.
We will use these set of binaries later on to install the application and its dependencies into a release image, without having to rely on external repos.

Now, you will see a `target` directory in the root of the application.
```
$ cd todobackend
$ tree -L 1
.
├── Jenkinsfile
├── Makefile
├── Makefile.v2
├── README.md
├── docker
├── reports
├── scripts
├── src
└── target
```
The target directory contains the application and dependencies wheels.

 
