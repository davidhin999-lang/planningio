#!/usr/bin/env python3
"""
Clear easy/medium/hard leaderboards in Firestore.
Team leaderboard will remain intact.
"""
import os
from firebase_admin import credentials, firestore, initialize_app

# Initialize Firebase
firebase_key_path = os.path.join(os.path.dirname(__file__), "firebase-key.json")
if os.path.exists(firebase_key_path):
    cred = credentials.Certificate(firebase_key_path)
    initialize_app(cred)
    db = firestore.client()
    
    print("Clearing easy/medium/hard leaderboards...")
    
    for difficulty in ["easy", "medium", "hard"]:
        try:
            # Get all documents in the difficulty collection
            docs = db.collection("leaderboard").document(difficulty).collection("scores").list_documents()
            
            if docs:
                print(f"Found {len(docs)} entries in {difficulty} leaderboard")
                
                # Delete all documents
                for doc in docs:
                    doc.delete()
                    
                print(f"Cleared {difficulty} leaderboard")
            else:
                print(f"No entries found in {difficulty} leaderboard")
                
        except Exception as e:
            print(f"Error clearing {difficulty} leaderboard: {e}")
    
    print("Done! Team leaderboard remains intact.")
else:
    print("Firebase key not found. Skipping leaderboard clear.")
