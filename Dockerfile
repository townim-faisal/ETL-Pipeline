FROM apache/airflow:2.3.1

USER root

RUN apt-get update \
  && apt-get install -y --no-install-recommends \
         vim \
  && apt-get autoremove -yqq --purge \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*


COPY .env /usr/src
COPY sql/* /usr/src
COPY .env /opt/airflow

USER airflow

COPY requirements.txt /tmp/requirements.txt
RUN python3 -m pip install -r /tmp/requirements.txt



# WORKDIR /usr/src
# RUN python3 source_db_table_with_dummy_data.py
# RUN python3 target_db_table_with_functions.py.py

# COPY airflow/plugins /opt/airflow/plugins

