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
    
class website:
    def __init__(self, url, create_if_not_found = False):
        website = collection.find_one({"url":url})
        if (not website or '_id' not in website) and create_if_not_found:
            date = datetime.datetime.now()
            website = collection.insert_one({
                "url": url,
                "views": 0,
                "created": date,
                "ratings": {"customerService": 0,
                            "shippingSpeed": 0,
                            "productQuality": 0},
                "numRatings": 0 
            })
        website['_id'] = str(website['_id'])

        self._id = website["_id"]
        self.created = website["created"]
        self.numRatings = website["numRatings"]
        self.ratings["customerService"] = website["ratings"]["customerService"]
        self.ratings["productQuality"] = website["ratings"]["productQuality"]
        self.ratings["shippingSpeed"] = website["ratings"]["shippingSpeed"]
        self.url = website["url"]
        self.views = website["views"]
    
    def add_view():
        self.views += 1
        collection.update_one({"url": { "$exists" : True }, 
                               "url": self.url},
                     {"$set": {"views": self.views}})
    def add_ratings(content):
        self.ratings["customerService"] += content["ratings"]["customerService"]
        self.ratings["shippingSpeed"] += content["ratings"]["shippingSpeed"]
        self.ratings["productQuality"] += content["ratings"]["productQuality"]
        self.numRatings += 1
        collection.update_one({"url": { "$exists" : True }, 
                               "url": self.url},
                     {"$set": {"ratings": website["ratings"],
                               "numRatings": website["numRatings"]
                     }})
    def output():
        return jsonify({
            "_id": self._id,
            "created": self.created,
            "numRatings": self.numRatings,
            "ratings": self.ratings,
            "url": self.url,
            "views": self.views,
        })

class user:
    def __init__(self, content, create_if_not_found = False):
        user = collection.find_one({"email": content["email"]}) 
        if (not user or '_id' not in user) and create_if_not_found:
            date = datetime.datetime.now()
            user = collection.insert_one({
                "email": content["email"], 
                "last_name": content["last_name"], 
                "first_name": content["first_name"], 
                "signup_date": date, 
                "image":content["image"],
                "likes":[],
                "comments":[],
                "history":[]
                })

        user['_id'] = str(user['_id'])
        
        self._id = user["_id"]
        self.email = user["email"]
        self.last_name = user["last_name"]
        self.first_name = user["first_name"]
        self.signup_date = user["signup_date"]
        self.image = user["image"]
        self.likes = user["likes"]
        self.comments = user["comments"]
        self.history = user["history"]
  
    def add_comment():
        return
    
    def add_like():
        return

    def add_history():
        return

    def output():
        return jsonify({
            "_id": self._id,
            "email": self.email,
            "last_name": self.last_name,
            "first_name": self.first_name,
            "signup_date": self.signup_date,
            "image": self.image,
            "likes": self.likes,
            "comments": self.comments,
            "history": self.history,
        }) 

class comment:
    def __init__(self, method, content, create_if_not_found = False):
        content["URL"] = content["website"]
        website = get_website(content)

        website = set_website("ratings",content,website)


        comment_id = collection.insert_one({"comment_type": content["comment_type"],
                                         "website": content["website"], 
                                         "user_id": content["user_id"], 
                                         "title": content["title"], 
                                         "child_comments": [], 
                                         "ratings": content["ratings"], 
                                         "text": content["text"], 
                                         "date": date,
                                         "views": 0,
                                         "likes": [0,0],
                                         })
        
        comment = get_comments("id",{"_id": comment_id.inserted_id})

        content["_id"] = content["user_id"]
        user = get_user("id",content) 
        if user and '_id' in user:
            user['_id'] = str(user['_id'])
        else:
            return comment
        comment["user_id"] = user["_id"]
        comment["email"] = user["email"]
        comment["image"] = user["image"]
        comment["first_name"] = user["first_name"]
        comment["last_name"] = user["last_name"]
    def add_child():
        return
    def add_view():
        return
    def like_child():
        return
    def like_parent():
        return
    def output():
        return

