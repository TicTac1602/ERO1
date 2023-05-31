import sys
import os

# Add the path to the reconaissance directory to the module search path
reconaissance_path = os.path.join(
    os.path.dirname(__file__), "..", "scan")
sys.path.append(reconaissance_path)

from scan import scan

# Import the scan function from reconaissance.scan

# Call the scan function
scan("montreal")
# scan("outremont",True)
# scan("montRoyal",True) # Je deconseille le verbose
# scan("verdun",True)
# scan("riviere") # Je deconseille le verbose
# scan("saintLeonard") # Je deconseille le verbose
