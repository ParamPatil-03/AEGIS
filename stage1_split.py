import pandas as pd
import numpy as np

# Load data
df = pd.read_csv('data/processed/model_ready_data.csv')
df['timestamp'] = pd.to_datetime(df['timestamp'])
df = df.sort_values('timestamp').reset_index(drop=True)

# Identify blocks (gaps > 1 hour)
# Calculate time difference between consecutive rows
time_diff = df['timestamp'].diff()
# A new block starts when the difference is greater than 1 hour
# Since we have hourly data, any diff > 1 hour (e.g., 2 hours) is a gap
is_new_block = time_diff > pd.Timedelta(hours=1.1) 
# Create block IDs
df['block_id'] = is_new_block.cumsum()

blocks = df.groupby('block_id').agg(
    start_time=('timestamp', 'min'),
    end_time=('timestamp', 'max'),
    row_count=('timestamp', 'count')
).reset_index()

total_rows = len(df)
target_train_rows = int(0.8 * total_rows)

# Identify the storm window
storm_start = pd.to_datetime('2023-03-17')
storm_end = pd.to_datetime('2023-04-30 23:59:59')

train_blocks = []
test_blocks = []
current_train_rows = 0

storm_in_data = False
storm_blocks = []

for _, row in blocks.iterrows():
    # Check if block overlaps with storm window
    overlaps_storm = (row['start_time'] <= storm_end) and (row['end_time'] >= storm_start)
    if overlaps_storm:
        storm_in_data = True
        storm_blocks.append(row['block_id'])

# Strategy: chronologically add blocks to train, but skip storm blocks.
for _, row in blocks.iterrows():
    block_id = row['block_id']
    if block_id in storm_blocks:
        test_blocks.append(block_id)
    elif current_train_rows < target_train_rows:
        train_blocks.append(block_id)
        current_train_rows += row['row_count']
    else:
        test_blocks.append(block_id)

train_df = df[df['block_id'].isin(train_blocks)]
test_df = df[df['block_id'].isin(test_blocks)]

print(f"Total Rows: {total_rows}")
print(f"Total Blocks: {len(blocks)}")
print("-" * 30)
print(f"Train Blocks: {len(train_blocks)}")
print(f"Train Rows: {len(train_df)} ({len(train_df)/total_rows*100:.1f}%)")
print(f"Test Blocks: {len(test_blocks)}")
print(f"Test Rows: {len(test_df)} ({len(test_df)/total_rows*100:.1f}%)")
print("-" * 30)
if storm_in_data:
    print("March 17 - April 30, 2023 window is PRESENT in the data.")
    # Verify it is in test
    storm_in_test = all(b in test_blocks for b in storm_blocks)
    if storm_in_test:
        print("SUCCESS: The entire storm window is in the test set.")
    else:
        print("WARNING: Some storm blocks ended up in train set!")
else:
    print("March 17 - April 30, 2023 window is NOT present in the data.")

# Save splits
train_df.to_csv('data/processed/train_data.csv', index=False)
test_df.to_csv('data/processed/test_data.csv', index=False)
print("Saved train_data.csv and test_data.csv to data/processed/")
