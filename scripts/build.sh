#!/bin/bash
# set -a # This will export all variables set below
# source .env
# set +a

# docker build \
#   --build-arg GITHUB_TOKEN=${GITHUB_TOKEN} \
#   --build-arg LINKEDIN_EMAIL=${LINKEDIN_EMAIL} \
#   --build-arg LINKEDIN_PASSWORD=${LINKEDIN_PASSWORD} \
#   --build-arg REDDIT_CLIENT_ID=${REDDIT_CLIENT_ID} \
#   --build-arg REDDIT_CLIENT_SECRET=${REDDIT_CLIENT_SECRET} \
#   --build-arg REDDIT_USERNAME=${REDDIT_USERNAME} \
#   --build-arg REDDIT_PASSWORD=${REDDIT_PASSWORD} \
#   --build-arg REDDIT_USER_AGENT=${REDDIT_USER_AGENT} \
#   --build-arg TWITTER_KEY=${TWITTER_KEY} \
#   --build-arg TWITTER_SECRET_KEY=${TWITTER_SECRET_KEY} \
#   --build-arg TWITTER_ACCESS_TOKEN=${TWITTER_ACCESS_TOKEN} \
#   --build-arg TWITTER_ACCESS_TOKEN_SECRET=${TWITTER_ACCESS_TOKEN_SECRET} \
#   --build-arg TWITTER_USERNAME=${TWITTER_USERNAME} \
#   --build-arg NOTION_API_KEY=${NOTION_API_KEY} \
#   --build-arg NOTION_DB_ID=${NOTION_DB_ID} \
#   -t notion-hoover .

  # docker build -t notion-hoover .

  #!/bin/bash

# Read and export variables from the .env file
set -a
source .env
set +a

# Start the docker build command
DOCKER_BUILD_CMD="docker build"

# Loop through each variable in .env file and append it as a build-arg
while IFS= read -r line; do
  if [[ ! $line =~ ^# ]] && [[ ! -z $line ]]; then
    key=$(echo $line | cut -d '=' -f 1)
    value=$(echo $line | cut -d '=' -f 2-)
    DOCKER_BUILD_CMD+=" --build-arg $key=$value"
  fi
done < .env

# Add the remaining options
DOCKER_BUILD_CMD+=" -t notion-hoover ."

# Execute the complete docker build command
eval $DOCKER_BUILD_CMD