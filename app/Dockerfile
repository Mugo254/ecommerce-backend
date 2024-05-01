# pull official base image
FROM python:3.9.6-alpine

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install psycopg2 dependencies
# RUN apk update \
#     && apk add postgresql-dev gcc python3-dev musl-dev g++ freetype-dev

# install psycopg2 and pillow dependencies
RUN apk update \
    && apk add postgresql-libs postgresql-dev libffi-dev \
       openldap-dev unixodbc-dev gcc musl-dev python3-dev \
       jpeg-dev zlib-dev libjpeg g++ freetype-dev cairo cairo-dev


# install dependencies
RUN apk add -u zlib-dev jpeg-dev gcc musl-dev
RUN python3 -m pip install --upgrade pip
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install --no-build-isolation pycairo
RUN pip3 install -r requirements.txt

# copy entrypoint.sh
COPY ./entrypoint.sh .
RUN sed -i 's/\r$//g' /usr/src/app/entrypoint.sh
RUN chmod +x /usr/src/app/entrypoint.sh

# copy project
COPY . .

# run entrypoint.sh
ENTRYPOINT ["/usr/src/app/entrypoint.sh"]
