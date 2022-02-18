# ================
# FENIA Dockerfile
# ================
# Best practives for writing Dockerfiles
# https://docs.docker.com/develop/develop-images/dockerfile_best-practices/
# About multi-stage builds
# https://docs.docker.com/develop/develop-images/multistage-build/
# -----
# BUILD
# -----
# https://docs.docker.com/engine/reference/commandline/build/
# TEMPLATE
# docker build [OPTIONS] PATH | URL | -
# SIMPLE
# docker build -t fenia .
# NO CACHE (don't reuse previous build steps, i.e. starts build from beginnig)
# docker build --no-cache -t fenia . 
# WITH ARGS
# docker build --build-arg PETSC_TAG=v3.9 --build-arg SLEPC_TAG=v3.9.2 -t fenia . 
# ---
# RUN
# ---
# https://docs.docker.com/engine/reference/run/
# TEMPLATE
# docker run [OPTIONS] IMAGE[:TAG|@DIGEST] [COMMAND] [ARG...]
# INTERACTIVE
# docker run --rm -it fenia /bin/bash
# RUN IN CURRENT DIRECTORY
# docker run --rm -v $(pwd):/work -w /work fenia linLMTerm

# --------------
# 0. Global ARGs
# --------------
# They are passed through all stages (FROMs) and could be set in the docker build command 
ARG PETSC_TAG=v3.9  # https://bitbucket.org/petsc/petsc/downloads/?tab=tags
ARG PETSC_ARCH=arch-linux2-c-opt
ARG SLEPC_TAG=v3.9.2  # https://bitbucket.org/slepc/slepc/downloads/?tab=tags
ARG ROOT_DIR=/opt
ARG PETSC_DIR=$ROOT_DIR/petsc
ARG SLEPC_DIR=$ROOT_DIR/slepc
ARG FENIA_DIR=$ROOT_DIR/OpenFEM-0.0.x
ARG TZ=Europe/Moscow

# --------------
# 1. BUILD STAGE
# --------------
FROM ubuntu:20.04 AS builder
ARG ROOT_DIR  # Set local ARG from global ARG
ENV ROOT_DIR = $ROOT_DIR  # Set ENV from local ARG

# APT-GET
# git, gcc, g++, make, cmake for PETSC, SLEPC, FENIA
# libz-dev, valgrind for FENIA
# python2 for PETSC, SLEPC
# DEBIAN_FRONTEND and TZ for cmake
ARG DEBIAN_FRONTEND=noninteractive  # Use temporary ARG instead of persistent ENV!
ARG TZ
ENV TZ=$TZ
RUN apt-get update && apt-get install -y \
    cmake \
    g++ \
    gcc \
    git \
    libz-dev \
    make \
    python2 \
    valgrind \
    && rm -rf /var/lib/apt/lists/*

# PETSC
ARG PETSC_TAG
ARG PETSC_DIR
ENV PETSC_DIR=$PETSC_DIR
ARG PETSC_ARCH
ENV PETSC_ARCH=$PETSC_ARCH
RUN git clone --depth 1 --branch $PETSC_TAG https://bitbucket.org/petsc/petsc $PETSC_DIR
WORKDIR $PETSC_DIR
RUN python2 ./configure --with-cc=gcc --with-cxx=g++ --with-fc=0 --with-debugging=0 COPTFLAGS=-O3 -march=native -mtune=native CXXOPTFLAGS=-O3 -march=native -mtune=native --download-mpich --download-f2cblaslapack --download-superlu_dist \
    && make all \
    && make check
WORKDIR $ROOT_DIR
ENV LD_LIBRARY_PATH=$PETSC_DIR/$PETSC_ARCH/lib:$LD_LIBRARY_PATH

# SLEPC
ARG SLEPC_TAG
ARG SLEPC_DIR
ENV SLEPC_DIR=$SLEPC_DIR
RUN git clone --depth 1 --branch $SLEPC_TAG https://bitbucket.org/slepc/slepc $SLEPC_DIR
WORKDIR $SLEPC_DIR
RUN python2 ./configure \
    && make all \
    && make check
WORKDIR $ROOT_DIR
ENV LD_LIBRARY_PATH=$SLEPC_DIR/$PETSC_ARCH/lib:$LD_LIBRARY_PATH

# FENIA
ARG FENIA_DIR
ENV FENIA_DIR=$FENIA_DIR
# Git requires ssh key, which is insecure and hard to implement
# Clone repository manually with get_fenia.sh script
# RUN git clone git@svn100.ibrae:/home/git/opf/OpenFEM-0.0.x.git $FENIA_DIR
COPY OpenFEM-0.0.x $FENIA_DIR
WORKDIR $FENIA_DIR/build
RUN cmake .. \
    && make
WORKDIR $ROOT_DIR
ENV PATH=$FENIA_DIR/build/bin:$PATH
ENV LD_LIBRARY_PATH=$FENIA_DIR/build/lib:$LD_LIBRARY_PATH

# --------------
# 2. BUILT STAGE
# --------------




