"""
OWASP Maryam!

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

meta = {
	'name': 'Cloud Storage',
	'author': 'Vikas Kundu',
	'version': '0.5',
	'description': 'Search cloud storage sites and show the results.',
	'sources': (	'google', 'carrot2', 'bing', 'yippy', 'yahoo', 'millionshort', 'qwant', 'duckduckgo'),
	'options': (
		('query', None, True, 'Query string', '-q', 'store', str),
		('limit', 1, False, 'Search limit(number of pages, default=1)', '-l', 'store', int),
		('count', 50, False, 'Number of links per page(min=10, max=100, default=50)', '-c', 'store', int),
		('engine', 'bing', False, 'Engine names for search(default=google)', '-e', 'store', str),
		('thread', 2, False, 'The number of engine that run per round(default=2)', '-t', 'store', int),
	),
	'examples': ('cloud_storage -q <QUERY> -l 15 --output',)
}

LINKS = []
PAGES = ''

def search(self, name, q, q_formats, limit, count):
	global PAGES,LINKS
	engine = getattr(self, name)
	name = engine.__init__.__name__
	q = f"{name}_q" if f"{name}_q" in q_formats else q_formats['default_q']
	varnames = engine.__init__.__code__.co_varnames
	if 'limit' in varnames and 'count' in varnames:
		attr = engine(q, limit, count)
	elif 'limit' in varnames:
		attr = engine(q, limit)
	else:
		attr = engine(q)

	attr.run_crawl()
	LINKS += attr.links
	PAGES += attr.pages

def module_api(self,site_name,site_url):
	query = self.options['query']
	limit = self.options['limit']
	count = self.options['count']
	engine = self.options['engine'].split(',')
	output = {'site': '', 'links': [] }
	q_formats = {
		'default_q': f'site:{site_url} {query}',
		'yippy_q': f'"{site_url}" {query}',
		'millionshort_q': f'site:{site_url} "{query}"',
		'qwant_q': f'site:{site_url} {query}'
	}
	
	self.thread(search, self.options['thread'], engine, query, q_formats, limit, count, meta['sources'])

	output['site'] = site_name
	output['links'] = list(self.reglib().filter(r"https?://([\w\-\.]+\.)?"\
	+site_url.replace('.','\.')+"/", list(set(LINKS)))) #escaping . for regex search using replace()

	self.save_gather(output, 'osint/cloud_storage', query, output=self.options.get('output'))
	return output

def module_run(self):
	sites = {'GoogleDrive': 'drive.google.com', 'DropBox': 'dl.dropboxusercontent.com',\
	 'OneDrive': '1drv.ms', 'Box': 'box.com/s', 'Amazon S3': 's3.amazonaws.com'}

	for site_name,site_url in sites.items():
		self.alert_results(module_api(self,site_name, site_url))