try:
    client = pymongo.MongoClient("mongodb+srv://todd:O12345@cluster0.nloih.mongodb.net/myFirstDatabase?retryWrites=true&w=majority",serverSelectionTimeoutMS=10, connectTimeoutMS=20000, socketTimeoutMS=None, socketKeepAlive=True, connect=False, maxPoolsize=1)
    if not client:
        app.logger.error("No client")
        exit()
    db = client["cext"]
    if not db:
        app.logger.error("No db")
        exit()
    collection = db["3"]
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
#     "title": this is title,
#     "child_comments": xf0b2f55096f7622f6000000,
#     "text": "this is a comment",
#     "stats": [12,23],
#     "date":"asdasddsa",
#     "img":[
#         "jksahfdkjhquionq123213"
#         "jksahfdkjhquionq123213"
#         "jksahfdkjhquionq123213"
#     ],
# }

def set_comments(action, content, comment = None):
    date = datetime.datetime.now()
    # if action == "update_main":
    if action == "add_child":
        if "user_id" not in content:
            return log_warn_ret("No comment user_id")
        elif "parent_id" not in content:
            return log_warn_ret("No comment parent_id")
        elif "text" not in content:
            return log_warn_ret("No comment text")

        comment = get_comments("id",{"_id": content["parent_id"]})
        if comment == "No valid comment id":
            return log_warn_ret("No valid comment id")

        user = get_user("id",{"_id": content["user_id"]})
        if user == "Get user by id no user":
            return log_warn_ret("Get user by id no user")

        comment["child_comments"].append({"id": len(comment["child_comments"]),
                                          "user_id": content["user_id"],
                                          "likes": [0,0],
                                          "views": 0,
                                          "date": date,
                                          "text": content["text"]})

        collection.update_one({"comment_type":{ "$exists" : True }, "_id": ObjectId(content["parent_id"])},
                                {"$set": {"child_comments": comment["child_comments"]}})
        return comment
    elif action == "like_child":
        if "user_id" not in content:
            return log_warn_ret("No comment user_id")
        elif "parent_id" not in content:
            return log_warn_ret("No comment parent_id")
        elif "like" not in content:
            return log_warn_ret("No comment like")
        elif "index" not in content:
            return log_warn_ret("No comment index")

        comment = get_comments("id",{"_id": content["parent_id"]})
        if comment == "No valid comment id":
            return log_warn_ret("No valid comment id")

        user = get_user("id",{"_id": content["user_id"]})
        if user == "Get user by id no user":
            return log_warn_ret("Get user by id no user")

        if content["like"] == True:
            comment["child_comments"][content["index"]]["likes"][0] += 1
        else:
            comment["child_comments"][content["index"]]["likes"][1] += 1


        collection.update_one({"comment_type":{ "$exists" : True }, "_id": ObjectId(content["parent_id"])},
                                {"$set": {"child_comments": comment["child_comments"]}})
        return comment
    elif action == "like_parent":
        if "user_id" not in content:
            return log_warn_ret("No comment user_id")
        elif "parent_id" not in content:
            return log_warn_ret("No comment parent_id")
        elif "like" not in content:
            return log_warn_ret("No comment like")

        comment = get_comments("id",{"_id": content["parent_id"]})
        if comment == "No valid comment id":
            return log_warn_ret("No valid comment id")

        user = get_user("id",{"_id": content["user_id"]})
        if user == "Get user by id no user":
            return log_warn_ret("Get user by id no user")
        
        if content["like"] == True:
            comment["likes"][0] += 1
        else:
            comment["likes"][1] += 1

        collection.update_one({"comment_type":{ "$exists" : True }, "_id": ObjectId(content["parent_id"])},
                                {"$set": {"likes": comment["likes"]}})
        return comment

    elif action == "views":
        if comment == None:
            return
        if "views" in comment:
            comment["views"] += 1
        if "child_comments" in comment:
            for idx in range(0,len(comment["child_comments"])):
                comment["child_comments"][idx]["views"] += 1
        return comment
    elif action == "new":
        if "comment_type" not in content:
            return log_warn_ret("No comment comment_type")
        elif "website" not in content:
            return log_warn_ret("No comment website")
        elif "user_id" not in content:
            return log_warn_ret("No comment user_id")
        elif "title" not in content:
            return log_warn_ret("No comment title")
        elif "ratings" not in content:
            return log_warn_ret("No comment ratings")
        elif "customerService" not in content["ratings"]:
            return log_warn_ret("No comment customerService")
        elif "productQuality" not in content["ratings"]:
            return log_warn_ret("No comment productQuality")
        elif "shippingSpeed" not in content["ratings"]:
            return log_warn_ret("No comment shippingSpeed")
        elif "text" not in content:
            return log_warn_ret("No comment text")

        content["URL"] = content["website"]
        website = get_website(content)

        website = set_website("ratings",content,website)


        comment_id = collection.insert_one({"comment_type": content["comment_type"],
                                         "website": content["website"], 
                                         "user_id": content["user_id"], 
                                         "title": content["title"], 
                                         "child_comments": [], 
                                         "ratings": content["ratings"], 
                                         "text": content["text"], 
                                         "date": date,
                                         "views": 0,
                                         "likes": [0,0],
                                         })
        
        comment = get_comments("id",{"_id": comment_id.inserted_id})

        content["_id"] = content["user_id"]
        user = get_user("id",content) 
        if user and '_id' in user:
            user['_id'] = str(user['_id'])
        else:
            return comment
        comment["user_id"] = user["_id"]
        comment["email"] = user["email"]
        comment["image"] = user["image"]
        comment["first_name"] = user["first_name"]
        comment["last_name"] = user["last_name"]
        return comment
    else:
        return log_warn_ret("No action set_comments")
    if comment and '_id' in comment:
        comment['_id'] = str(comment['_id'])
    return comment

