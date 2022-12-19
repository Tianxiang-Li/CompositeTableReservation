from flask import Flask, Response, request
from flask_cors import CORS
import json
import requests
from requests_futures.sessions import FuturesSession
from typing import *

# Create logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Handler 
LOG_FILE = '/tmp/sample-app.log'
handler = logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes=1048576, backupCount=5)
handler.setLevel(logging.INFO)

# Formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Add Formatter to Handler
handler.setFormatter(formatter)

# add Handler to Logger
logger.addHandler(handler)

welcome = """
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
  <!--
    Copyright 2012 Amazon.com, Inc. or its affiliates. All Rights Reserved.

    Licensed under the Apache License, Version 2.0 (the "License"). You may not use this file except in compliance with the License. A copy of the License is located at

        http://aws.Amazon/apache2.0/

    or in the "license" file accompanying this file. This file is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
  -->
  <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
  <title>Welcome</title>
  <style>
  body {
    color: #ffffff;
    background-color: #E0E0E0;
    font-family: Arial, sans-serif;
    font-size:14px;
    -moz-transition-property: text-shadow;
    -moz-transition-duration: 4s;
    -webkit-transition-property: text-shadow;
    -webkit-transition-duration: 4s;
    text-shadow: none;
  }
  body.blurry {
    -moz-transition-property: text-shadow;
    -moz-transition-duration: 4s;
    -webkit-transition-property: text-shadow;
    -webkit-transition-duration: 4s;
    text-shadow: #fff 0px 0px 25px;
  }
  a {
    color: #0188cc;
  }
  .textColumn, .linksColumn {
    padding: 2em;
  }
  .textColumn {
    position: absolute;
    top: 0px;
    right: 50%;
    bottom: 0px;
    left: 0px;

    text-align: right;
    padding-top: 11em;
    background-color: #1BA86D;
    background-image: -moz-radial-gradient(left top, circle, #6AF9BD 0%, #00B386 60%);
    background-image: -webkit-gradient(radial, 0 0, 1, 0 0, 500, from(#6AF9BD), to(#00B386));
  }
  .textColumn p {
    width: 75%;
    float:right;
  }
  .linksColumn {
    position: absolute;
    top:0px;
    right: 0px;
    bottom: 0px;
    left: 50%;

    background-color: #E0E0E0;
  }

  h1 {
    font-size: 500%;
    font-weight: normal;
    margin-bottom: 0em;
  }
  h2 {
    font-size: 200%;
    font-weight: normal;
    margin-bottom: 0em;
  }
  ul {
    padding-left: 1em;
    margin: 0px;
  }
  li {
    margin: 1em 0em;
  }
  </style>
</head>
<body id="sample">
  <div class="textColumn">
    <h1>Tables Manipulation</h1>
    <p>This is the Home page to manipulate tables</p>
    <p>To add table:</p>
    <p>'http://restaurantreservationtable-env.eba-ursbzmrt.us-east-2.elasticbeanstalk.com/api/tables/add/indoor/[#capacity]' to add indoor table with #capacity number of seats.</p>
    <p>'http://restaurantreservationtable-env.eba-ursbzmrt.us-east-2.elasticbeanstalk.com/api/tables/add/outdoor/[#capacity]' to add outdoor table with #capacity number of seats.</p>
    <p>To delete table:</p>
    <p>'http://restaurantreservationtable-env.eba-ursbzmrt.us-east-2.elasticbeanstalk.com/api/tables/delete/indoor/[#capacity]' to delete 1 indoor table with #capacity number of seats.</p>
    <p>'http://restaurantreservationtable-env.eba-ursbzmrt.us-east-2.elasticbeanstalk.com/api/tables/delete/outdoor/[#capacity]' to delete 1 outdoor table with #capacity number of seats.</p>
    <p>This environment is launched with Elastic Beanstalk Python Platform</p>
  </div>
  
  <div class="linksColumn"> 
    <h2>Sample links:</h2>
    <ul>
    <li><a href="http://restaurantreservationtable-env.eba-ursbzmrt.us-east-2.elasticbeanstalk.com/api/health">Test Connectivity: append '/api/health'</a></li>
    <li><a href="http://restaurantreservationtable-env.eba-ursbzmrt.us-east-2.elasticbeanstalk.com/api/tables/get/indoor">Get all indoor tables: append '/api/tables/get/indoor'</a></li>
    <li><a href="http://restaurantreservationtable-env.eba-ursbzmrt.us-east-2.elasticbeanstalk.com/api/tables/get/outdoor">Get all outdoor tables: append '/api/tables/get/outdoor'</a></li>
    <li><a href="http://restaurantreservationtable-env.eba-ursbzmrt.us-east-2.elasticbeanstalk.com/api/tables/get/seats/1">Get all tables with at least 1 seat : append '/api/tables/get/seats/1'</a></li>
    <li><a href="http://restaurantreservationtable-env.eba-ursbzmrt.us-east-2.elasticbeanstalk.com/api/tables/get/all">Get all tables: append '/api/tables/get/all'</a></li>
    <li><a href="http://restaurantreservationtable-env.eba-ursbzmrt.us-east-2.elasticbeanstalk.com/api/tables/get/indoor/1">Get all indoor talbes with at least 1 seat : append '/api/tables/get/indoor/1'</a></li>
    </ul>
  </div>
</body>
</html>
"""

