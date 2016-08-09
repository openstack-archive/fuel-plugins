FROM centos:7

RUN yum update -y; yum clean all

RUN yum install -y epel-release
RUN yum install -y git
RUN yum install -y python-pip python-wheel
RUN yum install -y rpm-build createrepo dpkg-scanpackages

#install epel as we need dpkg from epel-testing
RUN yum -y install epel-release
#install dpkg binaries from epel-testing
RUN yum -y install --enablerepo=epel-testing dpkg-dev tar

RUN mkdir /build
VOLUME /build

COPY . /fuel-plugins

WORKDIR /fuel-plugins
RUN python setup.py install
RUN pip install -r requirements.txt

ENTRYPOINT cd /build/test_plugin && fpb --build .
