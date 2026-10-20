import pandas as pd
import random
import time
import os
import re

# ---------------- HELPERS ----------------
def clean_text(text):
    """Force text onto ONE line so CSV/Excel never truncates it."""
    text = str(text).replace('\r', ' ').replace('\n', ' ').replace('\t', ' ')
    return re.sub(r'\s+', ' ', text).strip()

def find_col(headers, candidates):
    """Case/space-insensitive column finder. Returns the real column name or None."""
    norm = {str(h).strip().lower(): h for h in headers}
    for c in candidates:
        if c.strip().lower() in norm:
            return norm[c.strip().lower()]
    return None

# ---------------- STORY ENGINE ----------------
def get_crime_story(crime_name, taluk, accused):
    crime = str(crime_name).lower()

    if any(x in crime for x in ['murder', 'homicide', 'kill', '302']):
        stories = [
            f"A violent altercation broke out late at night near the {taluk} main circle. {accused} allegedly attacked the victim with a machete following a long-standing property dispute. The victim bled heavily and succumbed to injuries before reaching the hospital. The weapon was recovered from a nearby bush.",
            f"The control room received a panicked call from a resident in {taluk} reporting a foul smell. Upon breaking open the locked doors of an isolated house, officers discovered the victim's body. Forensics indicate death by asphyxiation. Neighbors reported seeing {accused} leaving the premises two nights prior."
        ]
    elif any(x in crime for x in ['theft', 'burglar', 'dacoit', 'robber', 'snatch', 'house break', 'housebreak', 'steal']):
        stories = [
            f"The complainant locked their residence in {taluk} to attend a family wedding. Taking advantage of the empty house, {accused} broke the rear window grill, deactivated the CCTV, and looted 150 grams of gold jewelry and Rs. 50,000 in cash from the bedroom locker.",
            f"While the victim was walking towards the {taluk} bus stand, a speeding motorcycle without a number plate approached them. {accused} snatched the victim's gold chain and mobile phone, pushing them to the ground, before speeding away towards the highway.",
            f"Miscreants struck a provision store in {taluk} bazaar after midnight. {accused} was captured on a nearby CCTV carrying away the cash drawer and valuables. Fingerprints were lifted from the broken shutter."
        ]
    elif any(x in crime for x in ['cyber', 'fraud', 'cheat', 'forger', 'breach of trust', 'impersonat', 'online']):
        stories = [
            f"The complainant, a retired teacher from {taluk}, received a WhatsApp call from someone posing as a bank manager. Under the pretext of updating KYC details, {accused} convinced the victim to share an OTP. Within minutes, Rs. 2.5 Lakhs were siphoned off from the victim's savings account.",
            f"{accused} created a fake e-commerce website offering heavy discounts on electronics. The victim, residing in {taluk}, transferred Rs. 45,000 for a laptop. The website vanished the next day and the contact numbers were switched off."
        ]
    elif any(x in crime for x in ['assault', 'riot', 'hurt', 'injur', 'affray', 'grievous', 'unlawful assembly']):
        stories = [
            f"During a local festival in {taluk}, a minor argument over parking escalated into a brawl. A mob led by {accused} started throwing stones and vandalizing public property. Three individuals sustained severe head injuries and were rushed to the district hospital.",
            f"The victim was confronted by {accused} near the {taluk} market area. The verbal abuse turned physical when {accused} used a heavy wooden stick to assault the victim, causing multiple fractures."
        ]
    elif any(x in crime for x in ['ndps', 'narcotic', 'drug', 'ganja', 'excise', 'liquor', 'prohibition']):
        stories = [
            f"Acting on a credible tip-off, the {taluk} police intercepted a suspicious transport vehicle. During the search, officers discovered 15 kilograms of illegal contraband (suspected Ganja) hidden beneath crates of vegetables. {accused} was detained on the spot.",
            f"A late-night raid was conducted at an abandoned warehouse on the outskirts of {taluk}. Police busted an illegal liquor distribution ring. {accused} was caught red-handed loading illicit crates into a delivery van."
        ]
    elif any(x in crime for x in ['rape', 'sexual', 'molest', 'pocso', 'outrag', 'modesty']):
        stories = [
            f"The survivor lodged a complaint at the {taluk} women's help desk alleging that {accused} committed the offence near an isolated stretch outside town. A medical examination was conducted, the scene secured, and the accused booked under relevant sections of law."
        ]
    elif any(x in crime for x in ['kidnap', 'abduct', 'missing']):
        stories = [
            f"The complainant reported that their son left home in {taluk} for tuition and never returned. CCTV footage showed him entering a white car in which {accused} was seated. A manhunt has been launched across district borders."
        ]
    elif any(x in crime for x in ['accident', 'rash', 'neglig', 'hit and run']):
        stories = [
            f"A speeding SUV driven by {accused} rammed into a two-wheeler near the {taluk} highway junction, seriously injuring the rider. The vehicle was traced through its registration number captured on a toll plaza camera."
        ]
    elif any(x in crime for x in ['dowry', 'cruelty', 'domestic', '498']):
        stories = [
            f"The complainant from {taluk} alleged continuous harassment by her husband {accused} and in-laws demanding additional dowry of Rs. 5 Lakhs. Neighbours corroborated frequent quarrels. Investigation is in progress."
        ]
    else:
        # Generic BUT still names the real offence
        stories = [
            f"A formal FIR was registered at the {taluk} police station for the offence recorded as '{crime_name}'. The complainant alleged that {accused} intentionally committed the act, causing loss and distress. The investigating officer secured the scene and witness statements are being recorded.",
            f"Officers from {taluk} station responded to a complaint classified under '{crime_name}'. {accused} was identified as the prime suspect based on preliminary evidence. Surveillance footage and call records are being collected."
        ]
    return random.choice(stories)

