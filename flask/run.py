from app import app
import pymongo
from pymongo import MongoClient

print("Started from run.py")

def connect(host='https://google.com'):
    try:
        urllib.request.urlopen(host) #Python 3.x
        return True
    except:
        return False

if __name__ == "__main__":
    print( "Connected" if connect() else "No internet!" )
    app.run(debug=False)