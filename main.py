import csv
from time import sleep
import requests
import string
import sys
import SECRETS

api_key = SECRETS.api_key
input_file = "locations.csv"
output_file = "locations_new.csv"

def sanitize_address(address):
    '''Sanitize the address string and remove punctuations, etc.'''
    symbols = string.punctuation + string.whitespace
    translation_table = str.maketrans(symbols, "_" * len(symbols))
    return address.translate(translation_table)

def convert_addresses_to_gps(input_file, output_file, api_key):
    '''The input should be called "locations.csv", and have exactly two columns in this order (name doesn't matter): identifier and address'''
    with open(input_file, 'r', encoding='utf-8') as infile, \
         open(output_file, 'w', newline='', encoding='utf-8') as outfile:
        
        reader = csv.reader(infile)
        writer = csv.writer(outfile)

        # Read and validate headers
        headers = next(reader)
        if len(headers) != 2:
            print(f"Error: The input file '{input_file}' does not have exactly two columns.")
            sys.exit(1)

        # Write headers to output file
        writer.writerow(headers + ["Status", "Longitude", "Latitude"])

        # Process each row
        for row in reader:
            identifier = row[0]
            sanitized_address = sanitize_address(row[1])
            url = f"https://restapi.amap.com/v3/geocode/geo?address={sanitized_address}&key={api_key}"

            # Make API request
            print(f"Requesting for {identifier}...")
            response = requests.get(url)
            data = response.json()

            # Extract information from the API response
            status = data.get("info", "")
            geocodes = data.get("geocodes", [])

            if geocodes:
                location = geocodes[0].get("location", "")
                longitude, latitude = location.split(",") if location else ("", "")
            else:
                longitude, latitude = "NA", "NA"
            
            print(f"{identifier}: {status}, {longitude}, {latitude}")

            # Write the processed row immediately
            writer.writerow(row + [status, longitude, latitude])

            sleep(0.1) # sleep for 100ms to avoid rate limiting     

    print(f"Conversion completed. Results saved to '{output_file}'.")

if __name__ == "__main__":
    convert_addresses_to_gps(input_file, output_file, api_key)