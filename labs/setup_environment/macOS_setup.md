# Software Setup for macOS


package manager
[Homebrew](http://brew.sh)

You might need to install xcode command line tools in order for brew to work.

For Docker, we will be using

- [Docker Compose](http://docker.com/docker-compose)
- [Docker Engine](http://docker.com/docker-engine)
- [Docker Machine](http://docker.com/docker-machine)
```
$ brew update
$ brew install docker-compose
```  
It has dependencies on `docker` and `docker-machine` <br>
You can still install them if you wish, just to make sure
```
$ brew install docker
$ brew install docker-machine
```

All of these tools are bundled into a toolbox
[Docker Toolbox](https://www.docker.com/products/docker-toolbox)

Installing Ansible

Before installing Ansible, we need to make sure python 2.7 is installed.

`$ brew install python`

The previous command will also install the `pip` python package manager. To ensure we have the most up-to-date pip, we run the following.<br>
`$ pip install pip --upgrade`

We are now ready to install Ansible.

`$ pip install ansible --upgrade`

NOTE: Make sure to include the `--upgrade` flag to ensure we always get the latest version of Ansible.

Install official python SDK to communicate with AWS

`$ pip install boto boto3`

We also need to install the AWS command line tools

`$ pip install awscli`


Installing other tools

Text Editor [Atom](https://atom.io/)

Terminal iterm2

The `tree` command. `$ brew install tree`


#### Create Docker Machine

```
$ docker-machine create --driver virtualbox --cpu-count "4" --disk-size "60000" --memory-size "8192" docker01
```

#### Create working directory

You can place it and name it however you like.
I will Use

`mkdir cd-docker-ansible`

in home directory
