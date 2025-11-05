FROM python:3.10-bookworm

RUN apt-get update && \
    apt-get install -y git gettext libmariadb-dev libpq-dev locales libmemcached-dev build-essential \
            git \
            sudo \
            locales \
            npm \
            --no-install-recommends && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    dpkg-reconfigure locales && \
    locale-gen C.UTF-8 && \
    /usr/sbin/update-locale LANG=C.UTF-8 && \
    mkdir /etc/pretalx && \
    mkdir /data && \
    mkdir /public

ENV LC_ALL=C.UTF-8

RUN pip install -U pip setuptools wheel
RUN pip install redis mozilla-django-oidc psycopg2-binary

# Clone pretalx from GitHub
RUN git clone https://github.com/pretalx/pretalx.git /pretalx

# Install pretalx
RUN cd /pretalx && pip install --upgrade-strategy eager -Ue ".[dev]"

COPY pretalx-oidc-plugin /pretalx-oidc
RUN cd /pretalx-oidc && pip install -e .

WORKDIR /pretalx/src

RUN groupadd -g 999 pretalxuser && \
    useradd -r -u 999 -g pretalxuser -d /pretalx -ms /bin/bash pretalxuser && \
    chown -R pretalxuser:pretalxuser /etc/pretalx /data /public /pretalx

USER pretalxuser

VOLUME ["/etc/pretalx", "/data", "/public", "/media"]

CMD ["tail", "-f", "/dev/null"]
