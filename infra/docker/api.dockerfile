FROM public.ecr.aws/lambda/python:3.8

# Install libraries
RUN yum install -y libpng \
    libjpeg \
    openssl \
    icu \
    libX11 \
    libXext \
    libXrender \
    xorg-x11-fonts-Type1 \
    xorg-x11-fonts-75dpi \
    wget && \
    wget https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6-1/wkhtmltox-0.12.6-1.amazonlinux2.x86_64.rpm && \
    rpm -Uvh wkhtmltox-0.12.6-1.amazonlinux2.x86_64.rpm && \
    rm wkhtmltox-0.12.6-1.amazonlinux2.x86_64.rpm

# Install Poetry
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | POETRY_HOME=/opt/poetry python && \
    cd /usr/local/bin && \
    ln -s /opt/poetry/bin/poetry && \
    poetry config virtualenvs.create false

# Copy poetry.lock* in case it doesn't exist in the repo
COPY ./pyproject.toml ./poetry.lock* ${LAMBDA_TASK_ROOT}/

# Allow installing dev dependencies to run tests
ARG INSTALL_DEV=false
RUN bash -c "if [ $INSTALL_DEV == 'true' ] ; then poetry install --no-root ; else poetry install --no-root --no-dev ; fi"

ADD ./app ${LAMBDA_TASK_ROOT}/app

ENV PYTHONPATH ${LAMBDA_TASK_ROOT}/app
CMD ["app.adapter.into.fastapi.lambda.handler"]