def get_comments(action, content):
    comments = ""
    if action == "website":
        if "website" not in content:
            return log_warn_ret("No comment website")
        
        comments = list(collection.find({"comment_type":{ "$exists" : True }, "website": content["website"]}))
        for comment in comments:
            s = ""
            if comment and '_id' in comment:
                comment['_id'] = str(comment['_id'])
            else:
                break
            content["_id"] = comment["user_id"]
            user = get_user("id",content) 

            if user and '_id' in user:
                user['_id'] = str(user['_id'])
            else:
                continue

            comment["user_id"] = user["_id"]
            comment["email"] = user["email"]
            comment["image"] = user["image"]
            comment["first_name"] = user["first_name"]
            comment["last_name"] = user["last_name"]
        
            comment = set_comments("views","",comment)
            collection.update_one({"comment_type": { "$exists" : True }, 
                        "_id": ObjectId(comment["_id"])},
                        {"$set": {"views": comment["views"],
                                  "child_comments": comment["child_comments"]
                                }})
            # if ("child_comments" in comment and len(comment["child_comments"]) > 0)
            #     comment["has_child_comments"] = True
            # else:
            #     comment["has_child_comments"] = False

            comment.pop('child_comments', None)
    elif action == "user":
        if "user_id" not in content:
            return log_warn_ret("No comment user_id")

        comments = list(collection.find({"comment_type":{ "$exists" : True }, "user_id": content["user_id"]})) 
        for comment in comments:
            if comment and '_id' in comment:
                comment['_id'] = str(comment['_id'])
            else:
                break
    elif action == "id":
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
#  "stats": [2,3,4,5,24],
# }

