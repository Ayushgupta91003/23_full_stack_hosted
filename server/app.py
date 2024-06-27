from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from urllib.parse import quote_plus
import config

def encode_mongo_uri(uri):
    if '://' in uri:
        prefix, rest = uri.split('://', 1)
        if '@' in rest:
            userinfo, hostinfo = rest.split('@', 1)
            user, passwd = userinfo.split(':', 1)
            user = quote_plus(user)
            passwd = quote_plus(passwd)
            rest = f'{user}:{passwd}@{hostinfo}'
            return f'{prefix}://{rest}'
    return uri

app = Flask(__name__)
app.config["MONGO_URI"] = encode_mongo_uri(config.Config.MONGO_URI)
mongo = PyMongo(app)

@app.route('/products', methods=['GET'])
def get_products():
    products = mongo.db.products.find()
    result = []
    for product in products:
        result.append({
            '_id': str(product['_id']),
            'name': product['name'],
            'description': product['description'],
            'price': product['price'],
            'category': product['category']
        })
    return jsonify(result)

@app.route('/products/<id>', methods=['GET'])
def get_product(id):
    product = mongo.db.products.find_one({'_id': ObjectId(id)})
    if product:
        result = {
            '_id': str(product['_id']),
            'name': product['name'],
            'description': product['description'],
            'price': product['price'],
            'category': product['category']
        }
        return jsonify(result)
    else:
        return jsonify({'error': 'Product not found'}), 404

@app.route('/products', methods=['POST'])
def add_product():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No input data provided'}), 400
    new_product = {
        'name': data.get('name'),
        'description': data.get('description'),
        'price': data.get('price'),
        'category': data.get('category')
    }
    result = mongo.db.products.insert_one(new_product)
    return jsonify({'_id': str(result.inserted_id)}), 201

@app.route('/products/<id>', methods=['PUT'])
def update_product(id):
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No input data provided'}), 400
    updated_product = {
        'name': data.get('name'),
        'description': data.get('description'),
        'price': data.get('price'),
        'category': data.get('category')
    }
    result = mongo.db.products.update_one({'_id': ObjectId(id)}, {'$set': updated_product})
    if result.modified_count:
        return jsonify({'success': 'Product updated successfully'})
    else:
        return jsonify({'error': 'Product not found or no changes made'}), 404

@app.route('/products/<id>', methods=['DELETE'])
def delete_product(id):
    result = mongo.db.products.delete_one({'_id': ObjectId(id)})
    if result.deleted_count:
        return jsonify({'success': 'Product deleted successfully'})
    else:
        return jsonify({'error': 'Product not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)
