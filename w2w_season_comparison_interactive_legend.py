import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from bs4 import BeautifulSoup
import requests
import json
from mplsoccer import * 


headers = {
    'accept': '*/*',
    'accept-language': 'es-ES,es;q=0.9,en;q=0.8',
    'cache-control': 'no-cache',
    # 'cookie': '_gcl_au=1.1.495834952.1723458264; _lr_env_src_ats=false; _ga=GA1.1.19138556.1723458265; __qca=P0-109151881-1723458265493; FCCDCF=%5Bnull%2Cnull%2Cnull%2C%5B%22CQDPSUAQDPSUAEsACCESBBFgAAAAAEPgAA6IAAARvADyFyImkKCwPCqQRYIQAIvgAAARYBAAAwCAgACgCUgAQgEIMAAABAAAEAAAAAAQIgCQAIAABAAAAAAAAAAQAAIAAAgAAAQQEAAAAAAAACAAAAQAAAAIAABgEAACAABghCIASQAkLAAAABAAAAABQAAAAAABAAAAJCAAAIAAAAAAAAAIACAIAAAAAAAACCQAAA.YAAACAgAAAA%22%2C%222~~dv.70.89.108.149.211.313.358.415.486.540.621.981.1029.1046.1092.1097.1126.1205.1301.1516.1558.1584.1598.1651.1697.1716.1753.1810.1832.1985.2328.2373.2440.2571.2572.2575.2577.2628.2642.2677.2767.2860.2878.2887.2922.3182.3190.3234.3290.3292.3331.10631%22%2C%22AE8E1037-F7D6-407F-8D2F-988E89EC6F3E%22%5D%5D; _lr_retry_request=true; __eoi=ID=9f8537f9af01cb0d:T=1723458279:RT=1723533307:S=AA-AfjaqhVdt3IWTf-fNI4tVNXga; gcid_first=95af7183-7c4b-49d4-a3fa-39ebecbaec50; _ga_3KF4XTPHC4=GS1.1.1723530800.2.1.1723533298.58.0.0; _ga_QH2YGS7BB4=GS1.1.1723530800.2.1.1723533298.0.0.0; _ga_HNQ9P9MGZR=GS1.1.1723530801.2.1.1723533299.0.0.0',
    'pragma': 'no-cache',
    'priority': 'u=1, i',
    'referer': 'https://www.sofascore.com/es/torneo/futbol/spain/laliga-2/54',
    'sec-ch-ua': '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
    'x-requested-with': '49530f',
}

team = "Real Zaragoza"
sofascore_2324 = requests.get('https://www.sofascore.com/api/v1/unique-tournament/54/season/52563/team/2815/team-performance-graph-data', headers=headers)
sofascore_2425 = requests.get('https://www.sofascore.com/api/v1/unique-tournament/54/season/62048/team/2815/team-performance-graph-data', headers=headers)
sofascore_2223 = requests.get('https://www.sofascore.com/api/v1/unique-tournament/54/season/42410/team/2815/team-performance-graph-data', headers=headers)

columnas = ['match_id', 'week', 'position', 'tournament_name', 'homeTeam_name', 'homeScore', 'awayTeam_name',
       'awayScore']

def match_score_column(df, team, home_team, away_team, home_goals, away_goals, points):
    df[points] = df.apply(lambda row:
        3 if (row[home_team] == team and row[home_goals] > row[away_goals]) or (row[away_team] == team and row[away_goals] > row[home_goals]) else
        1 if (row[home_team] == team or row[away_team] == team) and row[home_goals] == row[away_goals] else 0,
        axis=1
    )

    df[points] = df[points].cumsum()

    return df

def extract_match_data(sofascore_data):
    """
    Extract match data from a Sofascore JSON response and return a structured DataFrame.
    
    Parameters:
        sofascore_data (requests.Response or str): The JSON response or HTML text containing the data.
        columns (list): The list of columns to retain in the final DataFrame.
    
    Returns:
        pd.DataFrame: Processed DataFrame with match details.
    """
    # Parse HTML content if it's a requests.Response object
    html = sofascore_data.text if hasattr(sofascore_data, 'text') else sofascore_data
    soup = BeautifulSoup(html, 'html.parser').text
    data = json.loads(soup).get('graphData', [])

    # Extract and flatten JSON data
    rows = []
    for item in data:
        for event in item.get('events', []):
            row = {
                'week': item.get('week'),
                'position': item.get('position'),
                'tournament_name': event.get('tournament', {}).get('name'),
                'homeTeam_name': event.get('homeTeam', {}).get('name'),
                'homeScore': event.get('homeScore', {}).get('current'),
                'awayTeam_name': event.get('awayTeam', {}).get('name'),
                'awayScore': event.get('awayScore', {}).get('current'),
                'match_id': event.get('id')
            }
            rows.append(row)

    # Convert to DataFrame
    df = pd.DataFrame(rows)

    # Assign unique week numbers
    df['week'] = range(1, len(df) + 1)

    # Retain only the specified columns
    df = df[columnas] if columnas else df

    return df

df_2223 = extract_match_data(sofascore_2223)
match_score_column(df_2223, "Real Zaragoza", "homeTeam_name", "awayTeam_name", "homeScore", "awayScore", "points")

df_2324 = extract_match_data(sofascore_2324)
match_score_column(df_2324, "Real Zaragoza", "homeTeam_name", "awayTeam_name", "homeScore", "awayScore", "points")

df_2425 = extract_match_data(sofascore_2425)
match_score_column(df_2425, "Real Zaragoza", "homeTeam_name", "awayTeam_name", "homeScore", "awayScore", "points")



# Create the fig and the axis
fig, ax = plt.subplots(figsize=(12, 8))

# Create lineplots for each season
sns.lineplot(data=df_2223, x='week', y='position', marker='o', color='#E9B111', label='22/23')
sns.lineplot(data=df_2324, x='week', y='position', marker='o', color='#2086E5', label='23/24')
sns.lineplot(data=df_2425, x='week', y='position', marker='o', color='#FFFFFF', label='24/25')

# Config the axis ticks to match the matchweeks and positions
plt.yticks(ticks=range(1, 23, 1))
plt.gca().invert_yaxis()

plt.xticks(ticks=range(0, 43, 1))
plt.xlim(1, 42)

# Title & labels
plt.xlabel('Week', color='white')
plt.ylabel('Position', color='white')
plt.title('Real Zaragoza Liga Hypermotion W2W Performance', color='white')
plt.grid(color='#dfccae', linestyle='--', axis='y', alpha=.5)

ax.set_facecolor('#04182B')
fig.patch.set_facecolor('#04182B')

ax.tick_params(axis='x', colors='white', direction='out', length=5, width=2)
ax.tick_params(axis='y', colors='white', direction='in', length=5, width=2)

plt.subplots_adjust(right=0.15)

# Add legend
legend = plt.legend(loc='upper right', frameon=True, title='Season', facecolor='#AAABAC')

# Get the graph lines generated by seaborn
lines = ax.get_lines()

# Create a dict for the legend elements and the graph lines
lined = {legline: line for legline, line in zip(legend.get_lines(), lines)}

# Function to interact with the legend items
def on_pick(event):
    legend_item = event.artist  # Picked legend element
    if legend_item in lined:
        line = lined[legend_item]
        line.set_visible(not line.get_visible())  # Set visibility 
        plt.draw() 

# Enable Legend selection
for legline in legend.get_lines():
    legline.set_picker(6)  # Set the pixels for the click interaction

# Connect created function with selection event
fig.canvas.mpl_connect("pick_event", on_pick)

# Show graph
plt.tight_layout()
plt.show()