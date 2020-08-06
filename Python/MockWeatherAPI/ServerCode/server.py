#!flask/bin/python
from flask import Flask, Blueprint, flash, redirect, request, url_for, jsonify
from flask import request, abort
from flask_api import status
from functools import wraps
from flask import render_template
import simplejson as json
from decimal import Decimal
import mysql.connector

CONST_MYSQL_HOST = "localhost"
CONST_MYSQL_USER = "root"
CONST_MYSQL_PASS = "root"
CONST_MYSQL_DB = "mock_weather"

CONST_AUTH_PASS = "cervellotalentacq"


def connectMySql():
    mydb = mysql.connector.connect(
        host=CONST_MYSQL_HOST, user=CONST_MYSQL_USER, password=CONST_MYSQL_PASS, database=CONST_MYSQL_DB)
    return mydb


app = Flask(__name__)


@app.errorhandler(404)
def page_not_found(e):
    return jsonify({}), status.HTTP_404_NOT_FOUND


def validate_key(called_function):
    @wraps(called_function)
    def key_validator(*args, **kwargs):
        try:
            if request.args.get('api-key'):
                mydb = connectMySql()
                mycursor = mydb.cursor(dictionary=True)
                mycursor.execute(
                    "SELECT COUNT(*) AS COUNT FROM MOCK_WEATHER.AUTH WHERE AUTH_KEY = '{}'".format(request.args.get('api-key')))
                result = mycursor.fetchall()
                if result[0]['COUNT'] == 1:
                    return called_function(*args, **kwargs)
                else:
                    return {'status': 'UNAUTHORIZED'}, status.HTTP_401_UNAUTHORIZED
            else:
                return {'status': 'UNAUTHORIZED'}, status.HTTP_401_UNAUTHORIZED
        except Exception as e:
            response = {}
            response["status"] = "FAILED"
            response["error"] = str(
                e) + " : ERROR : While authenticating the API Key"
            return jsonify(response), status.HTTP_500_INTERNAL_SERVER_ERROR
    return key_validator


@app.route('/api/country', methods=['GET'])
@validate_key
def get_country():
    try:
        response = {}
        mydb = connectMySql()
        mycursor = mydb.cursor(dictionary=True)
        mycursor.execute(
            """SELECT DISTINCT COUNTRY FROM MOCK_WEATHER.VW_DIM_LOCATION;""")
        results = mycursor.fetchall()
        # print(results)
        result = map(lambda x: x['COUNTRY'], results)
        result = list(result)
        response["data"] = result
        print(response)
        return jsonify(response), status.HTTP_200_OK
    except Exception as e:
        response = {}
        response["status"] = "FAILED"
        response["error"] = str(e)
        return jsonify(response), status.HTTP_500_INTERNAL_SERVER_ERROR


@app.route('/api/cities', methods=['GET'])
@validate_key
def get_cities():
    try:
        response = {}
        mydb = connectMySql()
        mycursor = mydb.cursor(dictionary=True)
        if request.args.get('country'):
            mycursor.execute(
                """SELECT DISTINCT CITY_NAME FROM MOCK_WEATHER.VW_DIM_LOCATION WHERE COUNTRY = '{}';""".format(request.args.get('country')))
        else:
            mycursor.execute(
                """SELECT DISTINCT CITY_NAME FROM MOCK_WEATHER.VW_DIM_LOCATION;""")
        results = mycursor.fetchall()
        # print(results)
        result = map(lambda x: x['CITY_NAME'], results)
        result = list(result)
        response["data"] = result
        # print(response)
        return jsonify(response), status.HTTP_200_OK
    except Exception as e:
        response = {}
        response["status"] = "FAILED"
        response["error"] = str(e)
        return jsonify(response), status.HTTP_500_INTERNAL_SERVER_ERROR


