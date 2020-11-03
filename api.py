#!/usr/bin/python3
import pymysql
from app import app
from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from sqlalchemy import create_engine
from json import dumps
from db_config import mysql
import json
import collections
from flask_api import status
import uuid

api = Api(app)

class Authenticate(Resource):
    def post(self):
        try:
            username = request.json['username']
            password = request.json['password']
            if username and password and request.method == 'POST':
                query = "SELECT * FROM users WHERE username=%s AND password=%s LIMIT 1"
                data = (username, password)
                conn = mysql.connect()
                cursor = conn.cursor()
                cursor.execute(query, data)
                rows = cursor.fetchone()
                rows_count = cursor.rowcount
                if rows_count == 0:
                    raise Exception("Invalid User")

                token = str(uuid.uuid4())
                self.update_token(username, token)
                response = {'token': token}
                return response, status.HTTP_200_OK
            else:
                raise Exception("Invalid Request")
        except  Exception as e:
            response = {'message': format(e)}
            return response, status.HTTP_401_UNAUTHORIZED

    def update_token(self, username, token):
        try:
            query = "UPDATE users SET token=%s WHERE username=%s"
            data = (token, username)
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.execute(query, data)
            conn.commit()
        except  Exception as e:
            response = {'message': format(e)}
            return response, status.HTTP_401_UNAUTHORIZED

class Register(Resource):
    def post(self):
        try:
            username = request.json['username']
            email = request.json['email']
            phone = request.json['phone']
            password = request.json['password']
            aadhar_no = request.json['aadhar_no']
            if username == None:
                raise Exception('username is missing')
            elif email == None:
                raise Exception('email is missing')
            elif phone == None:
                raise Exception('phone is missing')
            elif password == None:
                raise Exception('password is missing')
            elif aadhar_no == None:
                raise Exception('aadhar_no is missing')

            if self.is_user_exists(username, email):
                raise Exception("User already exists")

            query = "INSERT INTO users(username, password, is_voted, token, email, aadhar_no, phone) VALUES(%s, %s, %a, %s, %s, %s, %s)"
            data = (username, password, 0, "", email, aadhar_no, phone)
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.execute(query, data)
            conn.commit()
            response = {'message': 'User Registered'}
            return response, status.HTTP_201_CREATED
        except Exception as e:
            response = {'message': format(e)}
            return response, status.HTTP_400_BAD_REQUEST

    def is_user_exists(self, username, email):
        query = "SELECT * FROM users WHERE username=%s OR email=%s"
        data = (username, email)
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute(query, data)
        rows = cursor.fetchall()
        rows_count = cursor.rowcount
        if rows_count == 0:
            return False

        return True

class GetUserDetails(Resource):
    def get(self, username):
        try:
            token = request.headers.get('Authorization')
            if token == None:
                raise Exception("Unauthorized")
            elif not 'Basic' in token:
                raise Exception("Unauthorized")
            token = token.lstrip('Basic')
            token = token.lstrip()
            if not self.is_valid_auth(username, token):
                raise Exception("Unauthorized")
            query = "SELECT * FROM users WHERE username=%s LIMIT 1"
            data = (username)
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.execute(query, data)
            rows = cursor.fetchone()
            rows_count = cursor.rowcount
            if rows_count == 0:
                raise Exception("User not found")
            response = {
                'username': rows[1],
                'is_voted': rows[3],
                'email': rows[5],
                'aadhar_no': rows[6],
                'phone': rows[7],
                'image_data': rows[8]
            }
            return response, status.HTTP_200_OK
        except Exception as e:
            response = {'message': format(e)}
            if format(e) == 'Unauthorized':
                return response, status.HTTP_401_UNAUTHORIZED
            return response, status.HTTP_400_BAD_REQUEST

    def is_valid_auth(self, username, token):
        query = "SELECT * FROM users WHERE username=%s AND token=%s"
        data = (username, token)
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute(query, data)
        rows = cursor.fetchone()
        rows_count = cursor.rowcount
        if rows_count == None:
            return False

        return True

class CastVote(Resource):
    def post(self):
        try:
            token = request.headers.get('Authorization')
            if token == None:
                raise Exception("Unauthorized")
            elif not 'Basic' in token:
                raise Exception("Unauthorized")
            username = request.json['username']
            is_voted = True
            token = token.lstrip('Basic')
            token = token.lstrip()
            if not self.is_valid_auth(username, token):
                raise Exception("Unauthorized")
            elif self.has_user_voted(username):
                raise Exception("User already voted")

            query = "UPDATE users SET is_voted=%a WHERE username=%s"
            data = (True, username)
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.execute(query, data)
            conn.commit()
            response = {'message': "Voted"}
            return response, status.HTTP_202_ACCEPTED
        except Exception as e:
            response = {'message': format(e)}
            if format(e) == 'Unauthorized':
                return response, status.HTTP_401_UNAUTHORIZED
            return response, status.HTTP_400_BAD_REQUEST

    def has_user_voted(self, username):
        query = "SELECT * FROM users WHERE username=%s"
        data = (username)
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute(query, data)
        rows = cursor.fetchone()
        if rows[3] != 1:
            return False

        return True

    def is_valid_auth(self, username, token):
        query = "SELECT * FROM users WHERE username=%s AND token=%s"
        data = (username, token)
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute(query, data)
        rows = cursor.fetchone()
        rows_count = cursor.rowcount
        if rows_count == 0:
            return False

        return True

