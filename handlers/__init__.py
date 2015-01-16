
import os

# Import all the handlers
if os.path.exists('handlers'):
    for filename in os.listdir('handlers'):
        exec('from %s import *' % filename.split('.')[0])