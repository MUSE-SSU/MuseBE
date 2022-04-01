FROM ubuntu:20.04

MAINTAINER kyoungnam

#ENV DOCKER_DEFAULT_PLATFORM=linux/amd64

# Local directory with project source
ENV DOCKER_SRC=MuseDjango
# Directory in container for all project files
ENV DOCKER_SRVHOME=/srv
# Directory in container for project source files
ENV DOCKER_SRVPROJ=$DOCKER_SRVHOME/$DOCKER_SRC
# Set Timezone
ENV TZ='Asia/Seoul'
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Update the default application repository sources list
RUN apt-get -y update
RUN apt-get install -y python3 python3-pip python3-dev
RUN apt-get install -y apt-utils
RUN pip3 install --upgrade pip
RUN apt-get install -y libssl-dev
RUN apt-get install -y mysql-server
RUN apt-get install -y libmysqlclient-dev
RUN apt-get install -y git
RUN apt-get install -y vim
RUN pip3 install gunicorn
RUN apt-get install -y nginx
RUN apt-get install --reinstall -y systemd
RUN apt-get install -y cron

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
COPY $DOCKER_SRC/notice $DOCKER_SRVPROJ/notice
COPY $DOCKER_SRC/notification $DOCKER_SRVPROJ/notification

WORKDIR $DOCKER_SRVPROJ

# COPY ./nginx/default.conf /etc/nginx/sites-available/
# RUN ln -s /etc/nginx/sites-available/default.conf /etc/nginx/sites-enabled
# RUN echo "daemon off;" >> /etc/nginx/nginx.conf

COPY ./docker-entrypoint.sh /
RUN ["chmod", "+x", "/docker-entrypoint.sh"]
ENTRYPOINT ["/docker-entrypoint.sh"]

#COPY ./docker-entrypoint.sh /
#ENTRYPOINT ["/docker-entrypoint.sh"]

# CMD ["gunicorn", "--bind", "0:8080", "config.wsgi:application"]

# ENTRYPOINT ["./entrypoint.sh"]
# CMD python3 manage.py runserver 0.0.0.0:8080