def set_website(action, content, website=None):
    if "URL" not in content:
        return log_warn_ret("No web URL")

    if action == "new":
        date = datetime.datetime.now()
        website = collection.insert_one({
            "url": content["URL"],
            "views": 0,
            "created": date,
            "ratings": {"customerService": 0,
                        "shippingSpeed": 0,
                        "productQuality": 0},
            "numRatings": 0 
        })
    elif action == "views":
        website["views"] += 1
        collection.update_one({"url": { "$exists" : True }, 
                               "url": content["URL"]},
                                {"$set": {"views": website["views"]}})
        return website
    elif action == "ratings":
        website["ratings"]["customerService"] += content["ratings"]["customerService"]
        website["ratings"]["shippingSpeed"] += content["ratings"]["shippingSpeed"]
        website["ratings"]["productQuality"] += content["ratings"]["productQuality"]
        website["numRatings"] += 1
        collection.update_one({"url": { "$exists" : True }, 
                               "url": content["URL"]},
                                {"$set": {"ratings": website["ratings"],
                                          "numRatings": website["numRatings"]
                                        }})
        return website
    else:
        return log_warn_ret("Set web no action")

    return get_website(content)

def get_website(content):
    if "URL" not in content:
        return log_warn_ret("No web URL")
    website = collection.find_one({"url":content["URL"]})
    if website and '_id' in website:
        website['_id'] = str(website['_id'])
        return set_website("views",content, website)
    else:
        return set_website("new",content)


#  Users {
#           "id": lf0b2f55096f7622f6000000
#           "email": "li.zhengtao5@gmail.com", 
#           "last_name": "Li", 
#           "first_name": "Zhengtao", 
#           "signup_date":"20023823"
#           "image":"jksahfdkjhquionq123213"
#  }

def set_user(action, content):
    existing_user = get_user("email",content)
    if action == "new":
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
                "image":content["image"],
                "likes":[],
                "comments":[],
                "history":[]
                })
            return get_user("email",content)
        else:
            return log_warn_ret("user already exist")
    # elif action == "add comment":


def get_user(action, content):
    user = ""
    if action == "email":
        if "email" not in content:
            return log_warn_ret("No user email")
        user = collection.find_one({"email": content["email"]}) 
    elif action == "id":
        if "_id" not in content:
            return log_warn_ret("No user id")
        try:
            user = collection.find_one({"_id": ObjectId(content["_id"])}) 
        except:
            return log_warn_ret("Get user by id no user")
    else:
        return log_warn_ret("No search method")

    if user and '_id' in user:
        user['_id'] = str(user['_id'])
        return user
    else:
        return log_info_ret("No user found")

def get(category, action, content):
    result = ""
    if category == "website":
        result = get_website(content)
    elif category == "user":
        result = get_user(action, content)
    elif category == "comments":
        result = get_comments(action, content)
    else:
        return log_warn_ret("Unknown category")
    return result

def set(category, action, content):
    result = ""
    if category == "user":
        result = set_user("new", content)
    elif category == "comments":
        result = set_comments(action, content)
    else:
        return log_warn_ret("Unknown category")
    return result


@app.route("/")
@cross_origin()
def origin():
    return jsonify(success=True)

@app.route("/<method>/<category>/", methods=["POST","GET","OPTIONS"], defaults={'action': None})
@app.route("/<method>/<category>/<action>/", methods=["POST","GET","OPTIONS"])
@cross_origin()
def api(method, category, action):
    if request.method == "OPTIONS":
        app.logger.info('OPTIONS')
        return jsonify(success=True)
    elif request.method == "GET":
        app.logger.info('GET')
        return jsonify(success=True)
    elif request.method == "POST":
        app.logger.info('POST')
        if method and category:
            content = request.json
            result = ""

            app.logger.info(content)
            
            if method == "get":
                result = get(category, action, content)
            elif method == "set":
                result = set(category, action, content)
            else:
                return log_warn_ret("Unknown category")

            app.logger.info(result)
            
            return jsonify(result)
        else:
            return log_warn_ret("No method or category")
    else:
        return log_warn_ret("Unknown request.method")

    return jsonify(success=True)

@app.route('/')
@app.route('/<path:dummy>')
def fallback(dummy=None):
    return log_warn_ret('fall back')
