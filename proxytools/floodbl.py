#!/usr/bin/env python
# FloodBL (DNSBL Proxy Checker)
# Developed by acidvegas in Python 3
# http://github.com/acidvegas/proxytools
# floodbl.py

import argparse
import concurrent.futures
import os
import socket
import time

# Config
dnsbls      = ('dnsbl.dronebl.org', 'rbl.efnetrbl.org', 'torexit.dan.me.uk')
max_threads = 100
timeout     = 30

# Globals
bad  = list()
good = list()

socket.setdefaulttimeout(timeout)

def alert(msg):
	print(f'{get_time()} | [+] - {msg}')

def debug(msg):
	print(f'{get_time()} | [~] - {msg}')

def error(msg, reason=None):
	if reason:
		print(f'{get_time()} | [!] - {msg} ({reason})')
	else:
		print(f'{get_time()} | [!] - {msg}')

def error_exit(msg):
	raise SystemExit(f'{get_time()} | [!] - {msg}')

def get_time():
	return time.strftime('%I:%M:%S')

def check_proxy(proxy):
	global bad, good
	ip = proxy.split(':')[0]
	formatted_ip = '.'.join(ip.split('.')[::-1])
	for dnsbl in dnsbls:
		try:
			socket.gethostbyname(f'{formatted_ip}.{dnsbl}')
		except socket.gaierror:
			pass
		else:
			bad.append(ip)
			break
	if ip in bad:
		error('BAD  | ' + ip)
	else:
		good.append(proxy)
		alert('GOOD | ' + ip)

# Main
print(''.rjust(56, '#'))
print('#{0}#'.format(''.center(54)))
print('#{0}#'.format('FloodBL (DNSBL Proxy Tester)'.center(54)))
print('#{0}#'.format('Developed by acidvegas in Python 3'.center(54)))
print('#{0}#'.format('https://github.com/acidvegas/proxytools'.center(54)))
print('#{0}#'.format(''.center(54)))
print(''.rjust(56, '#'))
parser = argparse.ArgumentParser(prog='floodbl.py', usage='%(prog)s <input> <output>')
parser.add_argument('input',  help='file to scan')
parser.add_argument('output', help='file to output')
args = parser.parse_args()
debug('Loading proxy file...')
if os.path.isfile(args.input):
	proxies = [line.strip() for line in open(args.input).readlines() if line]
else:
	error_exit('Missing proxies file!')
debug(f'Loaded {len(proxies)} proxies from file.')
debug('Starting scan...')
with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads) as executor:
	checks = {executor.submit(check_proxy, proxy): proxy for proxy in proxies}
	for future in concurrent.futures.as_completed(checks):
		checks[future]
good.sort()
with open (args.output, 'w') as output_file:
	for proxy in good:
		output_file.write(proxy + '\n')
debug(f'Total: {len(proxies)}')
debug(f'Bad:   {len(bad)}')
debug(f'Good:  {len(good)}')