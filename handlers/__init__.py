
import os

# Import all the handlers
if os.path.exists('handlers'):
	for filename in os.listdir('handlers'):
		if 'vanhi' not in filename:
			exec('from %s import *' % filename.split('.')[0])