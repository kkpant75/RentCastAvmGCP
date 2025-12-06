import functions_framework
from RentCastAVM import *

# Import your RentCastAVMProcessor and GetRentCastAPIKeyFromSecrets accordingly

@functions_framework.http
def rentcast_avm_processor(request):
    
    # Obtain API key from environment variables for Google Cloud Function
    RENTCAST_API_KEY = os.getenv("RENTCAST_API_KEY") #GetRentCastAPIKeyFromSecrets()
    COMP_COUNT = 5  # Number of comparables (can be parameterized)

    # Instantiate the processor with the API key and comp count
    processor = RentCastAVMProcessor(api_key=RENTCAST_API_KEY, comp_count=COMP_COUNT)
    
    # Run the address processing logic
    processor.process_all_addresses()
    
    return "Processing completed...." +str(RENTCAST_API_KEY)
 
