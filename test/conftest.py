import os
import sys

# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/crud')))

# Determine the absolute path of the root directory and src directory
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
SRC_DIR = os.path.join(ROOT_DIR, 'src')

# Add the src directory to sys.path
sys.path.insert(0, SRC_DIR)

# SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# sys.path.append(os.path.dirname(SCRIPT_DIR))

import src
