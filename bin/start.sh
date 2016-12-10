#!/bin/bash

bin="`dirname "$0"`"
ROOT_DIR="`cd "$bin/../"; pwd`"

# Find python executable
WHICH_PYTHON=$(which python)
if [[ -z "$WHICH_PYTHON" ]]; then
  echo "Python is not found, please install it"
  exit 1
fi

# interval of sending an email, defaults to "every day"
AWS_SECONDS_INTERVAL=${AWS_SECONDS_INTERVAL:-"86400"}

$WHICH_PYTHON $ROOT_DIR/leetserver.py \
  --smtp-host=$AWS_SMTP_HOST \
  --smtp-port=$AWS_SMTP_PORT \
  --from=$AWS_FROM_EMAIL_ADDRESS \
  --to=$AWS_TO_EMAIL_ADDRESS \
  --username=$AWS_SMTP_USERNAME \
  --password=$AWS_SMTP_PASSWORD \
  --interval=$AWS_SECONDS_INTERVAL
