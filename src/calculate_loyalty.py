import pandas as pd

# Load data
df = pd.read_csv('data/october_data.csv', parse_dates=['timestamp'])

# Add date and slot columns
df['date'] = df['timestamp'].dt.date
df['slot'] = df['timestamp'].apply(lambda x: 'S1' if x.hour < 12 else 'S2')

# Loyalty point formula function
def calculate_loyalty(row):
    return (
        0.01 * row['deposit_amount'] +
        0.005 * row['withdrawal_amount'] +
        0.001 * max(row['num_deposit'] - row['num_withdrawal'], 0) +
        0.2 * row['games_played']
    )

# Apply formula to each row
df['loyalty_points'] = df.apply(calculate_loyalty, axis=1)

# --- PART A: Specific Slot Calculations ---
def get_slot_loyalty(date_str, slot):
    date = pd.to_datetime(date_str).date()
    filtered = df[(df['date'] == date) & (df['slot'] == slot)]
    result = filtered.groupby('player_id').agg({
        'deposit_amount': 'sum',
        'withdrawal_amount': 'sum',
        'num_deposit': 'sum',
        'num_withdrawal': 'sum',
        'games_played': 'sum',
        'loyalty_points': 'sum'
    }).reset_index()
    result['date'] = date
    result['slot'] = slot
    return result

# Example slots:
slots_to_check = [
    ("2023-10-02", "S1"),
    ("2023-10-16", "S2"),
    ("2023-10-18", "S1"),
    ("2023-10-26", "S2")
]

slot_results = pd.concat([get_slot_loyalty(date, slot) for date, slot in slots_to_check])
print("---- Loyalty Points by Slot ----")
print(slot_results)

# --- PART A: Monthly Ranking ---
monthly = df.groupby('player_id').agg({
    'deposit_amount': 'sum',
    'withdrawal_amount': 'sum',
    'num_deposit': 'sum',
    'num_withdrawal': 'sum',
    'games_played': 'sum',
    'loyalty_points': 'sum'
}).reset_index()

monthly['rank'] = monthly.sort_values(
    ['loyalty_points', 'games_played'],
    ascending=[False, False]
).reset_index(drop=True).index + 1

print("\n---- Monthly Ranking ----")
print(monthly.sort_values('rank'))

# --- PART A: Averages ---
avg_deposit = df['deposit_amount'].mean()
avg_deposit_per_user = df.groupby('player_id')['deposit_amount'].sum().mean()
avg_games_per_user = df.groupby('player_id')['games_played'].sum().mean()

print("\nAverage Deposit Amount:", round(avg_deposit, 2))
print("Average Deposit per User:", round(avg_deposit_per_user, 2))
print("Average Games per User:", round(avg_games_per_user, 2))

# --- PART B: Bonus Allocation ---
bonus_pool = 500000  # Rs 5 lakhs
top_50 = monthly.sort_values(['loyalty_points', 'games_played'], ascending=False).head(50)
total_loyalty_top50 = top_50['loyalty_points'].sum()

top_50['bonus_amount'] = top_50['loyalty_points'] / total_loyalty_top50 * bonus_pool

print("\n---- Bonus Allocation (Top 50) ----")
print(top_50[['player_id', 'loyalty_points', 'bonus_amount']])


# Create output folder if it doesn't exist
import os
os.makedirs('output', exist_ok=True)

# Export results
slot_results.to_csv('output/slotwise_loyalty_points.csv', index=False)
monthly.to_csv('output/monthly_ranking.csv', index=False)
top_50.to_csv('output/bonus_distribution.csv', index=False)

# Optional: Export to Excel
with pd.ExcelWriter('output/abc_loyalty_outputs.xlsx') as writer:
    slot_results.to_excel(writer, sheet_name='Slotwise Points', index=False)
    monthly.to_excel(writer, sheet_name='Monthly Ranking', index=False)
    top_50.to_excel(writer, sheet_name='Bonus Distribution', index=False)

print("\n✅ All results exported to /output folder.")