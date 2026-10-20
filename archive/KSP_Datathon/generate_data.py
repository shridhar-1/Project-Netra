import pandas as pd
from faker import Faker
import random
import os

fake = Faker('en_IN')
NUM_CASES = 150000

print(f"Generating {NUM_CASES} hyper-realistic KSP FIR records... Please wait.")

# ---------------------------------------------------------
# CUSTOM KARNATAKA DATA ARRAYS (The Secret Sauce)
# ---------------------------------------------------------
karnataka_first_names = [
    'Manjunath', 'Mahesh', 'Chetana', 'Mehaboob', 'Shridhar', 'Darshan', 
    'Puneeth', 'Kavya', 'Rashmi', 'Prajwal', 'Karthik', 'Lakshmi', 
    'Yash', 'Sudeep', 'Radhika', 'Basavaraj', 'Ganesh', 'Deepa'
]

karnataka_last_names = [
    'Gouda', 'Madival', 'Patil', 'Shetty', 'Bhat', 
    'Naik', 'Kulkarni', 'Hegde', 'Desai', 'Hiremath'
]

# Real District ID Mapping
real_districts = {
    1044: 'Uttara Kannada',
    2055: 'Bengaluru Urban',
    3066: 'Dakshina Kannada',
    4077: 'Mysuru'
}

# Real Police Station (Unit) ID Mapping
real_units = {
    3000: 'Honnavar Town Police Station',
    3001: 'Bhatkal Rural Police Station',
    3002: 'Murdeshwar Police Station',
    3003: 'Kumta Police Station',
    3004: 'Karwar Town Police Station',
    3005: 'Gokarna Police Station'
}

def generate_local_name():
    return f"{random.choice(karnataka_first_names)} {random.choice(karnataka_last_names)}"

def generate_local_location():
    locations = ['Bus Stand', 'Main Market', 'College Road', 'Railway Station', 'Temple Street', 'Highway Junction']
    return f"{random.choice(list(real_units.values())).replace(' Police Station', '')} {random.choice(locations)}"

# ---------------------------------------------------------
# 1. GENERATE CASEMASTER
# ---------------------------------------------------------
case_master_data = []
case_categories = [1, 3, 4, 8]
years = [2024, 2025, 2026]

for i in range(1, NUM_CASES + 1):
    category = random.choice(case_categories)
    district_id = random.choice(list(real_districts.keys()))
    unit_id = random.choice(list(real_units.keys()))
    year = random.choice(years)
    serial = f"{i:05d}"
    
    crime_no = f"{category}{district_id}{unit_id}{year}{serial}"
    case_no = f"{year}{serial}"
    start_date = fake.date_time_between(start_date='-2y', end_date='now')
    
    case_master_data.append({
        'CaseMaster ID': i,
        'CrimeNo': crime_no,
        'CaseNo': case_no,
        'CrimeRegistered Date': start_date.strftime('%Y-%m-%d'),
        'Police PersonID': random.randint(100, 500),
        'PoliceStationID': unit_id,
        'CaseCategoryID': category,
        'Gravity OffenceID': random.randint(1, 3),
        'CrimeMajor HeadID': random.randint(1, 10),
        'CrimeMinorHeadID': random.randint(1, 20),
        'CaseStatusID': random.randint(1, 5),
        'CourtID': random.randint(1, 10),
        'IncidentFromDate': start_date.strftime('%Y-%m-%d %H:%M:%S'),
        'IncidentToDate': fake.date_time_between(start_date=start_date, end_date='now').strftime('%Y-%m-%d %H:%M:%S'),
        'InfoReceivedPSDate': fake.date_time_between(start_date=start_date, end_date='now').strftime('%Y-%m-%d %H:%M:%S'),
        'latitude': round(random.uniform(14.0, 15.0), 6), 
        'longitude': round(random.uniform(74.0, 75.0), 6), 
        'BriefFacts': f"Incident reported near {generate_local_location()}."
    })

df_casemaster = pd.DataFrame(case_master_data)

# ---------------------------------------------------------
# 2. GENERATE VICTIMS, ACCUSED, AND COMPLAINANTS
# ---------------------------------------------------------
victim_data, accused_data, complainant_data, arrest_data = [], [], [], []
victim_id, accused_id, complainant_id, arrest_id = 1, 1, 1, 1

for case_id in range(1, NUM_CASES + 1):
    
    for _ in range(random.randint(1, 2)):
        victim_data.append({
            'VictimMasterID': victim_id,
            'CaseMasterID': case_id,
            'VictimName': generate_local_name(),
            'AgeYear': random.randint(5, 80),
            'GenderID': random.choice([1, 2, 3]),
            'Victim Police': random.choice([0, 1])
        })
        victim_id += 1

    for acc_idx in range(1, random.randint(2, 4)):
        accused_data.append({
            'AccusedMasterID': accused_id,
            'CaseMasterID': case_id,
            'AccusedName': generate_local_name(),
            'AgeYear': random.randint(18, 65),
            'GenderID': random.choice([1, 2, 3]),
            'PersonID': f"A{acc_idx}"
        })
        
        if random.choice([True, False]):
            arrest_data.append({
                'ArrestSurrenderID': arrest_id,
                'CaseMasterID': case_id,
                'ArrestSurrender TypeID': random.choice([1, 2]),
                'Arrest SurrenderDate': fake.date_between(start_date='-1y', end_date='today').strftime('%Y-%m-%d'),
                'ArrestSurrenderStateId': 29, 
                'ArrestSurrenderDistrictId': random.choice(list(real_districts.keys())),
                'Police StationID': random.choice(list(real_units.keys())),
                'IOID': random.randint(100, 500),
                'CourtID': random.randint(1, 10),
                'AccusedMasterID': accused_id,
                'IsAccused': 1,
                'IsComplainantAccused': 0
            })
            arrest_id += 1
        accused_id += 1

    complainant_data.append({
        'ComplainantID': complainant_id,
        'CaseMasterID': case_id,
        'ComplainantName': generate_local_name(),
        'AgeYear': random.randint(18, 70),
        'OccupationID': random.randint(1, 10),
        'ReligionID': random.randint(1, 5),
        'CasteID': random.randint(1, 15),
        'GenderID': random.choice([1, 2, 3])
    })
    complainant_id += 1

# ---------------------------------------------------------
# 3. EXPORT TO CSV
# ---------------------------------------------------------
os.makedirs("synthetic_data", exist_ok=True)
df_casemaster.to_csv("synthetic_data/CaseMaster.csv", index=False)
pd.DataFrame(victim_data).to_csv("synthetic_data/Victim.csv", index=False)
pd.DataFrame(accused_data).to_csv("synthetic_data/Accused.csv", index=False)
pd.DataFrame(complainant_data).to_csv("synthetic_data/ComplainantDetails.csv", index=False)
pd.DataFrame(arrest_data).to_csv("synthetic_data/ArrestSurrender.csv", index=False)

print("✅ SUCCESS! Authentic Karnataka CSV files generated.")