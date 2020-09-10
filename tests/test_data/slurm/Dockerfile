FROM centos:7

LABEL org.opencontainers.image.source="https://github.com/giovtorres/slurm-docker-cluster" \
      org.opencontainers.image.title="slurm-docker-cluster" \
      org.opencontainers.image.description="Slurm Docker cluster on CentOS 7" \
      org.label-schema.docker.cmd="docker-compose up -d" \
      maintainer="Giovanni Torres"

ARG SLURM_TAG=slurm-19-05-1-2
ARG GOSU_VERSION=1.11

RUN set -ex \
    && yum makecache fast \
    && yum -y update \
    && yum -y install epel-release \
    && yum -y install \
       wget \
       bzip2 \
       perl \
       gcc \
       gcc-c++\
       git \
       gnupg \
       make \
       munge \
       munge-devel \
       python-devel \
       python-pip \
       python34 \
       python34-devel \
       python34-pip \
       mariadb-server \
       mariadb-devel \
       psmisc \
       bash-completion \
       vim-enhanced \
    && yum clean all \
    && rm -rf /var/cache/yum

RUN pip install Cython nose && pip3.4 install Cython nose

RUN set -ex \
    && wget -O /usr/local/bin/gosu "https://github.com/tianon/gosu/releases/download/$GOSU_VERSION/gosu-amd64" \
    && wget -O /usr/local/bin/gosu.asc "https://github.com/tianon/gosu/releases/download/$GOSU_VERSION/gosu-amd64.asc" \
    && export GNUPGHOME="$(mktemp -d)" \
    && gpg --keyserver ha.pool.sks-keyservers.net --recv-keys B42F6819007F00F88E364FD4036A9C25BF357DD4 \
    && gpg --batch --verify /usr/local/bin/gosu.asc /usr/local/bin/gosu \
    && rm -rf "${GNUPGHOME}" /usr/local/bin/gosu.asc \
    && chmod +x /usr/local/bin/gosu \
    && gosu nobody true

RUN set -x \
    && git clone https://github.com/SchedMD/slurm.git \
    && pushd slurm \
    && git checkout tags/$SLURM_TAG \
    && ./configure --enable-debug --prefix=/usr --sysconfdir=/etc/slurm \
        --with-mysql_config=/usr/bin  --libdir=/usr/lib64 \
    && make install \
    && install -D -m644 etc/cgroup.conf.example /etc/slurm/cgroup.conf.example \
    && install -D -m644 etc/slurm.conf.example /etc/slurm/slurm.conf.example \
    && install -D -m644 etc/slurmdbd.conf.example /etc/slurm/slurmdbd.conf.example \
    && install -D -m644 contribs/slurm_completion_help/slurm_completion.sh /etc/profile.d/slurm_completion.sh \
    && popd \
    && rm -rf slurm \
    && groupadd -r --gid=995 slurm \
    && useradd -r -g slurm --uid=995 slurm \
    && mkdir /etc/sysconfig/slurm \
        /var/spool/slurmd \
        /var/run/slurmd \
        /var/run/slurmdbd \
        /var/lib/slurmd \
        /var/log/slurm \
        /data \
    && touch /var/lib/slurmd/node_state \
        /var/lib/slurmd/front_end_state \
        /var/lib/slurmd/job_state \
        /var/lib/slurmd/resv_state \
        /var/lib/slurmd/trigger_state \
        /var/lib/slurmd/assoc_mgr_state \
        /var/lib/slurmd/assoc_usage \
        /var/lib/slurmd/qos_usage \
        /var/lib/slurmd/fed_mgr_state \
    && chown -R slurm:slurm /var/*/slurm* \
    && /sbin/create-munge-key

COPY slurm.conf /etc/slurm/slurm.conf
COPY slurmdbd.conf /etc/slurm/slurmdbd.conf

COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]


# Install SSH server
RUN yum -y install \
       openssh-server \
       openssh-clients &&\
    touch /run/utmp && \
    chmod u+s /usr/bin/ping && \
    echo "root:root" | chpasswd

RUN sed -i "0,/ListenAddress.*/c\#ListenAddress 0.0.0.0" /etc/ssh/sshd_config

COPY id_rsa.pub /root/.ssh/authorized_keys


# Install Singularity
RUN wget https://dl.google.com/go/go1.13.linux-amd64.tar.gz && \
    tar -C /usr/local -xzvf go1.13.linux-amd64.tar.gz && \
    rm go1.13.linux-amd64.tar.gz
ENV PATH=/usr/local/go/bin:$PATH
RUN wget https://github.com/sylabs/singularity/releases/download/v3.6.1/singularity-3.6.1.tar.gz && \
    tar -xzf singularity-3.6.1.tar.gz && \
    cd singularity && \
    ./mconfig && \
    make -C builddir && \
    make -C builddir install && \
    rm -Rf singularity-3.6.1.tar.gz singularity
RUN yum -y install squashfs-tools iptables-services net-tools
RUN echo 'root:100000:65536' > /etc/subuid
RUN echo 'root:100000:65536' > /etc/subgid

# Install conda
RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O /opt/miniconda.sh && \
    bash /opt/miniconda.sh -b -fp /opt/miniconda/ && \
    rm /opt/miniconda.sh
ENV PATH=/opt/miniconda/bin:$PATH


CMD ["slurmdbd"]
