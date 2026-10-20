import sqlite3
import requests

def run_video_architecture():
    print("1. Fetching data directly from the local SQLite database...")
    
    # Connect to the database and run the SQL query in Python (Just like Vignesh's ZCQL)
    conn = sqlite3.connect("karnataka_police_fir.db")
    cursor = conn.cursor()
    
    # Get total cases
    cursor.execute("SELECT COUNT(*) FROM CaseMaster")
    total_cases = cursor.fetchone()[0]
    
    # Get Honnavar cases (PoliceStationID 3000)
    cursor.execute("SELECT COUNT(*) FROM CaseMaster WHERE PoliceStationID = 3000")
    honnavar_cases = cursor.fetchone()[0]
    conn.close()
    
    # Package the data neatly
    db_data = f"Total registered cases in Karnataka: {total_cases}. Cases at Honnavar Town Police Station: {honnavar_cases}."
    print(f"   -> Found: {db_data}")
    
    # ... (keep the database fetching code at the top exactly the same) ...

    print("\n2. Sending data to Zoho GLM 4.7 Flash for NLP processing...")
    
    # Using your actual real token from Postman
    api_token = "1000.da1daf52002c3ccf0850d7ef2d5b7113.775628d82c0ff0e3cf808d9eee6ef175" 
    url = "https://api.catalyst.zoho.in/quickml/v1/project/46199000000013024/glm/chat"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Zoho-oauthtoken {api_token}",
        "CATALYST-ORG": "60075406816"
    }
    
    # THE FIX: Split the payload exactly as shown in image_31a9e5.png
    payload = {
        "model": "crm-di-glm47b_30b_it",
        "messages": [
            {
                "role": "system",
                "content": "You are an assistant for a police crime record system. Answer the user's question naturally in English based strictly on the provided database information."
            },
            {
                "role": "user",
                "content": f"DATABASE INFORMATION:\n{db_data}\n\nUSER QUESTION:\nCan you give me a summary of the registered cases, specifically for Honnavar?"
            }
        ],
        "temperature": 0.0,
        "stream": False,
        "chat_template_kwargs": {
            "enable_thinking": True
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=180)
        
        if response.status_code == 200:
            data = response.json()
            if "choices" in data:
                print("\n" + "="*50)
                print("Zoho GLM 4.7 Official Output:")
                print("="*50)
                print(data["choices"][0]["message"]["content"])
        else:
            print(f"\n[HTTP ERROR] Status: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    run_video_architecture()