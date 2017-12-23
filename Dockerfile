FROM ubuntu
RUN apt-get update

# Mopidy Installation
RUN apt-get -y install wget
RUN wget -q -O - https://apt.mopidy.com/mopidy.gpg | apt-key add -
RUN wget -q -O /etc/apt/sources.list.d/mopidy.list https://apt.mopidy.com/jessie.list
RUN apt-get update
RUN apt-get -y install mopidy python-pip
RUN pip install Mopidy-Moped

# Copy config
RUN mkdir -p /root/.config/mopidy
COPY ./docker/mopidy.conf /root/.config/mopidy

COPY ./docker/strobe.m3u /root/playlists/strobe.m3u
COPY ./docker/05-Strobe.mp3 /root/music/05-Strobe.mp3
COPY ./ /root/mopidy_alarmclock

# Scan for music hopefully
RUN mopidy local scan

# The real shiit
RUN pip install -e /root/mopidy_alarmclock
ENTRYPOINT mopidy