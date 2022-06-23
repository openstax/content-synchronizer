FROM python:3.7-slim-bullseye as base

# No interactive frontend during docker build
ENV DEBIAN_FRONTEND=noninteractive \
    DEBCONF_NONINTERACTIVE_SEEN=true

RUN apt-get update -qq \
 && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    git \
    gnupg2 \
    software-properties-common \
    sudo \
    tzdata \
    unzip \
    wget \
    build-essential \
    libxml2-dev \
    libxslt-dev \
    zlib1g-dev \
    python-dev \
    xmlstarlet \
    jq \
    ssh \
    openssh-client \
 && apt-get autoremove -y

#===================
# Timezone settings
# Possible alternative: https://github.com/docker/docker/issues/3359#issuecomment-32150214
#===================
ENV TZ "UTC"
RUN echo "${TZ}" > /etc/timezone \
  && dpkg-reconfigure --frontend noninteractive tzdata

#========================================
# Add normal user with passwordless sudo
#========================================
RUN useradd ceuser \
         --shell /bin/bash  \
         --create-home \
  && usermod -a -G sudo ceuser \
  && echo 'ALL ALL = (ALL) NOPASSWD: ALL' >> /etc/sudoers \
  && echo 'ceuser:secret' | chpasswd

#=============================
# Install Python Dependencies
#=============================
RUN python -m pip install --upgrade wheel pip setuptools
RUN CFLAGS="-O0" python -m pip install nebuchadnezzar lxml
