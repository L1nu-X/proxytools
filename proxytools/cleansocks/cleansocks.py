#!/usr/bin/env python
# CleanSocks (Proxy List Cleaner/Tester)
# Developed by acidvegas in Python 3
# http://github.com/acidvegas/proxytools
# cleansocks.py

import argparse
import concurrent.futures
import os
import re
import sys
import time

sys.dont_write_bytecode = True

# Config
max_threads = 150
timeout     = 5

def alert(msg):
	print(f'{get_time()} | [+] - {msg}')

def check_proxy(proxy):
	return re.match('^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]):(?:6553[0-5]|655[0-2][0-9]|65[0-4][0-9]{2}|6[0-4][0-9]{3}|[1-5][0-9]{4}|[1-9][0-9]{1,3}|[0-9])$', proxy)

def debug(msg):
	print(f'{get_time()} | [~] - {msg}')

def error(msg):
	print(f'{get_time()} | [!] - {msg}')

def error_exit(msg):
	raise SystemExit(f'{get_time()} | [!] - {msg}')

def get_time():
	return time.strftime('%I:%M:%S')

def test_proxy(proxy):
	global alive
	ip, port = proxy.split(':')
	try:
		sock = socks.socksocket()
		sock.set_proxy(socks.SOCKS5, ip, int(port))
		sock.settimeout(timeout)
		sock.connect(('www.google.com', 80))
	except:
		error('BAD  | ' + proxy)
	else:
		alert('GOOD | ' + proxy)
		alive.append(proxy)
	finally:
		sock.close()

# Main
print(''.rjust(56, '#'))
print('#{0}#'.format(''.center(54)))
print('#{0}#'.format('CleanSocks (Proxy List Cleaner/Tester)'.center(54)))
print('#{0}#'.format('Developed by acidvegas in Python 3'.center(54)))
print('#{0}#'.format('https://github.com/acidvegas/proxytools'.center(54)))
print('#{0}#'.format(''.center(54)))
print(''.rjust(56, '#'))
parser = argparse.ArgumentParser(prog='cleansocks.py', usage='%(prog)s <input> <output>')
parser.add_argument('input',  help='file to scan')
parser.add_argument('output', help='file to output')
args = parser.parse_args()
try:
	import socks
except ImportError:
	error_exit('Missing PySocks module! (https://pypi.python.org/pypi/PySocks)')
debug('Loading proxy file...')
if os.path.isfile(args.input):
	proxies = [line.strip() for line in open(args.input).readlines() if line]
else:
	error_exit('Missing proxies file!')
debug('Loaded {0} proxies from file.'.format(format(len(proxies), ',d')))
debug('Removing duplicate/invalid proxies...')
invalid = list()
for proxy in proxies:
	if not check_proxy(proxy):
		invalid.append(proxy)
valid = [x for x in proxies if x not in invalid]
deduped = list(set(valid))
dedupered, ip_list = list(), list()
for proxy in deduped:
	ip = proxy.split(':')[0]
	if ip not in ip_list:
		ip_list.append(ip)
		dedupered.append(proxy)
dedupered.sort()
debug('Testing proxies...')
alive = list()
with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads) as executor:
	checks = {executor.submit(test_proxy, proxy): proxy for proxy in dedupered}
	for future in concurrent.futures.as_completed(checks):
		checks[future]
alive.sort()
with open (args.output, 'w') as output_file:
	for proxy in alive:
		output_file.write(proxy + '\n')
debug('Total     : ' + format(len(proxies),                ',d'))
debug('Invalid   : ' + format(len(invalid),                ',d'))
debug('Duplicate : ' + format(len(proxies)-len(dedupered), ',d'))
debug('Dead      : ' + format(len(dedupered)-len(alive),   ',d'))
debug('Alive     : ' + format(len(alive),                  ',d'))