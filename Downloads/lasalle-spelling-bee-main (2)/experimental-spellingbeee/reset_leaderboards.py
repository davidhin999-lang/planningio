#!/usr/bin/env python3
"""
Clear leaderboards and keep only the highest score per user per difficulty.
This will reset all leaderboards to empty, allowing fresh starts.
"""
import os
import json
from firebase_admin import credentials, firestore, initialize_app

# Initialize Firebase if available
firebase_key_path = os.path.join(os.path.dirname(__file__), "firebase-key.json")
USE_FIRESTORE = os.path.exists(firebase_key_path)

if USE_FIRESTORE:
    cred = credentials.Certificate(firebase_key_path)
    initialize_app(cred)
    db = firestore.client()
    print("Using Firestore for leaderboard reset")
else:
    print("Using local JSON file for leaderboard reset")

LEADERBOARD_FILE = os.path.join(os.path.dirname(__file__), "leaderboard.json")

def reset_firestore_leaderboards():
    """Clear all Firestore leaderboards"""
    try:
        for difficulty in ["easy", "medium", "hard"]:
            # Get all documents in the difficulty collection
            docs = db.collection("leaderboard").document(difficulty).collection("scores").list_documents()
            
            if docs:
                print(f"Clearing {len(docs)} entries from {difficulty} leaderboard")
                
                # Delete all documents
                for doc in docs:
                    doc.delete()
                    
            else:
                print(f"No entries found in {difficulty} leaderboard")
        
        print("Firestore leaderboards cleared successfully")
    except Exception as e:
        print(f"Error clearing Firestore leaderboards: {e}")

def reset_json_leaderboard():
    """Clear local JSON leaderboard file"""
    try:
        # Create empty leaderboard structure
        empty_leaderboard = {
            "easy": [],
            "medium": [],
            "hard": []
        }
        
        with open(LEADERBOARD_FILE, "w", encoding="utf-8") as f:
            json.dump(empty_leaderboard, f, ensure_ascii=False, indent=2)
        
        print("Local JSON leaderboard cleared successfully")
    except Exception as e:
        print(f"Error clearing JSON leaderboard: {e}")

def main():
    print("Resetting leaderboards - keeping only highest score per user per difficulty")
    print("   (This clears all existing scores to start fresh)")
    print()
    
    if USE_FIRESTORE:
        reset_firestore_leaderboards()
    else:
        reset_json_leaderboard()
    
    print()
    print("Leaderboard reset complete!")
    print("   - All previous scores have been cleared")
    print("   - New scores will follow 'one per user per difficulty (highest wins)' rule")
    print("   - Team leaderboard remains unaffected")

if __name__ == "__main__":
    main()
