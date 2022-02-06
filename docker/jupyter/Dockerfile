FROM jupyter/scipy-notebook

USER root

RUN conda install --yes --name root psycopg2

RUN pip install plotly=5.5.0 \
                chart-studio=1.1.0 \
                sqlalchemy \
                dash=2.1.0 \
                opencv-python=4.5.5.62 

USER jovyan