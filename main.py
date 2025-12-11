import functions_framework
from RentCastAVM import *

# Import your PortFileAVMProcessor and GetRentCastAPIKeyFromSecrets accordingly

@functions_framework.http
def rentcast_avm_processor(request):
    
    # Obtain API key from environment variables for Google Cloud Function
    RENTCAST_API_KEY = GetRentCastAPIKeyFromSecrets()  # Replace with your actual API key
    
    # Initialize and run processor
    processor = PortFileAVMProcessor(api_key=RENTCAST_API_KEY)
    processor.process_all_addresses()
    
    return "Processing completed...."
 