"""
def application(environ, start_response):
    path = environ['PATH_INFO']
    method = environ['REQUEST_METHOD']
    if method == 'POST':
        try:
            if path == '/':
                request_body_size = int(environ['CONTENT_LENGTH'])
                request_body = environ['wsgi.input'].read(request_body_size)
                logger.info("Received message: %s" % request_body)
            elif path == '/scheduled':
                logger.info("Received task %s scheduled at %s", environ['HTTP_X_AWS_SQSD_TASKNAME'],
                            environ['HTTP_X_AWS_SQSD_SCHEDULED_AT'])
        except (TypeError, ValueError):
            logger.warning('Error retrieving request body for async work.')
        response = ''
    else:
        response = welcome
        start_response("200 OK", [
            ("Content-Type", "text/html"),
            ("Content-Length", str(len(response)))
        ])
        rep = [bytes(response, 'utf-8')]
    return rep
#"""

application = Flask(__name__)


@application.route("/", methods=["GET"])
def simple_get():
    return welcome


@application.get("/api/health")
def get_health():
    t = str(datetime.now())
    msg = {
        "name": "Tables",
        "health": "Good",
        "at time": t
    }

    result = Response(json.dumps(msg), status=200, content_type="application/json")

    return result


#####################################################################################################################
#                                                 add tables                                                        #
#####################################################################################################################
@application.route("/api/tables/add/indoor/<cap>", methods=["GET", "PUT"])
def add_indoor_table(cap):
    result = Tables.add_table(cap, True)
    if result:
        rsp = Response(json.dumps(result), status=200, content_type="application.json")
    else:
        rsp = Response("NOT FOUND", status=404, content_type="text/plain")

    return rsp


@application.route("/api/tables/add/outdoor/<cap>", methods=["GET", "PUT"])
def add_outdoor_table(cap):
    result = Tables.add_table(cap, False)
    if result:
        rsp = Response(json.dumps(result), status=200, content_type="application.json")
    else:
        rsp = Response("NOT FOUND", status=404, content_type="text/plain")

    return rsp


#####################################################################################################################
#                                                 get tables                                                        #
#####################################################################################################################
@application.route("/api/tables/get/all", methods=["GET"])
def get_all():
    result = Tables.get_all()
    if result:
        rsp = Response(json.dumps(result), status=200, content_type="application.json")
    else:
        rsp = Response("NOT FOUND", status=404, content_type="text/plain")

    return rsp

@application.route("/api/tables/get/seats/<num>", methods=["GET"])
def get_by_number(num):
    result = Tables.get_by_number(num)
    if result:
        rsp = Response(json.dumps(result), status=200, content_type="application.json")
    else:
        rsp = Response("NOT FOUND", status=404, content_type="text/plain")
    return rsp


@application.route("/api/tables/get/indoor", methods=["GET"])
def get_indoor():
    result = Tables.get_indoor(True)
    if result:
        rsp = Response(json.dumps(result), status=200, content_type="application.json")
    else:
        rsp = Response("NOT FOUND", status=404, content_type="text/plain")

    return rsp


@application.route("/api/tables/get/outdoor", methods=["GET"])
def get_outdoor():
    result = Tables.get_indoor(False)
    if result:
        rsp = Response(json.dumps(result), status=200, content_type="application.json")
    else:
        rsp = Response("NOT FOUND", status=404, content_type="text/plain")

    return rsp

@application.route("/api/tables/get/indoor/<num>", methods=["GET"])
def get_num_indoor(num):
    result = Tables.get_num_indoor(num, True)
    if result:
        rsp = Response(json.dumps(result), status=200, content_type="application.json")
    else:
        rsp = Response("NOT FOUND", status=404, content_type="text/plain")

    return rsp

@application.route("/api/tables/get/outdoor/<num>", methods=["GET"])
def get_num_outdoor(num):
    result = Tables.get_num_indoor(num, False)
    if result:
        rsp = Response(json.dumps(result), status=200, content_type="application.json")
    else:
        rsp = Response("NOT FOUND", status=404, content_type="text/plain")

    return rsp

#####################################################################################################################
#                                                delete tables                                                      #
#####################################################################################################################
@application.route("/api/tables/delete/outdoor/<cap>", methods=["GET", "PUT"])
def delete_outdoor_table(cap):
    result = Tables.delete_last_table(cap, False)
    if result:
        rsp = Response(json.dumps(result), status=200, content_type="application.json")
    else:
        rsp = Response("NOT FOUND", status=404, content_type="text/plain")

    return rsp


@application.route("/api/tables/delete/indoor/<cap>", methods=["GET", "PUT"])
def delete_indoor_table(cap):
    result = Tables.delete_last_table(cap, True)
    if result:
        rsp = Response(json.dumps(result), status=200, content_type="application.json")
    else:
        rsp = Response("NOT FOUND", status=404, content_type="text/plain")

    return rsp


if __name__ == "__main__":
    application.run(host="0.0.0.0", port=5000)
