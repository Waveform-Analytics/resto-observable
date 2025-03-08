# Load and prepare the restaurant week data

from resto import get_data
import json
import sys

all_data = get_data(['users', 'visits', 'restaurants'])

# Write the python dictionary all_data to json using sys.stdout
json.dump(all_data, sys.stdout, indent=2)
 