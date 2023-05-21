import sys
import os

# Add the path to the reconaissance directory to the module search path
reconaissance_path = os.path.join(
    os.path.dirname(__file__), "..", "reconaissance")
sys.path.append(reconaissance_path)

from scan import scan

# Import the scan function from reconaissance.scan

# Call the scan function
# scan("outremont", True):
# scan("montRoyal",True) # Je deconseille le verbose
# scan("verdun", True)
# scan("riviere",True) # Je deconseille le verbose
scan("saintLeonard",True) # Je deconseille le verbose
