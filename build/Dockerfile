FROM docker.io/frolvlad/alpine-python2
RUN apk add --no-cache make zlib-dev jpeg-dev gcc python2-dev musl-dev libxml2-dev libxslt-dev
RUN pip install wheel; pip install Pillow lxml
WORKDIR /app
EXPOSE 8080/tcp
