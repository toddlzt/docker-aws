from app import app
from flask import render_template, request,redirect,url_for, Flask
import os
import pymongo
from pymongo import MongoClient
import time
import urllib.request
import run
from bson.json_util import dumps
from pymongo.errors import ConfigurationError
from flask import jsonify
import dns.resolver
import datetime
from flask_cors import CORS, cross_origin
import logging
from bson.objectid import ObjectId
import json
app.logger.setLevel(logging.INFO)

def log_warn_ret(message):
    app.logger.warning(message)
    return message

def log_info_ret(message):
    app.logger.info(message)
    return message
    
try:
    client = pymongo.MongoClient("mongodb+srv://todd:O12345@cluster0.nloih.mongodb.net/myFirstDatabase?retryWrites=true&w=majority",serverSelectionTimeoutMS=10, connectTimeoutMS=20000, socketTimeoutMS=None, socketKeepAlive=True, connect=False, maxPoolsize=1)
    if not client:
        app.logger.error("No client")
        exit()
    db = client["cext"]
    if not db:
        app.logger.error("No db")
        exit()
    collection = db["2"]
    if not collection:
        app.logger.error("No collection")
        exit()
    app.logger.info("Database connected")
except ConfigurationError:
    app.logger.error("Database Connection failed. Error")
    exit()

