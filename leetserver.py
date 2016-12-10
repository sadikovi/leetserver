#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#
# Copyright 2016 sadikovi
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import argparse
import json
import random
import sys
import time
import urllib2
# Import the email modules
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Currently Python 2.7 is supported
PYTHON_VERSION_MAJOR = 2
PYTHON_VERSION_MINOR = 7
if sys.version_info.major != PYTHON_VERSION_MAJOR or sys.version_info.minor != PYTHON_VERSION_MINOR:
    print "[ERROR] Only Python %s.%s is supported" % (PYTHON_VERSION_MAJOR, PYTHON_VERSION_MINOR)
    sys.exit(1)

# Run only on OS X and Linux
if not (sys.platform.startswith("darwin") or sys.platform.startswith("linux")):
    print "[ERROR] Only OS X and Linux are supported"
    sys.exit(1)

# Application version
VERSION = "0.0.1"
# Leetcode READ url
LEETCODE_REST_URL = "https://leetcode.com/api/problems/algorithms"

# Container for the Leetcode question
class Question(object):
    def __init__(self, question):
        self.title = question["stat"]["question__title"]
        self.id = question["stat"]["question_id"]
        self.slug = question["stat"]["question__title_slug"]
        self.level = question["difficulty"]["level"]
        self.total_submissions = question["stat"]["total_submitted"]

    # Convert difficulty level into text
    def difficulty(self):
        if self.level == 1:
            return "Easy"
        elif self.level == 2:
            return "Medium"
        elif self.level == 3:
            return "Hard"
        else:
            return "Unknown"

    # Get URL for the question
    def get_url(self):
        return "https://leetcode.com/problems/%s" % self.slug

    def get_subject_title(self):
        return "We challenge you to solve %s" % self.title

    def as_plain_text(self):
        return ("== Leetcode Question ==\n" +
                "Title = %s\n" +
                "ID = %s\n" +
                "URL = %s\n" +
                "Difficulty = %s\n" +
                "Total submissions = %s\n") % (self.title, self.id, self.get_url(),
                    self.difficulty(), self.total_submissions)

    def as_html(self):
        return """
        <html>
          <head></head>
          <body>
            <h2>Hello!</h2>
            <p>
              <div>
                Improve your skills with this randomly selected challenge:
                <ul>
                  <li>%s [%s]</li>
                  <li>Difficulty: %s</li>
                  <li>Total submissions: %s</li>
                </ul>
              </div>
              <div>
                <a href="%s">Solve challenge</a>
              </div>
            </p>
          </body>
        </html>
        """ % (self.title, self.id, self.difficulty(), self.total_submissions, self.get_url())

# Parse input arguments
def create_cli_parser():
    parser = argparse.ArgumentParser(description="Leetcode random server")
    parser.add_argument("--smtp-host", required=True, help="AWS SMTP host")
    parser.add_argument("--smtp-port", required=True, type=int, help="AWS SMTP port")
    parser.add_argument("--from", required=True, help="sender email address, must be verified")
    parser.add_argument("--to", required=True, help="receiver email address, must be verified")
    parser.add_argument("--username", required=True, help="AWS SMTP username")
    parser.add_argument("--password", required=True, help="AWS SMTP password")
    parser.add_argument("--interval", required=True, type=int, help="interval to fetch, in seconds")
    return parser

# Select random question from list of questions
def random_question(questions):
    if not questions:
        return None
    return random.choice(questions)

# Parse raw payload into list of question dictionaries
def parse_leetcode_questions(payload):
    questions = []
    if not payload:
        return questions
    # flatten pair chunks, e.g. 0-99, 100-1999, etc.
    return [chunk for chunk in payload["stat_status_pairs"]]

def fetch_leetcode_questions():
    payload = None
    try:
        # perform request with timeout of 1 minute
        obj = urllib2.urlopen(LEETCODE_REST_URL, timeout=60)
        payload = json.loads(obj.read())
    except StandardError as err:
        print "Error occured when fetching questions, err=%s" % err
    return parse_leetcode_questions(payload)

# Refetch questions in case of failure
def safe_fetch_leetcode_questions():
    # refresh interval in seconds
    refresh_interval = 5
    number_of_attempts = 10
    questions = None
    while not questions and number_of_attempts > 0:
        questions = fetch_leetcode_questions()
        if not questions:
            print "Failed to fetch questions, retrying in %s seconds (left %s attempts)" % \
                (refresh_interval, number_of_attempts)
        number_of_attempts -= 1
        time.sleep(refresh_interval)
    if number_of_attempts <= 0:
        print "Number of attempts is exhausted"
    return questions

def send_email(smtp_host, smtp_port, from_addr, to_addr, username, password, subject, html_body):
    msg = MIMEMultipart("alternative")
    body = MIMEText(html_body, "html")
    msg.attach(body)
    msg["Subject"] = subject
    msg["From"] = from_addr
    msg["To"] = to_addr
    try:
        s = smtplib.SMTP(smtp_host, smtp_port)
        out = s.starttls()
        print "Starting TLS, %s" % (out,)
        out = s.login(username, password)
        print "Login, %s" % (out,)
        out = s.sendmail(from_addr, [to_addr], msg.as_string())
        print "Send email, %s" % (out,)
        s.quit()
    except Exception as err:
        print "Failed to send email, err=%s" % err
        return False
    else:
        return True

def main():
    parser = create_cli_parser()
    namespace = parser.parse_args()
    args = vars(namespace)
    print "Start server [version %s]..." % VERSION
    print "Using settings %s" % args
    interval = args["interval"]
    if not isinstance(interval, int) and interval <= 0:
        print "Invalid interval %s" % interval
        return None
    # All available questions
    questions = safe_fetch_leetcode_questions()
    print "Fetched questions %s" % len(questions)
    # Loop to sleep for interval, select random question and send it
    while True:
        time.sleep(interval)
        print "\n---\n"
        # only select non-paid question
        question = Question(random_question([x for x in questions if not x["paid_only"]]))
        print question.as_plain_text()
        status = send_email(args["smtp_host"], args["smtp_port"], args["from"], args["to"],
            args["username"], args["password"], question.get_subject_title(), question.as_html())
        if status:
            print "Email sent successfully"
        else:
            print "Failed to send email"

if __name__ == "__main__":
    main()
