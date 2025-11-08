[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/qtTaGRfE)

# Running the Docker Container

This runs on the python:3 Docker image. Run:
`$ docker image pull python:3`
if you do not have the image already.
Then, on the _/ucl-cc-beariables-birmingham/_ directory:
`$ docker build -t dashboard:latest .`
to build the dashboard image.
Finally:
`$ docker run dashboard:latest`
to run dashboard image.