def client_exist():
    connection = MongoClient("mongodb+srv://todd:O12345@cluster0.nloih.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
    try:
        connection.database_names()
        # app.logger.info('Data Base Connection Established........')
    except OperationFailure as err:
        app.logger.error("Data Base Connection failed. Error: {err}")
        return False
    if not client or not db or not collection:
        app.logger.error("no connection")
        return False
    return True

# comments {
#     "_id": xf0b2f55096f7622f6000000,
#     "comment_type": 1,
#     "website": url,
#     "user": email,
#     "parent_comment": xf0b2f55096f7622f6000000,
#     "text": "this is a comment",
#     "ratings": [12,23],
#     "date":"asdasddsa",
#     "img":[
#         "jksahfdkjhquionq123213"
#         "jksahfdkjhquionq123213"
#         "jksahfdkjhquionq123213"
#     ],
# }

def set_comments(search_method, content):
    date = datetime.datetime.now()
    comment = ""
    if search_method == "update":
        if "ratings" not in content:
            return log_warn_ret("No comment ratings")
        elif "user_id" not in content:
            return log_warn_ret("No comment user_id")
        comment = get_comments("id", {"_id": content["user_id"]})
        if comment:
            try:
                comment = collection.update_one({"comment_type": { "$exists" : True }, 
                                                "_id": ObjectId(content["user_id"])},
                                    {"$set": {"ratings": [comment["ratings"][0] + content["ratings"][0], 
                                                          comment["ratings"][1] + content["ratings"][1]]}})
            except:
                return log_warn_ret("Update comment _id issue")
                
            return get_comments("id", {"_id": content["user_id"]})
        else:
            return log_warn_ret("No comment found to be updated")
    elif search_method == "new":
        if "comment_type" not in content:
            return log_warn_ret("No comment comment_type")
        elif "website" not in content:
            return log_warn_ret("No comment website")
        elif "user_id" not in content:
            return log_warn_ret("No comment user_id")
        elif "parent_comment" not in content:
            return log_warn_ret("No comment parent_comment")
        elif "ratings" not in content:
            return log_warn_ret("No comment ratings")
        elif "text" not in content:
            return log_warn_ret("No comment text")

        comment_id = collection.insert_one({"comment_type": content["comment_type"],
                                         "website": content["website"], 
                                         "user_id": content["user_id"], 
                                         "parent_comment": content["parent_comment"], 
                                         "ratings": content["ratings"], 
                                         "text": content["text"], 
                                         "date":date})
        return get_comments("id",{"_id": comment_id.inserted_id})
    else:
        return log_warn_ret("No search_method set_comments")
    if comment and '_id' in comment:
        comment['_id'] = str(comment['_id'])
    return comment

def get_comments(search_method, content):
    comments = ""
    if search_method == "website":
        if "website" not in content:
            return log_warn_ret("No comment website")

        comments = list(collection.find({"comment_type":{ "$exists" : True }, "website": content["website"]}))
        for comment in comments:
            if comment and '_id' in comment:
                comment['_id'] = str(comment['_id'])
            else:
                break

            user = collection.find_one({"email": comment["user_id"]}) 
            if user and '_id' in user:
                user['_id'] = str(user['_id'])
            else:
                continue

            comment["user_id"] = user["_id"]
            comment["email"] = user["email"]
            comment["image"] = user["image"]
            comment["first_name"] = user["first_name"]
            comment["last_name"] = user["last_name"]

    elif search_method == "user":
        if "user_id" not in content:
            return log_warn_ret("No comment user_id")

        comments = list(collection.find({"comment_type":{ "$exists" : True }, "user_id": content["user_id"]})) 
        for comment in comments:
            if comment and '_id' in comment:
                comment['_id'] = str(comment['_id'])
            else:
                break
    elif search_method == "id":
        if "_id" not in content:
            return log_warn_ret("No comment _id")
        try:
            comments = collection.find_one({"comment_type":{ "$exists" : True }, "_id": ObjectId(content["_id"])}) 
        except:
            return log_warn_ret("No valid comment id")
        if comments and '_id' in comments:
            comments['_id'] = str(comments['_id'])
        return comments
    else:
        return log_warn_ret("No search method")
    
    return comments

# Websites {
#  "_id": 4f0b2f55096f7622f6000000,
#  "URL": "www.google.com",
#  "ratings": [2,3,4,5,24],
# }

def set_website(content):
    if "ratings" not in content:
        return log_warn_ret("No web ratings")
    elif "URL" not in content:
        return log_warn_ret("No web URL")
    website = get_website(content)

    if website == "not found":
        website = collection.insert_one({
            "url": content["URL"],
            "ratings": content["ratings"]})
    else:
        website = get_website(content)
        website = collection.update_one({"url": content["URL"]},
                              {"$set": {"ratings": [website["ratings"][0] + content["ratings"][0], 
                                                    website["ratings"][1] + content["ratings"][1],
                                                    website["ratings"][2] + content["ratings"][2],
                                                    website["ratings"][3] + content["ratings"][3],
                                                    website["ratings"][4] + content["ratings"][4]]}})
    return get_website(content)

def get_website(content):
    if "URL" not in content:
        return log_warn_ret("No web URL")
    website = collection.find_one({"url":content["URL"]})
    if website and '_id' in website:
        website['_id'] = str(website['_id'])
        return website
    else:
        return log_warn_ret("not found")

#  Users {
#           "id": lf0b2f55096f7622f6000000
#           "email": "li.zhengtao5@gmail.com", 
#           "last_name": "Li", 
#           "first_name": "Zhengtao", 
#           "signup_date":"20023823"
#           "image":"jksahfdkjhquionq123213"
#  }

def set_user(content):
    existing_user = get_user(content)
    app.logger.warning(existing_user != "No user found")
    if existing_user == "No user found":
        date = datetime.datetime.now()
        if "last_name" not in content:
            return log_warn_ret("No user last_name")
        elif "first_name" not in content:
            return log_warn_ret("No user first_name")
        elif "image" not in content:
            return log_warn_ret("No user image")
        new_user = collection.insert_one({
            "email": content["email"], 
            "last_name": content["last_name"], 
            "first_name": content["first_name"], 
            "signup_date": date, 
            "image":content["image"]})
        return get_user(content)
    else:
        return log_warn_ret("user already exist")

def get_user(content):
    if "email" not in content:
        return log_warn_ret("No user email")
    user = collection.find_one({"email": content["email"]}) 
    if user and '_id' in user:
        user['_id'] = str(user['_id'])
        return user
    else:
        return log_info_ret("No user found")

def get(category, search_method, content):
    result = ""
    if category == "website":
        result = get_website(content)
    elif category == "user":
        result = get_user(content)
    elif category == "comments":
        result = get_comments(search_method, content)
    else:
        return log_warn_ret("Unknown category")
    return result

def set(category, search_method, content):
    result = ""
    if category == "website":
        result = set_website(content)
    elif category == "user":
        result = set_user(content)
    elif category == "comments":
        result = set_comments(search_method, content)
    else:
        return log_warn_ret("Unknown category")
    return result


@app.route("/")
@cross_origin()
def origin():
    return jsonify(success=True)

@app.route("/<action>/<category>/", methods=["POST","GET","OPTIONS"], defaults={'search_method': None})
@app.route("/<action>/<category>/<search_method>/", methods=["POST","GET","OPTIONS"])
@cross_origin()
def api(action, category, search_method):
    if request.method == "OPTIONS":
        app.logger.info('OPTIONS')
        return jsonify(success=True)
    elif request.method == "GET":
        app.logger.info('GET')
        return jsonify(success=True)
    elif request.method == "POST":
        app.logger.info('POST')
        if action and category:
            content = request.json
            result = ""

            app.logger.info(content)
            
            if action == "get":
                result = get(category, search_method, content)
            elif action == "set":
                result = set(category, search_method, content)
            else:
                return log_warn_ret("Unknown category")

            app.logger.info(result)
            
            return jsonify(result)
        else:
            return log_warn_ret("No action or category")
    else:
        return log_warn_ret("Unknown request.method")

    return jsonify(success=True)

@app.route('/')
@app.route('/<path:dummy>')
def fallback(dummy=None):
    return log_warn_ret('fall back')
