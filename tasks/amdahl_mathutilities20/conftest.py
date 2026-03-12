import sys
import os

# Ensure the repo directory itself is on sys.path so that
# "from add import add" etc. work regardless of how pytest is invoked.
sys.path.insert(0, os.path.dirname(__file__))
