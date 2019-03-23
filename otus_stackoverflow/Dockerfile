FROM centos:latest

ARG DEFAULT_REQUIREMENTS
ENV REQUIREMENTS $DEFAULT_REQUIREMENTS

RUN yum -y update; yum clean all
RUN yum -y install epel-release gcc git curl make zlib-devel bzip2 bzip2-devel readline-devel sqlite sqlite-devel openssl openssl-devel patch

WORKDIR /root/otus_stackoverflow

RUN echo ${REQUIREMENTS}, ${pwd}

ENV HOME  /root
ENV APP_ROOT /root/otus_stackoverflow
ENV PYENV_ROOT $HOME/.pyenv
ENV PATH $PYENV_ROOT/shims:$PYENV_ROOT/bin:$PATH

RUN git clone git://github.com/yyuu/pyenv.git $HOME/.pyenv

RUN pyenv install 3.5.2
RUN pyenv global 3.5.2
RUN pyenv rehash

ADD ./requirements $APP_ROOT/requirements
RUN pip install -r ./requirements/$REQUIREMENTS
ADD . $APP_ROOT
