#!/usr/bin/env python
# SockSpot (Blogspot Proxy Scraper)
# Developed by acidvegas in Python 3
# http://github.com/acidvegas/proxytools
# sockspot.py

import datetime
import json
import os
import re
import threading
import time
import urllib.request

# Blogspot URLs
blogspot_list = (
	'live-socks.net',
	'socks24.org',
	'sock5us.blogspot.com',
	'sockproxy.blogspot.com',
	'socksproxylist24.blogspot.com',
	'sslproxies24.blogspot.com',
	'vip-socks24.blogspot.com'
)

# Settings
max_results = 100 # Maximum number of results per-page.
post_depth  = 2   # How many days back from the current date to pull posts from. (1 = Today Only)
timeout     = 30  # Timeout for HTTP requests.

# Globals
proxy_file       = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'proxies.txt')
proxy_list       = list()
proxy_list_clean = list()
threads          = dict()

def debug(msg):
	print(f'{get_time()} | [~] - {msg}')

def error(msg, reason):
	print(f'{get_time()} | [!] - {msg} ({reason})')

def get_time():
	return time.strftime('%I:%M:%S')

def get_date():
	date = datetime.datetime.today()
	return '{0}-{1:02d}-{2:02d}'.format(date.year, date.month, date.day)

def get_date_range():
	date_range = datetime.datetime.today() - datetime.timedelta(days=post_depth)
	return '{0}-{1:02d}-{2:02d}'.format(date_range.year, date_range.month, date_range.day)

def get_source(url):
	req = urllib.request.Request(url)
	req.add_header('User-Agent', 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)')
	source  = urllib.request.urlopen(req, timeout=timeout)
	charset = source.headers.get_content_charset()
	if charset:
		return source.read().decode(charset)
	else:
		return source.read().decode()

def parse_blogspot(url):
	global proxy_list
	try:
		source = json.loads(get_source(f'http://{url}/feeds/posts/default?max-results={max_results}&alt=json&updated-min={get_date_range()}T00:00:00&updated-max={get_date()}T23:59:59&orderby=updated'))
		found  = []
		if source['feed'].get('entry'):
			for item in source['feed']['entry']:
				data    = item['content']['$t']
				proxies = re.findall('[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+:[0-9]+', data, re.MULTILINE)
				if proxies:
					found      += proxies
					proxy_list += proxies
			debug('Found {0} proxies on {1}'.format(format(len(found), ',d'), url))
		else:
			error('No posts found on page!', url)
	except Exception as ex:
		error(f'Failed to parse {url} for proxies!', ex)

# Main
print(''.rjust(56, '#'))
print('#{0}#'.format(''.center(54)))
print('#{0}#'.format('SockSpot Proxy Scraper'.center(54)))
print('#{0}#'.format('Developed by acidvegas in Python 3'.center(54)))
print('#{0}#'.format('https://github.com/acidvegas/proxytools'.center(54)))
print('#{0}#'.format(''.center(54)))
print(''.rjust(56, '#'))
debug(f'Scanning {len(blogspot_list)} URLs from list...')
for url in blogspot_list:
	threads[url] = threading.Thread(target=parse_blogspot, args=(url,))
for thread in threads:
	threads[thread].start()
for thread in threads:
	threads[thread].join()
debug('Found {0} total proxies!'.format(format(len(proxy_list), ',d')))
with open (proxy_file, 'w') as proxy__file:
	for proxy in proxy_list:
		proxy__file.write(proxy + '\n')