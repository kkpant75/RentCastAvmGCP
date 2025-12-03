import os
import sys
import json
import requests
import logging
from urllib.parse import quote
from datetime import datetime, timedelta
from google.cloud import storage
from io import StringIO
from dotenv import load_dotenv

load_dotenv()

class RentCastAVMProcessor:
    def __init__(self, api_key, comp_count=5):
        """
        Initialize the RentCast AVM Processor
        
        Args:
            api_key: RentCast API key
            comp_count: Number of comparables (default: 5)
        """
        self.api_key = api_key
        self.comp_count = comp_count
        self.bucket_name = "rent-cast-avm"
        self.base_folder="AVM"
        self.input_file = F"{self.base_folder}/avmfile.txt"
        self.processed_file = f"{self.base_folder}/processed/avmfile.txt"
        self.output_folder = "JSON"
        self.log_folder = "Logs"
        
        # Setup logging
        self.setup_logging()
        
    def setup_logging(self):
        """Setup logging configuration with StringIO buffer and console handlers"""
        # Create logger
        self.logger = logging.getLogger('RentCastAVMProcessor')
        self.logger.setLevel(logging.INFO)
        
        # Clear existing handlers
        self.logger.handlers = []
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # StringIO buffer for log storage
        self.log_buffer = StringIO()
        buffer_handler = logging.StreamHandler(self.log_buffer)
        buffer_handler.setLevel(logging.INFO)
        buffer_handler.setFormatter(formatter)
        self.logger.addHandler(buffer_handler)
        
        self.logger.info("Logging initialized")
    
    def upload_log_to_gcp(self):
        """Upload log from StringIO buffer to GCP bucket"""
        try:
            # Generate log filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_filename = f"rentcast_avm_{timestamp}.log"
            log_path = f"{self.log_folder}/{log_filename}"
            
            # Get log content from buffer
            log_content = self.log_buffer.getvalue()
            
            # Upload to GCP
            storage_client = storage.Client()
            bucket = storage_client.bucket(self.bucket_name)
            blob = bucket.blob(log_path)
            blob.upload_from_string(log_content, content_type='text/plain')
            
            self.logger.info(f"Log file uploaded to GCP: {log_path}")
            
            # Close the buffer
            self.log_buffer.close()
                
        except Exception as e:
            self.logger.error(f"Error uploading log to GCP: {e}")
    
    def cleanup_old_logs(self, days=7):
        """
        Delete log files older than specified days
        
        Args:
            days: Number of days to retain logs (default: 7)
        """
        try:
            storage_client = storage.Client()
            bucket = storage_client.bucket(self.bucket_name)
            
            cutoff_date = datetime.now() - timedelta(days=days)
            deleted_count = 0
            
            self.logger.info(f"Cleaning up log files older than {days} days...")
            
            # List all blobs in the Logs folder
            blobs = bucket.list_blobs(prefix=f"{self.log_folder}/")
            
            for blob in blobs:
                # Get blob creation time
                if blob.time_created:
                    # Convert to offset-naive datetime for comparison
                    blob_date = blob.time_created.replace(tzinfo=None)
                    
                    if blob_date < cutoff_date:
                        self.logger.info(f"Deleting old log file: {blob.name}")
                        blob.delete()
                        deleted_count += 1
            
            self.logger.info(f"Deleted {deleted_count} old log file(s)")
            
        except Exception as e:
            self.logger.error(f"Error cleaning up old logs: {e}")
    
    def cleanup_old_processed_files(self, days=100):
        """
        Delete processed files older than specified days
        
        Args:
            days: Number of days to retain processed files (default: 100)
        """
        try:
            storage_client = storage.Client()
            bucket = storage_client.bucket(self.bucket_name)
            
            cutoff_date = datetime.now() - timedelta(days=days)
            deleted_count = 0
            
            self.logger.info(f"Cleaning up processed files older than {days} days...")
            
            # List all blobs in the Input/processed folder
            blobs = bucket.list_blobs(prefix=f"{self.base_folder}/processed/")
            
            for blob in blobs:
                # Get blob creation time
                if blob.time_created:
                    # Convert to offset-naive datetime for comparison
                    blob_date = blob.time_created.replace(tzinfo=None)
                    
                    if blob_date < cutoff_date:
                        self.logger.info(f"Deleting old processed file: {blob.name}")
                        blob.delete()
                        deleted_count += 1
            
            self.logger.info(f"Deleted {deleted_count} old processed file(s)")
            
        except Exception as e:
            self.logger.error(f"Error cleaning up old processed files: {e}")
    
    def read_addresses_from_gcp(self):
        """Read addresses from GCP bucket"""
        try:
            self.logger.info(f"Reading addresses from {self.bucket_name}/{self.input_file}")
            
            storage_client = storage.Client()
            bucket = storage_client.bucket(self.bucket_name)
            blob = bucket.blob(self.input_file)
            
            # Download file content
            content = blob.download_as_text()
            addresses = [line.strip() for line in content.split('\n') if line.strip()]
            
            self.logger.info(f"Successfully read {len(addresses)} addresses from GCP")
            return addresses
            
        except Exception as e:
            self.logger.error(f"Error reading from GCP: {e}")
            return []
    
    def call_rentcast_api(self, address):
        """
        Call RentCast API for a single address
        
        Args:
            address: The address to query
            
        Returns:
            dict: API response data or error information
        """
        try:
            encoded_address = quote(address)
            url = f"https://api.rentcast.io/v1/avm/value?address={encoded_address}&compCount={self.comp_count}"
            
            headers = {
                "X-Api-Key": self.api_key,
                "Accept": "application/json"
            }
            
            self.logger.debug(f"Calling API for address: {address}")
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                self.logger.info(f"SUCCESS: {address}")
                return {
                    "address": address,
                    "status": "success",
                    "data": response.json()
                }
            else:
                self.logger.warning(f"ERROR: API Error for {address}: Status {response.status_code}")
                return {
                    "address": address,
                    "status": "error",
                    "error_code": response.status_code,
                    "error_message": response.text
                }
                
        except Exception as e:
            self.logger.error(f"EXCEPTION for {address}: {str(e)}")
            return {
                "address": address,
                "status": "error",
                "error_message": str(e)
            }
    
    def process_batch(self, addresses):
        """
        Process a batch of addresses
        
        Args:
            addresses: List of addresses to process
            
        Returns:
            list: Results for all addresses in the batch
        """
        results = []
        success_count = 0
        error_count = 0
        
        for idx, address in enumerate(addresses, 1):
            self.logger.info(f"Processing address {idx}/{len(addresses)}: {address}")
            result = self.call_rentcast_api(address)
            results.append(result)
            
            if result['status'] == 'success':
                success_count += 1
            else:
                error_count += 1
        
        self.logger.info(f"Batch complete - Success: {success_count}, Errors: {error_count}")
        return results
    
    def save_batch_to_gcp(self, batch_results, batch_number):
        """
        Save batch results to GCP as JSON
        
        Args:
            batch_results: List of results for the batch
            batch_number: Batch number for file naming
        """
        try:
            # Generate filename with current date
            date_str = datetime.now().strftime("%y%m%d")
            filename = f"rentcast_avm_{date_str}_{batch_number:03d}.json"
            filepath = f"{self.output_folder}/{filename}"
            
            # Convert to JSON
            json_content = json.dumps(batch_results, indent=2)
            
            # Upload to GCP
            storage_client = storage.Client()
            bucket = storage_client.bucket(self.bucket_name)
            blob = bucket.blob(filepath)
            blob.upload_from_string(json_content, content_type='application/json')
            
            self.logger.info(f"Successfully saved {filename} to GCP ({len(batch_results)} records)")
            
        except Exception as e:
            self.logger.error(f"Error saving batch to GCP: {e}")
    
    def move_input_file_to_processed(self):
        """Move the input file to processed folder in GCP"""
        try:
            self.logger.info(f"Moving {self.input_file} to processed folder...")
            
            storage_client = storage.Client()
            bucket = storage_client.bucket(self.bucket_name)
            
            # Generate timestamped filename for processed file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            processed_filename = f"{self.base_folder}/processed/avmfile_{timestamp}.txt"
            
            # Get source blob
            source_blob = bucket.blob(self.input_file)
            
            # Copy to processed folder with timestamp
            bucket.copy_blob(source_blob, bucket, processed_filename)
            
            # Delete original
            source_blob.delete()
            
            self.logger.info(f"Successfully moved {self.input_file} to {processed_filename}")
            
        except Exception as e:
            self.logger.error(f"Error moving file: {e}")
    
    def process_all_addresses(self):
        """Main processing function"""
        try:
            self.logger.info("="*70)
            self.logger.info("Starting RentCast AVM processing...")
            self.logger.info("="*70)
            
            # Cleanup old files first
            self.cleanup_old_logs(days=7)
            self.cleanup_old_processed_files(days=100)
            
            # Read addresses from GCP
            addresses = self.read_addresses_from_gcp()
            
            if not addresses:
                self.logger.warning("No addresses found to process")
                return
            
            # Process in batches of 100
            batch_size = 100
            total_batches = (len(addresses) + batch_size - 1) // batch_size
            
            self.logger.info(f"Total addresses: {len(addresses)}")
            self.logger.info(f"Batch size: {batch_size}")
            self.logger.info(f"Total batches: {total_batches}")
            self.logger.info("-"*70)
            
            overall_success = 0
            overall_errors = 0
            
            for batch_num in range(total_batches):
                start_idx = batch_num * batch_size
                end_idx = min(start_idx + batch_size, len(addresses))
                batch_addresses = addresses[start_idx:end_idx]
                
                self.logger.info(f"\n{'='*70}")
                self.logger.info(f"Processing Batch {batch_num + 1}/{total_batches}")
                self.logger.info(f"Addresses: {start_idx + 1} to {end_idx}")
                self.logger.info(f"{'='*70}")
                
                # Process the batch
                batch_results = self.process_batch(batch_addresses)
                
                # Count successes and errors
                batch_success = sum(1 for r in batch_results if r['status'] == 'success')
                batch_errors = sum(1 for r in batch_results if r['status'] == 'error')
                
                overall_success += batch_success
                overall_errors += batch_errors
                
                # Save results to GCP
                self.save_batch_to_gcp(batch_results, batch_num + 1)
            
            # Move input file to processed folder
            self.logger.info("\n" + "="*70)
            self.logger.info("Moving input file to processed folder...")
            self.move_input_file_to_processed()
            
            # Final summary
            self.logger.info("\n" + "="*70)
            self.logger.info("PROCESSING COMPLETE")
            self.logger.info("="*70)
            self.logger.info(f"Total addresses processed: {len(addresses)}")
            self.logger.info(f"Successful: {overall_success}")
            self.logger.info(f"Errors: {overall_errors}")
            self.logger.info(f"Success rate: {(overall_success/len(addresses)*100):.2f}%")
            self.logger.info("="*70)
            
        except Exception as e:
            self.logger.error(f"Critical error in main processing: {e}", exc_info=True)
            
        finally:
            # Upload log to GCP
            self.upload_log_to_gcp()

