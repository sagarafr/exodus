FROM registry.ovh.net/official/python:3.5

ENTRYPOINT ["./docker-entrypoint.sh"]
CMD ["api"]

EXPOSE 5000

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app
ADD requirements/* /usr/src/app/requirements/

RUN pip install --no-cache-dir --extra-index-url=https://pypi.ovh.net -r requirements/prod.txt
COPY . /usr/src/app

RUN make --directory=doc html && \
    mkdir foo/doc/doc_files && \
    mv doc/build/html/* foo/doc/doc_files
