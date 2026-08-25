"""
Quick test to verify MongoDB connection after setup.
"""
import asyncio
from app.core.mongodb import get_mongodb
from app.core.config import get_config

async def test_connection():
    config = get_config()
    print(f"Testing MongoDB connection to: {config.mongodb_db_name}")
    
    mongo = get_mongodb()
    result = await mongo.connect()
    
    if result:
        print("SUCCESS: MongoDB connected!")
        print(f"Database: {config.mongodb_db_name}")
        
        # Test writing data
        test_data = {
            "conversation_id": "test_123",
            "messages": [{"role": "user", "content": "test message"}],
            "jurisdiction": "India",
            "language": "en"
        }
        await mongo.save_message("test_123", test_data["messages"][0])
        print("SUCCESS: Can write to MongoDB")
        
        # Test reading data
        conversation = await mongo.get_conversation("test_123")
        print(f"SUCCESS: Can read from MongoDB: {conversation is not None}")
        
    else:
        print("FAILED: MongoDB connection failed")
        print("Check your MongoDB URI and network connection")
    
    await mongo.close()

if __name__ == "__main__":
    asyncio.run(test_connection())