###################Google Secret Code Section######################################################
from google.cloud import secretmanager
import google_crc32c

def access_secret_version(project_id: str, secret_id: str, version_id: str) -> secretmanager.AccessSecretVersionResponse:  
    client = secretmanager.SecretManagerServiceClient()

    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"

    # Access the secret version.
    response = client.access_secret_version(request={"name": name})

    # Verify payload checksum.
    crc32c = google_crc32c.Checksum()
    crc32c.update(response.payload.data)
    
    if response.payload.data_crc32c != int(crc32c.hexdigest(), 16):
        print("Data corruption detected.")
        return response

    payload = response.payload.data.decode("UTF-8")
    
    return payload
###################Google Secret Code Section Ends Here######################################################

def GetRentCastAPIKeyFromSecrets():
    try:

        return access_secret_version(os.getenv('SECRET_PROJECT_ID'),os.getenv('SECRET_KEY_RENTCAST'),'latest')
    except Exception as e:
        print("Exception Raiased in "+sys._getframe().f_code.co_name +"...."+str(e))
        raise Exception("GetRentCastAPIKeyFromSecrets --Issue "+str(e))
        
        
# # Main execution
# if __name__ == "__main__":
    # # Configuration   
    # RENTCAST_API_KEY = GetRentCastAPIKeyFromSecrets()  # Replace with your actual API key
    # COMP_COUNT = 5  # Number of comparables
    
    # # Initialize and run processor
    # processor = RentCastAVMProcessor(api_key=RENTCAST_API_KEY, comp_count=COMP_COUNT)
    # processor.process_all_addresses()