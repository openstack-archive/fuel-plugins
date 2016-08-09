

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

VOLUME ['/fuel-plugins', '/build']

ENTRYPOINT cd /fuel-plugins; pip install -r requirements.txt; python setup.py install; cd /build; fpb --create test_plugin; fpb --build /build/test_plugin
