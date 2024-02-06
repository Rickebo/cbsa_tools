# The container image is based on the existing Python:3.11 image:
FROM python:3.11

# Use /app as the workdir, i.e. where the application files are, and where the
# application runs.
WORKDIR /app

# Copy and install the requirements. Doing this before copying and running the script
# files is beneficial since if the script files change without requirements
# changing, building a new image wont have to install the requirements again.
# Instead, a new build can restart from after the requirements install stage of the
# build.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Finally copy the script files.
COPY . .

# The entrypoint is py -u. Then, the arguments passed to the command "py -u" are
# specified by the user when ruinning the container. For example, running the
# container like "docker run <container name> view.py" passes view.py to py -u,
# resulting in "py -u view.py" being run.
ENTRYPOINT ["py", "-u"]