sudo python setup.py install
mkdir -p ./.docker_build/ && cd ./.docker_build/
rm -rf ./release-plugin
fpb --create release-plugin --fuel-import --library-path ../../fuel-library --nailgun-path ../../fuel-web/nailgun/nailgun
cd ..
tox -edocker