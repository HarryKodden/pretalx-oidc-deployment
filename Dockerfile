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
RUN pip install redis mozilla-django-oidc

# Clone pretalx from GitHub
RUN git clone https://github.com/pretalx/pretalx.git /pretalx

# Install pretalx
RUN cd /pretalx && pip install --upgrade-strategy eager -Ue ".[dev]"

# Copy patch script and apply it to settings.py
# This patches the plugin loading to support custom AppConfig classes (required for Django 3.2+)
COPY patch_settings.py /tmp/patch_settings.py
RUN python3 /tmp/patch_settings.py && rm /tmp/patch_settings.py

# Patch settings.py to add CSRF_TRUSTED_ORIGINS from site URL
COPY patch_csrf_trusted_origins.py /tmp/patch_csrf_trusted_origins.py
RUN python3 /tmp/patch_csrf_trusted_origins.py && rm /tmp/patch_csrf_trusted_origins.py

# Patch auth.html to hide password authentication when OIDC is the only backend
# This provides a cleaner OIDC-only login experience
COPY patch_hide_password_auth.py /tmp/patch_hide_password_auth.py
RUN python3 /tmp/patch_hide_password_auth.py && rm /tmp/patch_hide_password_auth.py

# Patch user_profile.html to hide password change section when OIDC is enabled
COPY patch_hide_password_profile.py /tmp/patch_hide_password_profile.py
RUN python3 /tmp/patch_hide_password_profile.py && rm /tmp/patch_hide_password_profile.py

# Patch organizer user settings page to hide password change section when OIDC is enabled
COPY patch_hide_password_orga.py /tmp/patch_hide_password_orga.py
RUN python3 /tmp/patch_hide_password_orga.py && rm /tmp/patch_hide_password_orga.py

# Patch settings.py to add SSL proxy awareness for reverse proxy deployments
COPY patch_ssl_proxy.py /tmp/patch_ssl_proxy.py
RUN python3 /tmp/patch_ssl_proxy.py && rm /tmp/patch_ssl_proxy.py

# Copy and install OIDC plugin
COPY pretalx-oidc-plugin /pretalx-oidc
RUN cd /pretalx-oidc && pip install -e .

WORKDIR /pretalx/src

RUN groupadd -g 999 pretalxuser && \
    useradd -r -u 999 -g pretalxuser -d /pretalx -ms /bin/bash pretalxuser && \
    chown -R pretalxuser:pretalxuser /etc/pretalx /data /public /pretalx

USER pretalxuser

VOLUME ["/etc/pretalx", "/data", "/public"]

CMD ["tail", "-f", "/dev/null"]
