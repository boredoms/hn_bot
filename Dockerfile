# use the astral alpine image which comes with uv preinstalled
FROM ghcr.io/astral-sh/uv:alpine

# copy the files into the container
COPY . /app

ENV UV_COMPILE_BYTECODE=1

# set the working directory
WORKDIR /app
RUN mkdir data &&\
  uv sync --frozen 

VOLUME "/data" "/config"

CMD [ "uv", "run", "bot" ]
