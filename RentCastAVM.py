#!/usr/bin/env python3
"""
RentCast API to CSV Converter
Fetches property valuation data and converts to CSV format
"""

import argparse
import requests
import csv
import json
import os
from datetime import datetime
from urllib.parse import quote
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def fetch_rentcast_data1(api_key=None, address=None, comp_count=5):

	jsonstr="""{
	  "price": 250000,
	  "priceRangeLow": 195000,
	  "priceRangeHigh": 304000,
	  "subjectProperty": {
		"id": "5500-Grand-Lake-Dr,-San-Antonio,-TX-78244",
		"formattedAddress": "5500 Grand Lake Dr, San Antonio, TX 78244",
		"addressLine1": "5500 Grand Lake Dr",
		"addressLine2": null,
		"city": "San Antonio",
		"state": "TX",
		"stateFips": "48",
		"zipCode": "78244",
		"county": "Bexar",
		"countyFips": "029",
		"latitude": 29.476011,
		"longitude": -98.351454,
		"propertyType": "Single Family",
		"bedrooms": 3,
		"bathrooms": 2,
		"squareFootage": 1878,
		"lotSize": 8843,
		"yearBuilt": 1973,
		"lastSaleDate": "2024-11-18T00:00:00.000Z",
		"lastSalePrice": 270000
	  },
	  "comparables": [
		{
		  "id": "5207-Pine-Lake-Dr,-San-Antonio,-TX-78244",
		  "formattedAddress": "5207 Pine Lake Dr, San Antonio, TX 78244",
		  "addressLine1": "5207 Pine Lake Dr",
		  "addressLine2": null,
		  "city": "San Antonio",
		  "state": "TX",
		  "stateFips": "48",
		  "zipCode": "78244",
		  "county": "Bexar",
		  "countyFips": "029",
		  "latitude": 29.47046,
		  "longitude": -98.351561,
		  "propertyType": "Single Family",
		  "bedrooms": 3,
		  "bathrooms": 2,
		  "squareFootage": 1895,
		  "lotSize": 6882,
		  "yearBuilt": 1988,
		  "status": "Active",
		  "price": 289444,
		  "listingType": "Standard",
		  "listedDate": "2025-04-11T00:00:00.000Z",
		  "removedDate": null,
		  "lastSeenDate": "2025-09-03T10:57:39.532Z",
		  "daysOnMarket": 146,
		  "distance": 0.384,
		  "daysOld": 1,
		  "correlation": 0.9916
		},
		{
		  "id": "6707-Lake-Cliff-St,-San-Antonio,-TX-78244",
		  "formattedAddress": "6707 Lake Cliff St, San Antonio, TX 78244",
		  "addressLine1": "6707 Lake Cliff St",
		  "addressLine2": null,
		  "city": "San Antonio",
		  "state": "TX",
		  "stateFips": "48",
		  "zipCode": "78244",
		  "county": "Bexar",
		  "countyFips": "029",
		  "latitude": 29.47617,
		  "longitude": -98.356908,
		  "propertyType": "Single Family",
		  "bedrooms": 3,
		  "bathrooms": 2,
		  "squareFootage": 1811,
		  "lotSize": 8146,
		  "yearBuilt": 1977,
		  "status": "Inactive",
		  "price": 279000,
		  "listingType": "Standard",
		  "listedDate": "2025-06-06T00:00:00.000Z",
		  "removedDate": "2025-07-12T00:00:00.000Z",
		  "lastSeenDate": "2025-07-11T13:21:20.968Z",
		  "daysOnMarket": 36,
		  "distance": 0.3286,
		  "daysOld": 55,
		  "correlation": 0.9887
		},
		{
		  "id": "6917-Deep-Lake-Dr,-San-Antonio,-TX-78244",
		  "formattedAddress": "6917 Deep Lake Dr, San Antonio, TX 78244",
		  "addressLine1": "6917 Deep Lake Dr",
		  "addressLine2": null,
		  "city": "San Antonio",
		  "state": "TX",
		  "stateFips": "48",
		  "zipCode": "78244",
		  "county": "Bexar",
		  "countyFips": "029",
		  "latitude": 29.479375,
		  "longitude": -98.351978,
		  "propertyType": "Single Family",
		  "bedrooms": 3,
		  "bathrooms": 2,
		  "squareFootage": 1753,
		  "lotSize": 11151,
		  "yearBuilt": 1974,
		  "status": "Inactive",
		  "price": 199900,
		  "listingType": "Standard",
		  "listedDate": "2025-05-22T00:00:00.000Z",
		  "removedDate": "2025-08-27T00:00:00.000Z",
		  "lastSeenDate": "2025-08-26T12:36:31.859Z",
		  "daysOnMarket": 97,
		  "distance": 0.2348,
		  "daysOld": 9,
		  "correlation": 0.9863
		},
		{
		  "id": "5314-Lost-Tree,-San-Antonio,-TX-78244",
		  "formattedAddress": "5314 Lost Tree, San Antonio, TX 78244",
		  "addressLine1": "5314 Lost Tree",
		  "addressLine2": null,
		  "city": "San Antonio",
		  "state": "TX",
		  "stateFips": "48",
		  "zipCode": "78244",
		  "county": "Bexar",
		  "countyFips": "029",
		  "latitude": 29.477064,
		  "longitude": -98.343686,
		  "propertyType": "Single Family",
		  "bedrooms": 3,
		  "bathrooms": 2,
		  "squareFootage": 1948,
		  "lotSize": 9017,
		  "yearBuilt": 2000,
		  "status": "Inactive",
		  "price": 159900,
		  "listingType": "Standard",
		  "listedDate": "2025-06-23T00:00:00.000Z",
		  "removedDate": "2025-06-28T00:00:00.000Z",
		  "lastSeenDate": "2025-06-27T11:02:28.080Z",
		  "daysOnMarket": 5,
		  "distance": 0.4734,
		  "daysOld": 69,
		  "correlation": 0.9859
		},
		{
		  "id": "7207-Solar-Eclipse,-Converse,-TX-78109",
		  "formattedAddress": "7207 Solar Eclipse, Converse, TX 78109",
		  "addressLine1": "7207 Solar Eclipse",
		  "addressLine2": null,
		  "city": "Converse",
		  "state": "TX",
		  "stateFips": "48",
		  "zipCode": "78109",
		  "county": "Bexar",
		  "countyFips": "029",
		  "latitude": 29.463689,
		  "longitude": -98.348663,
		  "propertyType": "Single Family",
		  "bedrooms": 3,
		  "bathrooms": 2,
		  "squareFootage": 1883,
		  "lotSize": 5140,
		  "yearBuilt": 2022,
		  "status": "Active",
		  "price": 320000,
		  "listingType": "Standard",
		  "listedDate": "2025-03-10T00:00:00.000Z",
		  "removedDate": null,
		  "lastSeenDate": "2025-09-03T10:33:44.607Z",
		  "daysOnMarket": 178,
		  "distance": 0.8687,
		  "daysOld": 1,
		  "correlation": 0.9835
		}
	  ]
	}"""
	return json.loads(jsonstr)



