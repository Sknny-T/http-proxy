FROM ubuntu:latest
ENV DEBIAN_FRONTEND noninteractive

# Install latest scapy (with all its dependencies)

RUN apt-get update && \
    apt-get install -y \
    zip \
    unzip \
    python3 \
    python3-pyx \
    python3-matplotlib \
    tcpdump \
    python3-crypto \
    graphviz \
    imagemagick \
    gnuplot \
    python3-gnuplot \
    git \
    re \   
    libpcap-dev && apt-get clean

ADD https://github.com/secdev/scapy/archive/master.zip /tmp/master.zip
RUN unzip /tmp/master.zip -d /usr/local/ && rm /tmp/master.zip

RUN apt-get update && \
    apt-get -qq -y install \
    bridge-utils \
    net-tools \
    iptables \
    python3 \
    tcpdump \
    build-essential \
    python3-dev \
    libnetfilter-queue-dev \
    python3-pip

RUN pip3 install --upgrade pip
COPY ./requirements.txt /usr/src/app/requirements.txt
RUN pip3 install -r /usr/src/app/requirements.txt
RUN pip3 install -U git+https://github.com/kti/python-netfilterqueue

# Force matplotlib to generate the font cache
RUN python3 -c 'import matplotlib.pyplot'
ADD ./http_proxy /http_proxy


ENV QUEUE_NUM=1

ENTRYPOINT python3 -u /http_proxy/proxy.py
