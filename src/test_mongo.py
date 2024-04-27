import pymongo
from pymongo import MongoClient

# Connect to MongoDB
cluster = MongoClient("mongodb+srv://ip2294:vZGaG2ngwrXFxZnL@mtastationdata.jwckd6t.mongodb.net/?retryWrites=true&w=majority&appName=MTAStationData")
db = cluster["MTA"]
collection = db["ridership"]

# Insert a document (test data)
insert_result = collection.insert_one({"_id": 0, "user_name": "Soumi"})
print(f"Insert Result: {insert_result.inserted_id}")

# Retrieve and print the inserted document to verify
retrieved_document = collection.find_one({"_id": 0})
print("Retrieved Document:", retrieved_document)

# Optionally, to understand more about the existing data structure:
# Fetch and print the first few documents in the collection
for doc in collection.find().limit(5):  # Limit to first 5 docs for brevity
    print(doc)