@app.route('/api/location', methods=['GET'])
@validate_key
def get_location():
    try:
        response = {}
        mydb = connectMySql()
        mycursor = mydb.cursor(dictionary=True)
        if request.args.get('country'):
            mycursor.execute(
                """SELECT * FROM MOCK_WEATHER.VW_DIM_LOCATION WHERE COUNTRY = '{}';""".format(request.args.get('country')))
        else:
            mycursor.execute(
                """SELECT * FROM MOCK_WEATHER.VW_DIM_LOCATION;""")
        results = mycursor.fetchall()
        # print(results)
        response["data"] = results
        # print(response)
        return jsonify(response), status.HTTP_200_OK
    except Exception as e:
        response = {}
        response["status"] = "FAILED"
        response["error"] = str(e)
        return jsonify(response), status.HTTP_500_INTERNAL_SERVER_ERROR


@app.route('/api/weather', methods=['GET'])
@validate_key
def get_weather():
    try:
        response = {}
        mydb = connectMySql()
        mycursor = mydb.cursor(dictionary=True)
        if request.args.get('city') and request.args.get('date'):
            mycursor.execute(
                """SELECT * FROM MOCK_WEATHER.WEATHER_DATA WHERE CITY_NAME = '{}' AND TIMESTAMP = '{}';""".format(request.args.get('city'), request.args.get('date')))
        elif request.args.get('city') and not request.args.get('date'):
            mycursor.execute(
                """SELECT * FROM MOCK_WEATHER.WEATHER_DATA WHERE CITY_NAME = '{}';""".format(request.args.get('city')))
        elif request.args.get('date') and not request.args.get('city'):
            mycursor.execute(
                """SELECT * FROM MOCK_WEATHER.WEATHER_DATA WHERE TIMESTAMP = '{}';""".format(request.args.get('date')))
        else:
            mycursor.execute(
                """SELECT * FROM MOCK_WEATHER.WEATHER_DATA;""")
        results = mycursor.fetchall()
        response["data"] = results
        return jsonify(response), status.HTTP_200_OK
    except Exception as e:
        response = {}
        response["status"] = "FAILED"
        response["error"] = str(e)
        return jsonify(response), status.HTTP_500_INTERNAL_SERVER_ERROR


@app.route('/api/keys', methods=['GET'])
def get_keys():
    try:
        if request.args.get("passkey") and request.args.get("passkey") == CONST_AUTH_PASS:
            if request.args.get("action"):
                response = {}
                mydb = connectMySql()
                mycursor = mydb.cursor(dictionary=True)
                if request.args.get("action") == "delete":
                    mycursor.execute("""TRUNCATE TABLE MOCK_WEATHER.AUTH;""")
                    response["status"] = "SUCCESS"
                    response["message"] = "delete completed"
                    return jsonify(response), status.HTTP_200_OK
                elif request.args.get("action") == "insert" and request.args.get("value"):
                    mycursor.execute("""INSERT INTO MOCK_WEATHER.AUTH (AUTH_KEY) VALUES('{}');""".format(
                        request.args.get("value")))
                    mydb.commit()
                    response["status"] = "SUCCESS"
                    response["message"] = "Insert completed"
                    return jsonify(response), status.HTTP_200_OK
                else:
                    response["status"] = "TERMINATED"
                    response["message"] = request.args.get(
                        "action") + " action not supported"
                    return jsonify(response), status.HTTP_404_NOT_FOUND
            else:
                response = {}
                mydb = connectMySql()
                mycursor = mydb.cursor(dictionary=True)
                mycursor.execute(
                    """SELECT AUTH_KEY FROM MOCK_WEATHER.AUTH""")
                results = mycursor.fetchall()
                result = map(lambda x: x['AUTH_KEY'], results)
                result = list(result)
                response["data"] = result
                return jsonify(response), status.HTTP_200_OK
        else:
            response = {}
            response["status"] = "FAILED"
            response["message"] = "Auth pass key is incorrect"
            return jsonify(response), status.HTTP_401_UNAUTHORIZED
    except Exception as e:
        response = {}
        response["status"] = "FAILED"
        response["error"] = str(e)
        return jsonify(response), status.HTTP_500_INTERNAL_SERVER_ERROR


if __name__ == '__main__':
    app.run(port=9000, debug=False)
