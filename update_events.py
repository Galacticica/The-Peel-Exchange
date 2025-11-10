import json
import random

# Read the existing events
with open('market/fixtures/market_events.json', 'r') as f:
    events = json.load(f)

# Update impact values with variation
for event in events:
    level = event['fields']['impact_level']
    
    if level == 'minor':
        # 15-25% range with variation
        base = random.uniform(0.15, 0.25)
        spread = random.uniform(0.04, 0.07)
        low = round(base - spread/2, 2)
        high = round(base + spread/2, 2)
        
    elif level == 'moderate':
        # 25-40% range with variation
        base = random.uniform(0.25, 0.40)
        spread = random.uniform(0.08, 0.12)
        low = round(base - spread/2, 2)
        high = round(base + spread/2, 2)
        
    elif level == 'major':
        # 40-60% range with variation
        base = random.uniform(0.40, 0.60)
        spread = random.uniform(0.12, 0.18)
        low = round(base - spread/2, 2)
        high = round(base + spread/2, 2)
        
    elif level == 'severe':
        # 60-90% range with variation (capped to prevent stocks going negative)
        base = random.uniform(0.60, 0.90)
        spread = random.uniform(0.15, 0.25)
        low = round(base - spread/2, 2)
        high = round(base + spread/2, 2)
        # Cap at 95% to be safe
        if high > 0.95:
            high = 0.95
        if low > 0.90:
            low = 0.90
    
    # Keep negative events negative
    if event['fields']['impact_low'] < 0:
        event['fields']['impact_low'] = -abs(high)
        event['fields']['impact_high'] = -abs(low)
    else:
        event['fields']['impact_low'] = low
        event['fields']['impact_high'] = high

# Write back
with open('market/fixtures/market_events.json', 'w') as f:
    json.dump(events, f, indent=2)

print("Updated all market events with new impact ranges!")
print("\nSummary:")
print("Minor: 15-25%")
print("Moderate: 25-40%")
print("Major: 40-60%")
print("Severe: 60-95% (capped to prevent negative prices)")
