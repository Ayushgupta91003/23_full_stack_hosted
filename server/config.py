import os

class Config:
    MONGO_URI = os.getenv('MONGO_URI', 'your_mongodb_uri_here')