# ---------------- MAIN ----------------
def generate_story_mode_cases():
    print("🚀 Initializing Project Netra - AI Story Mode Generator...")
    start_time = time.time()

    input_file  = 'casemasters_20k_TextType.csv'
    unit_file   = 'Unit_2.csv' if os.path.exists('Unit_2.csv') else 'Unit.csv'
    crime_file  = 'CrimeHead.csv'
    output_file = 'casemasters_20k_UttaraKannada_Exclusive.csv'

    uk_gps = {
        'Honnavar': {'lat': 14.2798, 'lon': 74.4439}, 'Karwar':   {'lat': 14.8045, 'lon': 74.1322},
        'Ankola':   {'lat': 14.6655, 'lon': 74.3001}, 'Kumta':    {'lat': 14.4216, 'lon': 74.4172},
        'Bhatkal':  {'lat': 13.9749, 'lon': 74.5606}, 'Sirsi':    {'lat': 14.6195, 'lon': 74.8354},
        'Siddapur': {'lat': 14.3352, 'lon': 74.8924}, 'Yellapur': {'lat': 14.9643, 'lon': 74.7121},
        'Mundgod':  {'lat': 14.9666, 'lon': 75.0378}, 'Haliyal':  {'lat': 15.3340, 'lon': 74.7592},
        'Joida':    {'lat': 15.1667, 'lon': 74.4833}, 'Dandeli':  {'lat': 15.2415, 'lon': 74.6186}
    }
    other_taluks_list = [t for t in uk_gps if t != 'Honnavar']
    names = ["Suresh Desai", "Vinay Shetty", "Karthik Hiremath", "Darshan Desai",
             "Pradeep Shetty", "Ravi Naik", "Manjunath Bhat", "Prakash Gouda", "Abdul Majeed"]

    try:
        # 1. CRIME HEAD MAP — dtype-proof (int-normalized keys)
        print(f"   ... Reading {crime_file}")
        crime_df = pd.read_csv(crime_file)
        id_col   = find_col(crime_df.columns, ['CrimeHeadID'])
        name_col = find_col(crime_df.columns, ['CrimeGroupName', 'CrimeHeadName', 'CrimeName'])
        crime_mapping = {}
        for _, r in crime_df.iterrows():
            try:
                crime_mapping[int(float(r[id_col]))] = str(r[name_col]).strip()
            except (ValueError, TypeError):
                continue
        print(f"   ... Loaded {len(crime_mapping)} crime head names.")

        # 2. UNITS — tolerant taluk matching
        print(f"   ... Reading {unit_file}")
        units_df = pd.read_csv(unit_file)
        u_taluk = find_col(units_df.columns, ['Taluk', 'Taluka', 'TalukName'])
        u_id    = find_col(units_df.columns, ['UnitID', 'PoliceStationID'])
        units_df['_t'] = units_df[u_taluk].astype(str).str.strip().str.lower()
        taluk_to_units = {}
        for taluk in uk_gps:
            ids = units_df.loc[units_df['_t'] == taluk.lower(), u_id].tolist()
            if ids:
                taluk_to_units[taluk] = ids
        if 'Honnavar' not in taluk_to_units:
            raise ValueError(f"No UnitIDs found for Honnavar! Taluks found in unit file: {sorted(units_df['_t'].unique())}")
        valid_others = [t for t in other_taluks_list if t in taluk_to_units] or ['Honnavar']

        # 3. CASEMASTERS — robust column detection, hard error instead of silent skip
        print(f"   ... Loading {input_file}")
        df_original = pd.read_csv(input_file)
        headers   = df_original.columns.tolist()
        unit_col  = find_col(headers, ['PoliceStationID', 'UnitID'])
        lat_col   = find_col(headers, ['latitude', 'lat'])
        lon_col   = find_col(headers, ['longitude', 'lon', 'lng'])
        bf_col    = find_col(headers, ['BriefFacts', 'Brief_Facts', 'Facts'])
        crime_col = find_col(headers, ['CrimeMajorHeadID', 'CrimeHeadID', 'CrimeMajorHeadId', 'MajorHeadID'])
        if bf_col is None:
            raise KeyError(f"BriefFacts column not found. Columns: {headers}")
        if crime_col is None:
            raise KeyError(f"Crime head column not found. Columns: {headers}")
        print(f"   ... Crime column = '{crime_col}' | Story column = '{bf_col}'")

        df_new = df_original.sample(n=20000, replace=True).copy().reset_index(drop=True)

        print("   ... Writing 20,000 FIR stories...")
        mapped, generic = 0, 0
        for i in range(20000):
            taluk = 'Honnavar' if random.random() < 0.65 else random.choice(valid_others)

            if unit_col: df_new.at[i, unit_col] = random.choice(taluk_to_units[taluk])
            if lat_col:  df_new.at[i, lat_col]  = round(uk_gps[taluk]['lat'] + random.uniform(-0.02, 0.02), 5)
            if lon_col:  df_new.at[i, lon_col]  = round(uk_gps[taluk]['lon'] + random.uniform(-0.02, 0.02), 5)

            # dtype-proof lookup
            try:
                key = int(float(df_new.at[i, crime_col]))
            except (ValueError, TypeError):
                key = None
            actual_crime_name = crime_mapping.get(key)
            if actual_crime_name:
                mapped += 1
            else:
                actual_crime_name, generic = "General Offence", generic + 1

            accused_str = ", ".join(random.sample(names, k=random.randint(1, 3)))
            story = get_crime_story(actual_crime_name, taluk, accused_str)

            # ✅ THE FIX: single-line text, pipe separators — never truncates
            df_new.at[i, bf_col] = clean_text(
                f"**District:** Uttara Kannada | **Taluk:** {taluk} | "
                f"**Crime Type:** {actual_crime_name} | **Accused:** {accused_str} | "
                f"**Incident Report:** {story}"
            )

        print(f"   ... Crime match rate: {mapped} mapped ✅ | {generic} generic ⚠️")
        if mapped == 0:
            print("   ⚠️ WARNING: 0 matches! CrimeMajorHeadID values don't exist in CrimeHead.csv — check the ID ranges in both files.")

        # 4. PRIMARY KEYS
        if 'CaseMasterID' in df_new.columns:
            mx = pd.to_numeric(df_original['CaseMasterID'], errors='coerce').max()
            start_id = int(mx) + 1 if pd.notna(mx) else 1
            df_new['CaseMasterID'] = range(start_id, start_id + 20000)
        if 'CaseNo' in df_new.columns:
            mx = pd.to_numeric(df_original['CaseNo'], errors='coerce').max()
            start_no = int(mx) + 1 if pd.notna(mx) else 202600001
            df_new['CaseNo'] = range(start_no, start_no + 20000)
        if 'Year' in df_new.columns:
            df_new['Year'] = 2026

        df_new.to_csv(output_file, index=False, encoding='utf-8-sig')

        # 5. VERIFY — read back and print an actual written story
        verify = pd.read_csv(output_file, nrows=3)
        print("\n🔎 Sample BriefFacts actually written to file:")
        print(verify[bf_col].iloc[0])

        print(f"\n✅ Done in {round(time.time() - start_time, 2)}s → {output_file}")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    generate_story_mode_cases()