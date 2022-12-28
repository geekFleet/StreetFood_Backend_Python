FROM python:3.8-slim-buster

# build variables.
ENV DEBIAN_FRONTEND noninteractive

# install Microsoft SQL Server requirements.
ENV ACCEPT_EULA=Y
RUN apt-get update -y && apt-get update \
    && apt-get install -y --no-install-recommends curl gcc g++ gnupg unixodbc-dev

# Add SQL Server ODBC Driver 17 for Ubuntu 18.04
RUN apt-get update \
    && apt-get install -y curl apt-transport-https \
    && curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql17 unixodbc-dev

COPY ./requirements.txt /requirements.txt
RUN pip install --upgrade pip
RUN pip install -r /requirements.txt

RUN apt-get -y clean

COPY ./ /app
WORKDIR /app

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]