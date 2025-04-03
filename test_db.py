from pymongo import MongoClient

# Update with your MongoDB connection details
MONGO_URI = "mongodb://localhost:27017"  # Change if using a different host
DB_NAME = "timetable_db"  # Change this to your actual database name

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client[DB_NAME]

# Fetch all subjects and faculty
print("Fetching subjects from Subject_collection:")
subjects = list(db["Subject_collection"].find({}))
for subject in subjects:
    print(subject)

print("\nFetching faculty from faculty collection:")
faculty = list(db["faculty"].find({}))
for member in faculty:
    print(member)

# Close connection
client.close()
