# MacOS Unit and Integration Testing using Docker

## Continuous Delivery Workflow

The continuous delivery workflow is composed of 4 stages

1. Testing
2. Build
3. Release
4. Deploy

In this lab, we will focus on the first stage; Test.
This lab is based on the work of the previous lab [Acceptance Testing](labs/acceptance_testing/readme.md)

So we already have the building blocks.
In this lab, we will create a Docker workflow to conduct our tests in an automatic, reliable, consistent and performant manner.

This lab is composed of 3 parts

1. [Create base image](creating_docker_base_image.md)
2. [Create development image](creating_docker_dev_image.md)
3. [Multi-Container](multi_container_testing.md) testing environment using `docker-compose`
