FROM ubuntu:20.04

# libxcursor1 - OSError: libXcursor.so.1: cannot open shared object file: No such file or directory
# libxft2 - OSError: libXft.so.2: cannot open shared object file: No such file or directory
# libxinerama1 - OSError: libXinerama.so.1: cannot open shared object file: No such file or directory
# libglu1 - OSError: libGLU.so.1: cannot open shared object file: No such file or directory
# libxrender1 - OSError: libXrender.so.1: cannot open shared object file: No such file or directory
# libpq-dev - pip3 postgres install error
RUN apt-get update && apt-get install -y \
    git \
    libglu1 \
    libpq-dev \
    libxcursor1 \ 
    libxft2 \
    libxinerama1 \
    libxrender1 \
    python3-pip \
    python-is-python3 \
    && rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/romanzes637/gmsh_scripts.git /opt/gmsh/
WORKDIR /opt/gmsh
RUN pip3 install --no-cache-dir -r requirements_ml.txt 
RUN pip3 install --no-cache-dir -r requirements_postgres.txt 

WORKDIR /opt/gmsh/input/tenex
CMD ["python3", "../../ml.py", "opt.json"]