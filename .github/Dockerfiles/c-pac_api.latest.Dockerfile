# Copyright (C) 2023-2024  C-PAC Developers

# This file is modified from a file that is part of C-PAC.

# C-PAC is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the
# Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.

# C-PAC is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public
# License for more details.

# You should have received a copy of the GNU Lesser General Public
# License along with C-PAC. If not, see <https://www.gnu.org/licenses/>.
FROM ghcr.io/fcp-indi/c-pac/ubuntu:jammy-non-free as src
LABEL org.opencontainers.image.description "NOT INTENDED FOR USE OTHER THAN AS A DRY-RUN TESTING IMAGE \
Dry-run C-PAC latest API."
LABEL org.opencontainers.image.source https://github.com/FCP-INDI/cpac
USER root
COPY --from=fcpindi/c-pac:latest /code /code
RUN mkdir -p /home/user/c-pac_user \
    && chown -R c-pac_user:c-pac /home/user/c-pac_user \
    && chown -R c-pac_user:c-pac /code \
    && apt-get update && apt-get install -y \
       git \
       python3-pip \
       python3.10 \
       python-is-python3 \
    && rm -rf /var/lib/apt/lists/*
ENV PYTHONUSERBASE=/home/c-pac_user/.local
ENV PATH=$PATH:/home/c-pac_user/.local/bin \
    PYTHONPATH=$PYTHONPATH:$PYTHONUSERBASE/lib/python3.10/site-packages
USER c-pac_user
RUN pip install -r /code/requirements.txt && pip install --user /code
ENV FSLDIR="/FSLDIR"
ENTRYPOINT [ "/code/run.py" ]
