FROM ubuntu:xenial
# Requirements for the python test environment
RUN apt-get --yes update \
 && apt-get install --yes --no-install-recommends \
    build-essential \
    libpq-dev \
    python3-dev \
    python3-setuptools \
 && rm -rf /var/lib/apt/lists/*
# Install newest pip
RUN apt-get --yes update \
 && apt-get install --yes --no-install-recommends \
    python3-pip \
 && rm -rf /var/lib/apt/lists/* \
 && pip3 install --upgrade 'pip<21.0' \
 && apt-get purge --yes python3-pip
