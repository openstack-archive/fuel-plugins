docker build -t builder .
rm -rf ../build
mkdir ../build
docker run -v `pwd`/:/fuel-plugins -v  `cd .. && pwd`/build/:/build builder