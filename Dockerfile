FROM potentialspecific/flask-pdftk

RUN git clone https://github.com/agudelotmateo/pdf-mark.git
WORKDIR pdf-mark

CMD gunicorn -w 2 -b 0.0.0.0:$PORT application:app
