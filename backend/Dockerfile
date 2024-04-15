FROM python:3.11.2-slim-buster

# Create app directory
RUN mkdir -p /usr/src/back
WORKDIR /usr/src/back

# Copy app source
COPY . /usr/src/back

# Install app dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

CMD ["python", "./server.py"]

EXPOSE 8000