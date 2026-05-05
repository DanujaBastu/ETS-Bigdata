import json

# Read file
with open('dashboard/data/spark_results.json', 'r') as f:
    content = f.read()

# Replace NaN dengan null
content = content.replace('NaN', 'null')
content = content.replace('Infinity', 'null')

# Parse dan re-save
data = json.loads(content)
with open('dashboard/data/spark_results.json', 'w') as f:
    json.dump(data, f, indent=2)
print('JSON fixed! NaN replaced with null')