class Otp(Resource):
    def post(self):
        try:
            if request.args.get('generate') == '1':
                response = {'message' : 'OTP generated'}
                return response, status.HTTP_201_CREATED
            elif request.args.get('validate') == '1':
                token = request.headers.get('Authorization')
                if token == None:
                    raise Exception("Unauthorized")
                elif not 'Basic' in token:
                    raise Exception("Unauthorized")
                username = request.json['username']
                otp = request.json['otp']
                token = token.lstrip('Basic')
                token = token.lstrip()
                if not self.is_valid_auth(username, token):
                    raise Exception("Unauthorized")

                if otp != '123123':
                    raise Exception("Invalid OTP")

                response = {'message': 'OTP validated'}
                return response, status.HTTP_200_OK
            else:
                raise Exception("Invalid Request")
        except Exception as e:
            response = {'message': format(e)}
            if format(e) == 'Unauthorized':
                return response, status.HTTP_401_UNAUTHORIZED
            return response, status.HTTP_400_BAD_REQUEST

    def is_valid_auth(self, username, token):
        query = "SELECT * FROM users WHERE username=%s AND token=%s"
        data = (username, token)
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute(query, data)
        rows = cursor.fetchone()
        rows_count = cursor.rowcount
        if rows_count == 0:
            return False

        return True

class Image(Resource):
    def post(self):
        try:
            token = request.headers.get('Authorization')
            if token == None:
                raise Exception("Unauthorized")
            elif not 'Basic' in token:
                raise Exception("Unauthorized")
            username = request.json['username']
            image_data = request.json['image_data']
            token = token.lstrip('Basic')
            token = token.lstrip()
            if not self.is_valid_auth(username, token):
                raise Exception("Unauthorized")
            query = "UPDATE users SET image_data=%s WHERE username=%s"
            data = (image_data, username)
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.execute(query, data)
            conn.commit()
            response = {'message': "Image Registered"}
            return response, status.HTTP_201_CREATED
        except Exception as e:
            response = {'message': format(e)}
            if format(e) == 'Unauthorized':
                return response, status.HTTP_401_UNAUTHORIZED
            return response, status.HTTP_400_BAD_REQUEST

    def is_valid_auth(self, username, token):
        query = "SELECT * FROM users WHERE username=%s AND token=%s"
        data = (username, token)
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute(query, data)
        rows = cursor.fetchone()
        rows_count = cursor.rowcount
        if rows_count == 0:
            return False

        return True


class Leaders(Resource):
    def get(self, username):
        try:
            token = request.headers.get('Authorization')
            if token == None:
                raise Exception("Unauthorized")
            elif not 'Basic' in token:
                raise Exception("Unauthorized")
            token = token.lstrip('Basic')
            token = token.lstrip()
            if not self.is_valid_auth(username, token):
                raise Exception("Unauthorized")
            query = "SELECT * FROM leaders"
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            rows_count = cursor.rowcount
            if rows_count == 0:
                raise Exception("Leaders not found")
            response =[]
            for i in rows:
                obj = {
                    'label': i[1] + ":" + i[2],
                    'value': i[1] + ":" + i[2]
                }
                response.append(obj)
            return response, status.HTTP_200_OK
        except Exception as e:
            response = {'message': format(e)}
            if format(e) == 'Unauthorized':
                return response, status.HTTP_401_UNAUTHORIZED
            return response, status.HTTP_400_BAD_REQUEST

    def is_valid_auth(self, username, token):
        query = "SELECT * FROM users WHERE username=%s AND token=%s"
        data = (username, token)
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute(query, data)
        rows = cursor.fetchone()
        rows_count = cursor.rowcount
        if rows_count == 0:
            return False

        return True

class LogOut(Resource):
    def post(self):
        try:
            token = request.headers.get('Authorization')
            if token == None:
                raise Exception("Unauthorized")
            elif not 'Basic' in token:
                raise Exception("Unauthorized")
            token = token.lstrip('Basic')
            token = token.lstrip()
            username = request.json['username']
            if not self.is_valid_auth(username, token):
                raise Exception("Unauthorized")
            query = "UPDATE users SET token=%s WHERE username=%s"
            data = ("", username)
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.execute(query, data)
            conn.commit()
            response = {'message': 'Logged Out'}
            return response, status.HTTP_200_OK
        except Exception as e:
            response = {'message': format(e)}
            if format(e) == 'Unauthorized':
                return response, status.HTTP_401_UNAUTHORIZED
            return response, status.HTTP_400_BAD_REQUEST

    def is_valid_auth(self, username, token):
        query = "SELECT * FROM users WHERE username=%s AND token=%s"
        data = (username, token)
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute(query, data)
        rows = cursor.fetchone()
        rows_count = cursor.rowcount
        if rows_count == 0:
            return False

        return True




api.add_resource(Authenticate, '/v1/authenticate')
api.add_resource(Register, '/v1/register')
api.add_resource(GetUserDetails, '/v1/user/<username>')
api.add_resource(CastVote, '/v1/cast-vote')
api.add_resource(Otp, '/v1/otp')
api.add_resource(Image, '/v1/image')
api.add_resource(Leaders, '/v1/leaders/<username>')
api.add_resource(LogOut, '/v1/logout')


if __name__ == '__main__':
     app.run(host='0.0.0.0', port=3000)
