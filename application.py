from flask import Flask, Response, request
from flask_cors import CORS
import json
import requests
import threading
from threading import Thread
from datetime import datetime, date
from werkzeug.exceptions import HTTPException


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
    <h1>Table Reservation</h1>
    <p>This is the Composite Service for Table Reservation</p>
    <p>To add reservation:</p>
    <p>'http://compositetablereservation-env.eba-fxm55zhy.us-east-2.elasticbeanstalk.com/api/table_reserve/indoor/<email>/[#num]' to reserve indoor table for #num number of guests.</p>
    <p>'http://compositetablereservation-env.eba-fxm55zhy.us-east-2.elasticbeanstalk.com/api/table_reserve/outdoor/<email>/[#num]' to reserve outdoor table for #num number of guests.</p>
    <p>This environment is launched with Elastic Beanstalk Python Platform</p>
  </div>
  
  <div class="linksColumn"> 
    <h2>Get Informations:</h2>
    <ul>
    <li><a href="http://compositetablereservation-env.eba-fxm55zhy.us-east-2.elasticbeanstalk.com/api/health">Test Connectivity: append '/api/health'</a></li>
    <li><a href="http://compositetablereservation-env.eba-fxm55zhy.us-east-2.elasticbeanstalk.com/api/table_reserve/get/5">Get the number of tables indoor and outdoor availble for 5 guests</a></li>
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
CORS(application)

REGISTRATION = {
    'microservice': 'Registration microservice',
    'api': 'http://registration-env.eba-xi2mxgp6.us-east-1.elasticbeanstalk.com/'
}

TABLES = {
    'microservice': 'Tables Management microservice',
    'api': 'http://restaurantreservationtable-env.eba-ursbzmrt.us-east-2.elasticbeanstalk.com/api/tables/get'
}

RESERVATION = {
    'microservice': 'Reservation microservice',
    'api': 'http://ec2-54-235-224-149.compute-1.amazonaws.com:5011/api/reservations/'
}

def reserve_table(email, indoor, num):
    # table id
    tables = requests.get(TABLES['api'] + '/{}/{}'.format(indoor, num))
    if tables.status_code != 200:
        table_error = 'tables with {} seats {}'.format(num, tables.text)
        print(table_error)
        return Response(table_error, status=tables.status_code, content_type="application.json")
    tables_data = tables.json()
    table_id_ls = [t['table_id'] for t in tables_data]
    print(table_id_ls)

    # reserved tables
    reserves = requests.get(RESERVATION['api'])
    if reserves.status_code != 200:
        print(reserves.text)
        reserved_tables = set()
    else:
        reserves_data = reserves.json()
        reserved_tables = set(r['table_id'] for r in reserves_data)
        print(reserved_tables)

    table_id = None
    for tid in table_id_ls:
        if tid not in reserved_tables:
            table_id = tid
            break
    print(table_id)
    if table_id is None:
        return Response("No available indoor seats", status=404, content_type="application.json")

    # user email
    registered_email = requests.get(REGISTRATION['api'] + "/api/check-registration/")
    if registered_email.status_code != 200:
        email_error = "Error finding registrations!"
        print(email_error)
        return Response(email_error, status=email.status_code, content_type="application.json")
    email_data = registered_email.json()
    user_email = set(e['email'] for e in email_data)
    print(user_email)
    if email not in user_email:
        return Response("Your email is not registered yet, please register first", status=404, content_type="text/plain")
    # input user email

    # put to reservation schema
    reserve_api = RESERVATION['api'] + '{}/{}'.format(email, table_id)
    print(reserve_api)
    resp = requests.put(reserve_api)
    if resp.status_code == 200:
        resp_msg = resp.text
        resp_msg_ls = resp_msg.split()
        resp_starter = resp_msg_ls[0]
        if resp_starter == "Success":
            resp_text = "Successfully reserved {} table of {} guests for {}".format(indoor, num, user_email)
        else:
            resp_text = "Reserving {} table of {} guests for {}. Attention ".format(indoor, num, user_email)
            resp_text += ' '.join(resp_msg_ls[:-5])

        res = Response(resp_text, status=200, content_type="application.json")
    else:
        resp_error = "Could not reserve table of {} guests for {}: ".format(num, user_email) + resp.text
        print(resp_error)
        res = Response(resp_error, status=resp.status_code, content_type="application.json")
    return res


@application.route("/", methods=["GET"])
def simple_get():
    return welcome


@application.get("/api/health")
def get_health():
    t = str(datetime.now())
    msg = {
        "name": "Table Reservation",
        "health": "Good",
        "at time": t
    }

    result = Response(json.dumps(msg), status=200, content_type="application/json")

    return result


#####################################################################################################################
#                                        get available tables                                                       #
#####################################################################################################################
@application.route("/api/table_reserve/get/<num>", methods=["GET"])
def get_num_table(num):
    # reserved tables
    reserves = requests.get(RESERVATION['api'])
    if reserves.status_code == 200:
        reserves_data = reserves.json()
        reserved_tables = set(r['table_id'] for r in reserves_data)
    else:
        reserved_tables = set()
    print(reserved_tables)

    # table id
    tables = requests.get(TABLES['api'] + '/seats/{}'.format(num))
    if not tables:
        return Response("No available seats for {} guests".format(num), status=404, content_type="application.json")
    tables_data = tables.json()
    indoor = 0
    outdoor = 0
    for t in tables_data:
        if t['table_id'] not in reserved_tables:
            if t['indoor'] == 1:
                indoor += 1
            else:
                outdoor += 1

    msg = {
        'indoor': indoor,
        'outdoor': outdoor
    }
    return Response(json.dumps(msg), status=200, content_type="application/json")


#####################################################################################################################
#                                              reserve tables                                                       #
#####################################################################################################################
@application.route("/api/table_reserve/indoor/<email>/<num>", methods=["GET", "PUT"])
def reserve_indoor_table(email, num):
    return reserve_table(email, 'indoor', num)


@application.route("/api/table_reserve/outdoor/<email>/<num>", methods=['GET','PUT'])
def reserve_outdoor_table(email, num):
    return reserve_table(email, 'outdoor', num)


if __name__ == "__main__":
    application.run(host="0.0.0.0", port=8000)