def fetch_rentcast_data(api_key, address, comp_count=5):
    """
    Fetch data from RentCast API
    
    Args:
        api_key (str): RentCast API key
        address (str): Property address
        comp_count (int): Number of comparable properties
    
    Returns:
        dict: JSON response from API
    """
    encoded_address = quote(address)
    url = f"https://api.rentcast.io/v1/avm/value?address={encoded_address}&compCount={comp_count}"
    
    headers = {
        'accept': 'application/json',
        'X-Api-Key': api_key
    }
    
    print(f"Fetching data for: {address}")
    print(f"Requesting {comp_count} comparables...")
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        print("✓ Data fetched successfully\n")
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"✗ Error fetching data: {e}")
        return None


def write_to_csv(data, output_file):
    """
    Convert JSON data to CSV format and write to file
    Each row contains subject property data + one comparable property
    
    Args:
        data (dict): JSON data from RentCast API
        output_file (str): Output CSV filename
    """
    if not data:
        print("No data to write")
        return
    
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        
        # Create headers combining subject property and comparable fields
        headers = [
            # Valuation data
            'Estimated_Price',
            'Price_Range_Low',
            'Price_Range_High',
            
            # Subject Property fields (prefixed with Subject_)
            'Subject_Property_ID',
            'Subject_Formatted_Address',
            'Subject_Address_Line_1',
            'Subject_Address_Line_2',
            'Subject_City',
            'Subject_State',
            'Subject_State_FIPS',
            'Subject_Zip_Code',
            'Subject_County',
            'Subject_County_FIPS',
            'Subject_Latitude',
            'Subject_Longitude',
            'Subject_Property_Type',
            'Subject_Bedrooms',
            'Subject_Bathrooms',
            'Subject_Square_Footage',
            'Subject_Lot_Size',
            'Subject_Year_Built',
            'Subject_Last_Sale_Date',
            'Subject_Last_Sale_Price',
            
            # Comparable Property fields (prefixed with Comp_)
            'Comp_Property_ID',
            'Comp_Formatted_Address',
            'Comp_Address_Line_1',
            'Comp_Address_Line_2',
            'Comp_City',
            'Comp_State',
            'Comp_State_FIPS',
            'Comp_Zip_Code',
            'Comp_County',
            'Comp_County_FIPS',
            'Comp_Latitude',
            'Comp_Longitude',
            'Comp_Property_Type',
            'Comp_Bedrooms',
            'Comp_Bathrooms',
            'Comp_Square_Footage',
            'Comp_Lot_Size',
            'Comp_Year_Built',
            'Comp_Status',
            'Comp_Price',
            'Comp_Listing_Type',
            'Comp_Listed_Date',
            'Comp_Removed_Date',
            'Comp_Last_Seen_Date',
            'Comp_Days_On_Market',
            'Comp_Distance_Miles',
            'Comp_Days_Old',
            'Comp_Correlation'
        ]
        
        writer.writerow(headers)
        
        # Extract subject property data
        sp = data.get('subjectProperty', {})
        subject_data = [
            data.get('price', ''),
            data.get('priceRangeLow', ''),
            data.get('priceRangeHigh', ''),
            sp.get('id', ''),
            sp.get('formattedAddress', ''),
            sp.get('addressLine1', ''),
            sp.get('addressLine2', ''),
            sp.get('city', ''),
            sp.get('state', ''),
            sp.get('stateFips', ''),
            sp.get('zipCode', ''),
            sp.get('county', ''),
            sp.get('countyFips', ''),
            sp.get('latitude', ''),
            sp.get('longitude', ''),
            sp.get('propertyType', ''),
            sp.get('bedrooms', ''),
            sp.get('bathrooms', ''),
            sp.get('squareFootage', ''),
            sp.get('lotSize', ''),
            sp.get('yearBuilt', ''),
            sp.get('lastSaleDate', ''),
            sp.get('lastSalePrice', '')
        ]
        
        # Write one row for each comparable with subject property data
        comparables = data.get('comparables', [])
        
        if comparables:
            for comp in comparables:
                row = subject_data + [
                    comp.get('id', ''),
                    comp.get('formattedAddress', ''),
                    comp.get('addressLine1', ''),
                    comp.get('addressLine2', ''),
                    comp.get('city', ''),
                    comp.get('state', ''),
                    comp.get('stateFips', ''),
                    comp.get('zipCode', ''),
                    comp.get('county', ''),
                    comp.get('countyFips', ''),
                    comp.get('latitude', ''),
                    comp.get('longitude', ''),
                    comp.get('propertyType', ''),
                    comp.get('bedrooms', ''),
                    comp.get('bathrooms', ''),
                    comp.get('squareFootage', ''),
                    comp.get('lotSize', ''),
                    comp.get('yearBuilt', ''),
                    comp.get('status', ''),
                    comp.get('price', ''),
                    comp.get('listingType', ''),
                    comp.get('listedDate', ''),
                    comp.get('removedDate', ''),
                    comp.get('lastSeenDate', ''),
                    comp.get('daysOnMarket', ''),
                    comp.get('distance', ''),
                    comp.get('daysOld', ''),
                    comp.get('correlation', '')
                ]
                writer.writerow(row)
        else:
            # If no comparables, write subject property data only
            row = subject_data + [''] * 28  # 28 empty fields for comparable data
            writer.writerow(row)
    
    print(f"✓ CSV file created: {output_file}")
    print(f"  Total rows: {len(comparables) if comparables else 1} (excluding header)")


