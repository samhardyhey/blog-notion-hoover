# Use an official Python runtime as a parent image
FROM python:3.8-slim-buster

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages
RUN apt-get update \
    && apt-get install -y chromium \
    xsel \
    xclip \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install -r requirements.txt

# and install playwright browsers
RUN playwright install

# as well as an x-server to render browser head
RUN apt-get update -y && apt-get install -y xvfb

# Set build arguments
ARG GITHUB_TOKEN
ARG LINKEDIN_EMAIL
ARG LINKEDIN_PASSWORD
ARG REDDIT_CLIENT_ID
ARG REDDIT_CLIENT_SECRET
ARG REDDIT_USERNAME
ARG REDDIT_PASSWORD
ARG REDDIT_USER_AGENT
ARG TWITTER_KEY
ARG TWITTER_SECRET_KEY
ARG TWITTER_ACCESS_TOKEN
ARG TWITTER_ACCESS_TOKEN_SECRET
ARG TWITTER_USERNAME
ARG NOTION_API_KEY
ARG NOTION_DB_ID

# Set environment variables
ENV GITHUB_TOKEN=$GITHUB_TOKEN
ENV LINKEDIN_EMAIL=$LINKEDIN_EMAIL
ENV LINKEDIN_PASSWORD=$LINKEDIN_PASSWORD
ENV REDDIT_CLIENT_ID=$REDDIT_CLIENT_ID
ENV REDDIT_CLIENT_SECRET=$REDDIT_CLIENT_SECRET
ENV REDDIT_USERNAME=$REDDIT_USERNAME
ENV REDDIT_PASSWORD=$REDDIT_PASSWORD
ENV REDDIT_USER_AGENT=$REDDIT_USER_AGENT
ENV TWITTER_KEY=$TWITTER_KEY
ENV TWITTER_SECRET_KEY=$TWITTER_SECRET_KEY
ENV TWITTER_ACCESS_TOKEN=$TWITTER_ACCESS_TOKEN
ENV TWITTER_ACCESS_TOKEN_SECRET=$TWITTER_ACCESS_TOKEN_SECRET
ENV TWITTER_USERNAME=$TWITTER_USERNAME
ENV NOTION_API_KEY=$NOTION_API_KEY
ENV NOTION_DB_ID=$NOTION_DB_ID

# Run the script
# CMD ["python", "ingest/linkedin.py"]

# # X11 server alternative?
# # Install X11 server and related libraries
# RUN apt-get update && apt-get install -y x11-xserver-utils xauth x11-apps

# # Add a user to run the X11 server
# RUN groupadd -r user && useradd -r -g user -G audio,video user \
#     && mkdir -p /home/user \
#     && chown -R user:user /home/user

# # Run the X11 server
# CMD ["startx"]