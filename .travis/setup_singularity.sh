#!/bin/bash -ex

sudo sed -i -e 's/^Defaults\tsecure_path.*$//' /etc/sudoers

# Check Python

echo "Python Version:"
python --version
pip install sregistry[all]
sregistry version

echo "sregistry Version:"

# Install Singularity

SINGULARITY_BASE="${GOPATH}/src/github.com/sylabs/singularity"
export PATH="${GOPATH}/bin:${PATH}"

mkdir -p "${GOPATH}/src/github.com/sylabs"
cd "${GOPATH}/src/github.com/sylabs"

git clone -b 2.6.1 https://github.com/sylabs/singularity
cd singularity
# These are the Singularity 2 installation commands:
./autogen.sh
./configure --prefix=/usr/local --sysconfdir=/etc
make
sudo make install
# These are the Singularity 3 installation commands:
# ./mconfig -v -p /usr/local
# make -j `nproc 2>/dev/null || echo 1` -C ./builddir all
# sudo make -C ./builddir install
