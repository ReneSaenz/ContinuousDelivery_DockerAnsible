# Creating a Docker Base Image

Before we get into creating a Docker base image, we first need to go over some concepts.

## Docker Image Hierarchy

Key feature of Docker is to create a hierarchy of images.
With child images inheriting all of the state and behavior of parent images. It is strongly recommended to create a base image.
The base image will satisfy *__Minimum Runtime Environment__*.

We need to focus on the work *minimum*: We need to reduce the footprint of the runtime environment as much as possible to increase performance and reduce attack surface.

Runtime Environment (Base Image) consists of

- Application dependencies
- System Configuration
- Default Settings

With the *Base Image* defined, the application is then installed in a *__Release Image__* which is a child of the Base Image.

The *Release Image* contains the full runtime of the application. Creating the release image consists of:

- Installing the application
- Application Configuration
- Application entry-point

Taking the approach, promotes reusability and separation of concerns and responsibilities.
For example, we can have an operation team responsable of maintaining the *Base Image* by applying operating and security updates to the *Base Image*. Developers then only be responsable for the application itself. By each application release, creating a new *Release Image*, without caring about the underlying *Base Image*.

Another advantage of Docker image hierarchy, is the ability to create other images such as *__Development Image__* as a child of the *Base Image*. The advantage is that the Base Image already contains the core dependencies of the application. Thus the *Development Image*
only needs to add development and test dependencies.

- Install Dev dependencies
- Install Test/Build tools

In later labs, we will go over how to use the *Development Image* to Test, Build and Release phase. Creating Application Artifacts which can eventually be deployed to production.

## Creating the Base Image

We will maintain in a separate repository since it has a different cadance than the application.

Create a new folder where the *Dockerfile* for the base image will be located.

```
$ mkdir todobackend-docker-base
$ tree -L 1
.
├── todobackend
├── todobackend-client
├── todobackend-docker-base
└── todobackend-specs

4 directories, 0 files
```

Create a Dockerfile for our Docker base image

```
$ cd todobackend-docker-base
```

Initial Dockerfile
```
FROM ubuntu:trusty
MAINTAINER Rene Saenz <rene.saenz@gmail.com>

# Prevent dpkg errors
ENV TERM=xterm-256color

# Install Python runtime
RUN apt-get update && \
    apt-get install -qy \
    -o APT::Install-Recommend=false -o APT::Install-Suggests=false \
    python python-virtualenv
```
##### Establish the Virtual Environment

We can now focus on the virtual environment where our application will run. To read more about it, please read
[Hynek Schlawack](https://hynek.me/articles/virtualenv-lives/)

Add code to the Dockerfile to create the virtual environment.
```
# Create virtual environment
# Upgrade PIP in virtual environment to latest version
RUN virtualenv /appenv && \
    . /appenv/bin/activate && \
    pip install pip --upgrade
```

*__NOTE:__* The dot instead of the *source* command. This is because Docker supports bash which does not support *source* command.

We want our application to run in the virtual environment. So we need to make sure that our entry-point script does that.
We need to add our custom entry-point script to the execution path of the container, so that it will be accessible from anywhere.
```
# Add entrypoint script
ADD scripts/entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh
ENTRYPOINT ["entrypoint.sh"]
```

We now need to create our entry-point script.
```
$ cd todobackend-docker-base
$ mkdir scripts
$ touch scripts/entrypoint.sh
$ tree
.
├── Dockerfile
└── scripts
    └── entrypoint.sh

1 directory, 2 files
```

## Building the base image

To build the image, execute the following
```
$ cd todobackend-docker-base
$ docker build -t renesaenz/todobackend-docker-base .
...
```
After the Docker image is build, let test it.<br>
*__NOTE:__* the flag `--rm` is to automatically remove the container after it exits.

The container will run `entrypoint.sh ps`
```
$ docker run --rm renesaenz/todobackend-base ps
/usr/local/bin/entrypoint.sh: line 4: ./appenv/bin/activate: Permission denied
  PID TTY          TIME CMD
    1 ?        00:00:00 ps
```
Notice the process ID of `ps` is one. This means the application process will receive a SIGTERM signal when the container is stopped.
Allowing the application process, to gracefully terminate.
