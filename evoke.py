from time import sleep
import requests
import csv
import json
import sys
import os

# get token from arguments or environment variable or input
token = sys.argv[1] if len(sys.argv) > 1 else os.getenv('SNAPP_TOKEN') or input('Enter your Snapp token: ')

# Authorization token
token = 'Bearer ' + token

# Open CSV file for writing
with open('rides_data.csv', 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    # Write the header
    writer.writerow([
        'index', 'is_delivery', 'latest_ride_status', 'title', 'human_readable_id',
        'origin_lat', 'origin_lng', 'destination_lat', 'destination_lng',
        'service_type', 'type', 'created_at', 'updated_at',
        'driver_name', 'vehicle_model', 'is_for_friend', 'final_price'
    ])

    response = requests.get(
        f'https://app.snapp.taxi/api/api-base/v2/passenger/ride/history?page=1',
        headers={"authorization": token}
    )
    total = response.json()['data']['successful_snapp_rides']

    index = 0
    page = 1
    max_retries = 3

    while True:
        try:
            # Fetch ride history data with retry mechanism
            for attempt in range(max_retries):
                try:
                    response = requests.get(
                        f'https://app.snapp.taxi/api/api-base/v2/passenger/ride/history?page={page}',
                        headers={"authorization": token}
                    )
                    rides = response.json()['data']['rides']
                    break  # Exit the retry loop if the request is successful
                except Exception as e:
                    if attempt < max_retries - 1:
                        print(f"Attempt {attempt + 1} failed: {e}. Retrying...")
                        print('response from snapp:')
                        print(json.dumps(response.json(), indent=4))
                        sleep(1)
                    else:
                        print(f"Attempt {attempt + 1} failed: {e}. Moving to next page.")
                        rides = []

            # Break the loop if no more rides are found
            if not rides:
                print('No more rides. Finished.')
                break

            # Increment page for the next request
            page += 1

            # Process each ride
            for ride in rides:
                row = [
                    index,
                    ride.get('is_delivery', ''),
                    ride.get('latest_ride_status', ''),
                    ride.get('title', ''),
                    ride.get('human_readable_id', ''),
                    ride.get('origin', {}).get('lat', ''),
                    ride.get('origin', {}).get('lng', ''),
                    ride.get('destination', {}).get('lat', ''),
                    ride.get('destination', {}).get('lng', ''),
                    ride.get('service_type', {}).get('name', ''),
                    ride.get('service_type', {}).get('type', ''),
                    ride.get('created_at', ''),
                    ride.get('updated_at', ''),
                    ride.get('driver_name', ''),
                    ride.get('vehicle_model', ''),
                    ride.get('is_for_friend', ''),
                    ride.get('final_price', '')
                ]
                index += 1
                writer.writerow(row)
                print(f"Processed ride {index} of {total} : {ride.get('human_readable_id')}")

        except Exception as e:
            print(f"An error occurred: {e}")
            print('response from snapp:')
            print(json.dumps(response.json(), indent=4))
            print('Retrying in 1 second...')
            sleep(1)
