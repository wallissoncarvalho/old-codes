FROM python:3.7-alpine

#SETTING THE PYTHON UNBUFFERED ENVIROMENT VARIABLE
#What this does is it tells python to run in unbuffered mode which is recommended when running Python within a Docker Containers
#The reason for this is that it doesn't allow Python to buffer the outputs
ENV PYTHONUNBUFFERED 1


#COPYING THE REQUERIMENTS FILE FROM THE PROJECT ROOT TO /REQUIREMENTS.TXT
COPY ./requirements.txt /requirements.txt

#TAKING THE REQUIREMENTS FILE THAT WE'VE JUST COPIED AND IT INSTALLS USING PIP INTO THE DOCKER IMAGE
RUN pip install -r /requirements.txt

#MAKING A DIRECTORY WITHIN OUR DOCKER IMAGE THAT WE CAN USE TO STORE THE APPLICATION SOURCE CODE

#CREATING AN EMPY FOLDER ON THE DOCKER IMAGE
RUN mkdir /app
#SWITCHING  TO THE APP FOLDER AS THE DEFAULT DIRECTORY
WORKDIR /app
#COPYING FROM THE LOCAL MACHINE THE APP FOLDER TO THE APP FOLDER IN THE DOCKER IMAGE
COPY ./app /app

#CREATING AN INTERNAL USER FOR SECURITY PROPORSES
RUN adduser -D user
USER user