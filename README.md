# leetserver
Select random Leetcode question and send email using AWS (or any other SMTP server with TLS support)

## Install
Clone repository and build docker image on either local machine or EC2 instance, this creates
Ubuntu 14.04 with Python installed.
```
git clone https://github.com/sadikovi/leetserver.git
cd leetserver
docker build --tag leetserver .
```

Run container with supplied environment variables:
```
docker run -it -e AWS_SMTP_HOST=host -e AWS_SMTP_PORT=port \
  -e AWS_FROM_EMAIL_ADDRESS=email -e AWS_TO_EMAIL_ADDRESS=email \
  -e AWS_SMTP_USERNAME=username -e AWS_SMTP_PASSWORD=password \
  -e AWS_SECONDS_INTERVAL=interval leetserver
```

Environment variables are explained below:
- `AWS_SMTP_HOST` SMTP server host name
- `AWS_SMTP_PORT` SMTP server port, e.g. 25 or 587
- `AWS_FROM_EMAIL_ADDRESS` sender's email address, must be verified if using AWS SES
- `AWS_TO_EMAIL_ADDRESS` recipient's email address, must be verified if using AWS SES
- `AWS_SMTP_USERNAME` username for SMTP
- `AWS_SMTP_PASSWORD` password for SMTP
- `AWS_SECONDS_INTERVAL` interval in seconds when to send email, defaults to 1 day. Recommended to
keep it around 2-5 days
