
import os

# Import all the handlers
for filename in os.listdir('handlers'):
    exec('from %s import *' % filename.split('.')[0])