FROM 10.160.140.32:5000/letv-centos6
MAINTAINER bingzheng.zhou <zhoubingzheng@letv.com>

RUN rpm -ivh http://pkg-repo.oss.letv.com/pkgs/centos6/letv-release.noarch.rpm
RUN yum install jetty -y
RUN yum install vim -y
RUN yum install java-1.7.0-openjdk-devel -y

EXPOSE 8080 8888 9888
USER root

ADD ./file/jetty /etc/init.d/jetty
RUN chmod 755 /etc/init.d/jetty

RUN yum install gbalancer -y
RUN yum install gbalancer-manager -y
RUN yum install jetty-manager -y

ENTRYPOINT bash service gbalancer-manager start && service jetty-manager restart && /bin/bash