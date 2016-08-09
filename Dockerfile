FROM centos:7
RUN yum install -y epel-release
RUN yum install -y git
RUN yum install -y python-pip python-wheel
RUN yum install -y rpm-build createrepo dpkg-scanpackages
#install epel as we need dpkg from epel-testing
RUN yum -y install epel-release
#install dpkg binaries from epel-testing
RUN yum -y install --enablerepo=epel-testing dpkg-dev tar

COPY . /tmp/fuel-plugins
WORKDIR /tmp/fuel-plugins/
RUN python setup.py install
RUN pip install -r requirements.txt
WORKDIR /tmp/
RUN ls /usr/lib/python2.7/site-packages/fuel_plugin_builder/
RUN fpb --create test_plugin
WORKDIR /tmp/test_plugin/
RUN fpb --build .
