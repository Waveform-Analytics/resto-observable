# Prepare the annual measles data. Extract data 1985-Present.
# This data loader exports a dataframe with year and cases, both stored as numbers

# import pandas as pd
# import sys
# import numpy as np

# # Read the CSV
# df = pd.read_csv("src/data/measles-cases.csv")

# df_filtered = df.loc[df['filter'] == "1985-Present*"]

# df_filtered['era'] = np.where(df_filtered['year'] <= 2009, "part1", "part2")

# df_output = df_filtered[['year', 'cases', 'era']]

# # Write to CSV
# df_output.to_csv(sys.stdout, index=False)

from resto import get_data

df = get_data(
    'users',
    clerk_secret_key=None,
    supabase_url=None,
    supabase_key=None
)

print(df)