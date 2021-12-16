import os
import csv
from wootrade import Client
from datetime import datetime
import logging

# Configure the logger
logging.basicConfig(
    filename = 'tracker.log',
    filemode = 'a',
    format = '%(levelname)s %(asctime)s: %(message)s', 
    level = logging.INFO
)

# Convert UNIX timestamp into human-readable format
def strtime(timestamp_milliseconds):
    return datetime.utcfromtimestamp(int(timestamp_milliseconds)/1000).strftime('%Y-%m-%d %H:%M:%S')

API = os.getenv("WOO_API_KEY")
SECRET = os.getenv("WOO_API_SECRET")
APPLICATION_ID = os.getenv("WOO_APPLICATION_ID")

client = Client(API, SECRET, APPLICATION_ID, testnet=False)

SYMBOLS = ['SPOT_BTC_USDT', 'SPOT_ETH_USDT'] # koersen
TYPE = '1m' # stapgrootte
LIMIT = '1000' # aantal regels per requests

# De kolommen in de csv zijn de volgende:
# amount,close,end_timestamp,high,low,open,start_timestamp,volume

for symbol in SYMBOLS:
    filename = f'{symbol}_{TYPE}.csv'
    logging.info(f'Updating {filename}')
    
    # Read existing entries
    with open(filename, 'r', newline='') as fp:
        csv_reader = csv.reader(fp, delimiter=',', quotechar='"')
        rows = { row[2]: tuple(row) for row in csv_reader }

    # Add new entries
    with open(filename, 'a', newline='') as fp:
        csv_writer = csv.writer(fp, delimiter=',', quotechar='"')

        # Get the data from the API
        info = client._get('kline', True, symbol=symbol, type=TYPE, limit=LIMIT)

        # Sort the data from old to new
        json_rows = list(reversed(info['rows']))
        json_rows.sort(key=lambda json_row: json_row['end_timestamp'])
        
        # Skip the last row, as it may change
        json_rows.pop()

        already_downloaded = 0
        for json_row in json_rows:

            # Flatten the json to an ordered list
            row = tuple([
                str(json_row['amount']),
                str(json_row['close']),
                str(json_row['end_timestamp']),
                str(json_row['high']),
                str(json_row['low']),
                str(json_row['open']),
                str(json_row['start_timestamp']),
                str(json_row['volume'])
            ])

            # Check if there alreay exists a row with the same end_timestamp
            existing_row = rows.get(row[2], None)
            if existing_row is None: 
                # Write new entries to the file
                csv_writer.writerow(row)
            elif existing_row != row:                
                # This may happen if we previously downloaded entries that are modified afterwards
                logging.warning(f'Inconsistent data at end_timestamp {strtime(row[2])}')
                logging.warning(f'Old entry: {existing_row}')
                logging.warning(f'New entry: {row}')
            else:
                already_downloaded += 1

        logging.info(f'{already_downloaded} entries were already downloaded')