def print_summary(data):
    """Print a summary of the fetched data"""
    if not data:
        return
    
    print("=" * 60)
    print("DATA SUMMARY")
    print("=" * 60)
    
    if 'subjectProperty' in data:
        sp = data['subjectProperty']
        print(f"Address: {sp.get('formattedAddress', 'N/A')}")
        print(f"Property Type: {sp.get('propertyType', 'N/A')}")
        print(f"Specs: {sp.get('bedrooms', 'N/A')} bed, {sp.get('bathrooms', 'N/A')} bath, {sp.get('squareFootage', 'N/A'):,} sq ft")
        print(f"Year Built: {sp.get('yearBuilt', 'N/A')}")
    
    print(f"\nEstimated Price: ${data.get('price', 'N/A'):,}")
    print(f"Price Range: ${data.get('priceRangeLow', 'N/A'):,} - ${data.get('priceRangeHigh', 'N/A'):,}")
    
    comp_count = len(data.get('comparables', []))
    print(f"\nComparable Properties Found: {comp_count}")
    print("=" * 60)


def main():
    """Main function to parse arguments and execute the script"""
    parser = argparse.ArgumentParser(
        description='Fetch RentCast property data and convert to CSV',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python rentcast_to_csv.py --address "5500 Grand Lake Dr, San Antonio, TX, 78244"
  python rentcast_to_csv.py --address "123 Main St, Austin, TX" --comp-count 10
  python rentcast_to_csv.py --address "456 Oak Ave, Dallas, TX" --output property_data.csv
  python rentcast_to_csv.py --api-key YOUR_KEY --address "123 Main St" (override .env API key)
        '''
    )
    
    parser.add_argument(
        '--api-key',
        default=None,
        help='RentCast API key (overrides .env file if provided)'
    )
    
    parser.add_argument(
        '--address',
        required=True,
        help='Property address (e.g., "5500 Grand Lake Dr, San Antonio, TX, 78244")'
    )
    
    parser.add_argument(
        '--comp-count',
        type=int,
        default=5,
        help='Number of comparable properties (default: 5, max: 25)'
    )
    
    parser.add_argument(
        '--output',
        default=None,
        help='Output CSV filename (default: rentcast_YYYYMMDD_HHMMSS.csv)'
    )
    
    args = parser.parse_args()
    
    # Get API key from command line argument or environment variable
    api_key = args.api_key or os.getenv('RENTCAST_API_KEY')
    
    if not api_key:
        print("✗ Error: API key not found!")
        print("  Please either:")
        print("  1. Add RENTCAST_API_KEY to your .env file, or")
        print("  2. Provide it via --api-key argument")
        print("\nExample .env file:")
        print("  RENTCAST_API_KEY=your_api_key_here")
        exit(1)
    
    # Validate comp_count
    if args.comp_count < 1 or args.comp_count > 25:
        print("Warning: comp-count should be between 1 and 25. Using default value of 5.")
        args.comp_count = 5
    
    # Generate output filename if not provided
    if not args.output:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        args.output = f'rentcast_avm_{timestamp}.csv'
    
    # Fetch data from API
    data = fetch_rentcast_data(api_key, args.address, args.comp_count)
    
    if data:
        # Print summary
        print_summary(data)
        
        # Write to CSV
        write_to_csv(data, args.output)
        
        print(f"\n✓ Process completed successfully!")
        print(f"  Output file: {args.output}")
    else:
        print("\n✗ Failed to fetch data. Please check your API key and address.")
        exit(1)


if __name__ == '__main__':
    main()

