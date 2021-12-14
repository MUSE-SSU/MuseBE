# Set the base image to use to Ubuntu
FROM ubuntu:20.04

# Set the file maintainer (your name - the file's author)
MAINTAINER kyoungnam

#ENV DOCKER_DEFAULT_PLATFORM=linux/amd64

# Local directory with project source
ENV DOCKER_SRC=MuseDjango
# Directory in container for all project files
ENV DOCKER_SRVHOME=/srv
# Directory in container for project source files
ENV DOCKER_SRVPROJ=$DOCKER_SRVHOME/$DOCKER_SRC
# Set TImezone
ENV TZ='Asia/Seoul'
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Update the default application repository sources list
RUN apt-get -y update
RUN apt-get install -y python3 python3-pip python3-dev
RUN apt-get install -y apt-utils
# RUN apt-get install -y tzdata
# RUN apt-get install -y gcc
# RUN cd /usr/local/bin
# RUN ln -s /usr/bin/python3 python
RUN pip3 install --upgrade pip
RUN apt-get install -y libssl-dev
RUN apt-get install -y mysql-server
RUN apt-get install -y libmysqlclient-dev
RUN apt-get install -y git
RUN apt-get install -y vim
RUN apt-get install -y nginx
RUN apt-get install --reinstall -y systemd
RUN apt-get install -y cron
#ffmpeg
RUN apt-get install -y ffmpeg

#locale
RUN apt-get install -y language-pack-ko
RUN locale-gen ko_KR.UTF-8

# Create application subdirectories
WORKDIR $DOCKER_SRVHOME
RUN mkdir logs
#read
VOLUME ["$DOCKER_SRVHOME/logs/"]
# Copy application source code to SRCDIR
COPY $DOCKER_SRC/requirements.txt $DOCKER_SRVPROJ/requirements.txt
# Install Python dependencies
RUN pip3 install -r $DOCKER_SRVPROJ/requirements.txt

ARG STAGE

ENV STAGE=$STAGE

#COPY sources
COPY $DOCKER_SRC/manage.py $DOCKER_SRVPROJ/manage.py
COPY $DOCKER_SRC/my_settings.py $DOCKER_SRVPROJ/my_settings.py
COPY $DOCKER_SRC/static $DOCKER_SRVPROJ/static
COPY $DOCKER_SRC/common $DOCKER_SRVPROJ/common
COPY $DOCKER_SRC/config $DOCKER_SRVPROJ/config
COPY $DOCKER_SRC/accounts $DOCKER_SRVPROJ/accounts
COPY $DOCKER_SRC/musepost $DOCKER_SRVPROJ/musepost
COPY $DOCKER_SRC/topics $DOCKER_SRVPROJ/topics

# EXPOSE: 네트워크 상에서 컨테이너로 들어오는 트래픽 리스닝하는 포트와 프로토콜 지정.
# 프로토콜 지정 안하면 기본값 TCP
EXPOSE 8080
WORKDIR $DOCKER_SRVPROJ

ENTRYPOINT ["python3", "manage.py", "runserver", "0.0.0.0:8080"]

# ENTRYPOINT ["./entrypoint.sh"]
# CMD python3 manage.py runserver 0.0.0.0:8080
