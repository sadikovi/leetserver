FROM ubuntu:14.04

MAINTAINER Ivan Sadikov <sadikovi@docker.com>

RUN apt-get update && apt-get install -y python-software-properties git
RUN git clone https://github.com/sadikovi/leetserver.git

ENTRYPOINT ["leetserver/bin/start.sh"]
