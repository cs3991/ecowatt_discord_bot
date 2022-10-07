# set base image (host OS)
FROM python:3.10-slim-bullseye

# set the working directory in the container
WORKDIR /code

# install locales
RUN apt-get update
RUN apt-get install -y locales locales-all
ENV LC_ALL fr_FR.UTF-8
ENV LANG fr_FR.UTF-8
ENV LANGUAGE fr_FR.UTF-8


# copy the dependencies file to the working directory
COPY requirements.txt .

# install dependencies
RUN pip install -r requirements.txt

# copy the content of the local src directory to the working directory
COPY . .

# pour pouvoir avoir la sortie erreur dans les logs
ENV PYTHONUNBUFFERED=1

# command to run on container start
ENTRYPOINT ["/bin/sh", "-c" , "python3 -u /code/main.py"]
