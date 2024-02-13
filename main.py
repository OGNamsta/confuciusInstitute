import asyncio
import httpx
from time import perf_counter
import json
import os
import logging

logging.basicConfig(filename='app.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


async def log_request(request):
    logging.info(f"Request:  {request.url!r} {request.method!r}")


async def log_response(response):
    logging.info(f"Response: {response.url!r} {response.status_code!r}")


# A function that creates a json cache per labelkey
def create_cache_json(data, label):
    cache_path = 'Caches'
    cache_file = os.path.join(cache_path, f'{label}.json').replace('\\', '/')
    if not os.path.exists(cache_path):
        try:
            logging.info(f"Creating {cache_path} directory...")
            os.makedirs(cache_path)
            logging.info(f"{cache_path} directory created")
        except Exception as e:
            logging.error(f"Error creating {cache_path} directory: {e}")
            return None

    try:
        with open(cache_file, 'w') as f:
            logging.info(f"Creating {label}.json cache...")
            json.dump(data, f)
            logging.info(f"{label}.json cache created")
    except Exception as e:
        logging.error(f"Error creating {label}.json cache: {e}")
        return None


# A function that reads the cache
async def read_cache_file(label):
    cache_path = 'Caches'
    cache_file = os.path.join(cache_path, f'{label}.json').replace('\\', '/')

    logging.info(f"Checking cache file: {cache_file}")

    if not os.path.exists(cache_path):
        logging.info(f"Creating {cache_path} directory...")
        try:
            os.makedirs(cache_path)
            logging.info(f"{cache_path} directory created")
        except Exception as e:
            logging.error(f"Error creating {cache_path} directory: {e}")
            return None

    if os.path.exists(cache_file):
        try:
            logging.info(f"Reading existing {label}.json cache...")
            with open(cache_file, 'r') as f:
                json_data = json.load(f)
                logging.info(f"{label}.json cache loaded")
                return json_data
        except Exception as e:
            logging.error(f"Error reading {label}.json cache: {e}")
            return None
    else:
        logging.info(f"No cache found for {label}")
        return None


# A function that reads the labelkey file
async def read_label_files(labelkey):
    label_path = 'Labelkeys'
    label_file = os.path.join(label_path, f'{labelkey}.txt').replace('\\', '/')

    logging.info(f"Checking labelkey file: {label_file}")

    if not os.path.exists(label_path):
        try:
            logging.info(f"Creating {label_path} directory...")
            os.makedirs(label_path)
            logging.info(f"{label_path} directory created")
        except Exception as e:
            logging.error(f"Error creating {label_path} directory: {e}")
            return None

    if os.path.exists(label_file):
        try:
            logging.info(f"Reading existing {labelkey}.txt file...")
            with open(label_path, 'r') as f:
                label_contents = f.read().splitlines()
                logging.info(f"{labelkey}.txt file loaded")
                return label_contents
        except Exception as e:
            logging.error(f"Error reading {labelkey}.txt file: {e}")
            return None
    else:
        logging.info(f"No labelkey file found for {labelkey}")
        return None


async def create_label_file(label, countries):
    label_path = 'Labelkeys'
    label_file = os.path.join(label_path, f'{label}.txt').replace('\\', '/')

    # Check if the labelkey directory exists
    if not os.path.exists(label_path):
        try:
            logging.info(f"Creating {label_path} directory...")
            os.makedirs(label_path)
            logging.info(f"{label_path} directory created")
        except Exception as e:
            logging.error(f"Error creating {label_path} directory: {e}")
            return None

    # Check if the labelkey file exists. If it does not, create it and write the countries to it
    if not os.path.exists(label_file):
        try:
            logging.info(f"Creating {label}.txt file...")
            with open(label_file, 'w') as f:
                for country in countries:
                    f.write(f"{country}\n")
            logging.info(f"{label}.txt file created")
        except Exception as e:
            logging.error(f"Error creating {label}.txt file: {e}")
            return None

    # Check if the labelkey file exists. If it does, read the contents and append the new labelKeys to the file if there are any
    if os.path.exists(label_file):
        try:
            logging.info(f"Reading existing {label}.txt file...")
            # Read the contents
            with open(label_file, 'r') as f:
                label_contents = f.read().splitlines()  # Split the contents into a list

            # Find the new labelKeys if there are any
            new_label_keys = [labelKey for labelKey in countries if labelKey not in label_contents]

            if new_label_keys:
                # Append the new labelKeys to the file
                with open(label_file, 'a') as f:  # Open the file in append mode
                    for labelKey in new_label_keys:
                        f.write(f"{labelKey}\n")
                logging.info(f"Updated {label}.txt with {len(new_label_keys)} new labelKeys")
            else:
                logging.info(f"{label}.txt is already up to date")
        except Exception as e:
            logging.error(f"Error updating {label}.txt file: {e}")
            return None
    else:
        logging.info(f"No labelkey file found for {label}")
        return None


async def get_countries(label):
    url = 'https://ci.cn/open/label/labelsByKey'
    cookies = {
        '__jsluid_s': '1145a9b931be40a97b586abe3635f9ca',
        'cvid': '1707387773653_752',
        'enable': '1',
    }

    headers = {
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.9,en-GB;q=0.8,de;q=0.7,es;q=0.6',
        'Connection': 'keep-alive',
        # 'Cookie': '__jsluid_s=1145a9b931be40a97b586abe3635f9ca',
        'DNT': '1',
        'Referer': 'https://ci.cn/en/qqwl/qqky',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
        'sec-ch-ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }

    params = {
        'labelKey': str(label),
        'language': 'EN',
    }
    try:
        async with httpx.AsyncClient(event_hooks={'request': [log_request], 'response': [log_response]}, headers=headers, params=params, cookies=cookies) as client:
            response = await client.get(url)
            data = response.json()
            return data
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    except httpx.HTTPStatusError as e:
        print(f"An HTTP error occurred: {e}")
        return None
    except httpx.RequestError as e:
        print(f"A request error occurred: {e}")
        return None


async def get_country_data(labelid):
    url = 'https://ci.cn/open/site-tab/sitesByLabelIdAndSiteName'

    cookies = {
        '__jsluid_s': '1145a9b931be40a97b586abe3635f9ca',
        'enable': '1',
    }

    headers = {
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.9,en-GB;q=0.8,de;q=0.7,es;q=0.6',
        'Connection': 'keep-alive',
        # 'Cookie': '__jsluid_s=1145a9b931be40a97b586abe3635f9ca; enable=1',
        'DNT': '1',
        'Referer': 'https://ci.cn/en/qqwl/qqky',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
        'sec-ch-ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }

    params = {
        'labelId': str(labelid),
        'siteName': '',
        'language': 'EN',
    }

    try:
        async with httpx.AsyncClient(event_hooks={'request': [log_request], 'response': [log_response]}, headers=headers, params=params, cookies=cookies) as client:
            response = await client.get(url)
            country_data = response.json()
            return country_data
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    except httpx.HTTPStatusError as e:
        print(f"An HTTP error occurred: {e}")
        return None
    except httpx.RequestError as e:
        print(f"A request error occurred: {e}")
        return None


async def main():
    start_time = perf_counter()
    labels = ['C-Africa', 'C-Asia', 'C-Europe', 'C-America', 'C-Oceania']

    # Start looping through the labels
    for label in labels:
        logging.info(f"Processing labelkey: {label}")
        countries = []

        # Run the read_cache_file function to check if the cache exists
        json_data = await read_cache_file(label)

        # If the cache exists, use the cache
        if json_data:
            logging.info(f"Using cached data for {label}")
        else:
            logging.info(f"Fetching live data for {label}")
            json_data = await get_countries(label)
            logging.info(f"Caching live data for {label}...")
            create_cache_json(json_data, label)

        # Load the labelKey into the countries list
        countries = [item['labelKey'] for item in json_data['data']]

        # Run the create_label_file function to create the labelkey file
        await create_label_file(label, countries)
        logging.info(f"Created {label}.txt with {len(countries)} countries")

        # Open the labelkey files and read the contents
        label_id_data = await read_label_files(label)

        # Loop through the label_id_data and get the country data
        for label_id in label_id_data:
            logging.info(f"Fetching country data for {label_id}...")
            country_data = await get_country_data(label_id)
            logging.info(f"Caching country data for {label_id}...")
            create_cache_json(country_data, label_id)
            logging.info(f"Done caching country data for {label_id}")


    end_time = perf_counter()
    logging.info(f"Time taken: {end_time - start_time:.2f} seconds")
    print(f"Time taken: {end_time - start_time:.2f} seconds")
    logging.info("Done")
    print("Done")


if __name__ == '__main__':
    asyncio.run(main())
