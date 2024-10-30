FROM python:3.10

RUN mkdir /python_advanced_diploma

WORKDIR /python_advanced_diploma

COPY requirements_prod.txt .

RUN pip install -r requirements_prod.txt

COPY python_advanced_diploma .

RUN chmod a+x docker/*.sh
