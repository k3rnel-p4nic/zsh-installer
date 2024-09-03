#!/usr/bin/env python3
# -*- coding: latin-1 -*-
#
#	Copyright (c) 2018
#	Angelone Alessandro <angelone.alessandro98@gmail.com>.
# 	All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its contributors
#    may be used to endorse or promote products derived from this software
#    without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.

import os
from sys import stderr, stdout
from argparse import ArgumentParser
from tarfile import open as tar_open
from shutil import move
from subprocess import run as run_cmd
from urllib.request import urlretrieve, urlopen
from urllib.parse import urlparse

# Setup Arguments

parser = ArgumentParser()

parser.add_argument('zsh_version', type=str)
parser.add_argument('--debug', help='Get debug messages', action='store_true')
parser.add_argument('-d', '--download-dir', help='Set a custom download dir', type=str)
parser.add_argument('-p', '--zsh-path', help='Set a different position to the zsh root path', type=str)
parser.add_argument('--set-default-workaround', action='store_true', help='Using a workaround, set ZSH as default shell.')

args = parser.parse_args()


# Script internal functions

def keyboard_interrupt_handler():
	if input('Are you sure you want to quit? [y/N] ').lower() != 'n':
		exit(1)


def which(cmd, returnPath=False):
	"""
	"which" tries to recreate the "which" built-in bash command
	Usage: which("cmd_to_search", returnPath=True|False)
	returnPath default value is "False". If is set on true
	will return:
	In case of success --> The path of cmd
	Otherwise --> None
	"""
	for path in os.environ["PATH"].split(os.pathsep):
		if os.path.exists(os.path.join(path, cmd)):
			# if not returnPath:
				# return True
			return True if not returnPath else os.path.join(path,cmd)

	return False if not returnPath else None



def download_manager(url, destdir=os.getcwd(), proxy=None, auth_proxy=None):
	"""
	Function to download files using HTTP.
	Returns: path of the downloaded file
	"""
	result = urlopen(url)
	result_url = result.url
	result_url_parse = urlparse(result_url)
	result_path = result_url_parse.path
	filename = os.path.basename(result_path)
	filepath = (destdir if destdir[-1] == '/' else destdir + '/') + filename

	def reporthook(count, block_size, total_size):
		percent = min(int(count * block_size * 100 / total_size), 100)
		progress_size = int(count * block_size)

		bar_len = 50
		filled_len = int(round(percent / 2.0))
		bar = '=' * filled_len + '-' * (bar_len - filled_len)

		if total_size > 1000**3:
			progress_size /= 1000**3
			total_size /= 1000**3
			unit = 'GB'

		elif total_size > 1000**2:
			progress_size /= 1000**2
			total_size /= 1000**2
			unit = 'MB'

		elif total_size > 1000:
			progress_size /= 1000
			total_size /= 1000
			unit = 'KB'

		if progress_size > total_size:
			progress_size = total_size

		stdout.write(f'\r[{bar}] {percent}%,  {progress_size:.2f} {unit} / {total_size:.2f} {unit}')


	if not os.path.exists(filepath):
		print(f'Downloading {filename}')
		urlretrieve(url, filepath, reporthook)
		print('')

	return filepath

# Basic checks

if os.geteuid() == 0:
	print('This script cannot be run as root.', file=stderr)
	exit(1)


for cmd in ['tar', 'make']:
	if not which(cmd):
		print(f'Fatal Error: {cmd} not found.', file=stderr)
		exit(1)


# Setting up vars

zsh_root_path = args.zsh_path if args.zsh_path and os.path.exists(args.zsh_path) else os.path.expanduser('~/zsh/')
source_path = 'https://sourceforge.net/projects/zsh/files/latest' if args.zsh_version == 'latest' else f'https://sourceforge.net/projects/zsh/files/zsh/{args.zsh_version}/zsh-{args.zsh_version}.tar.xz'
download_dir_path = args.download_dir if args.download_dir else os.getcwd()


# compile_cmd = ['./configure --prefix=' + zsh_root_path + ' --enable-multibyte --enable-function-subdirs --enable-fndir=' + zsh_root_path \
# + 'usr/share/zsh/functions --enable-scriptdir=' + zsh_root_path + 'usr/share/zsh/scripts --with-tcsetpgrp --enable-pcre --enable-cap --enable-zsh-secure-free --enable-etcdir=' \
# + zsh_root_path + 'etc/zsh']

compile_cmd = ['./configure', f'--prefix={zsh_root_path}', f'--enable-multibyte', '--enable-function-subdirs', f'--enable-fndir={zsh_root_path}usr/share/zsh/functions'
f'--enable-scriptdir={zsh_root_path}usr/share/zsh/scripts', '--with-tcsetpgrp', '--enable-pcre', '--enable-cap', '--enable-zsh-secure-free', f'--enable-etcdir={zsh_root_path}etc/zsh']

generate_cmd = 'make'
check_cmd = ['make', 'check']
install_cmd = ['make', 'install']


if args.debug:
	print('\n### DEBUG ###')
	print(f'ZSH DEST: {zsh_root_path}')
	print(f'SOURCE: {source_path}')
	print(f'DOWNLOAD DIR: {download_dir_path}')
	print('### END DEBUG ###\n\n')


downloaded_file = download_manager(source_path, download_dir_path)
print(downloaded_file)

parsed_filepath = os.path.splitext(downloaded_file)

if parsed_filepath[0].split('.')[-1]  == 'tar':
	with tar_open(downloaded_file) as tar_file:
		tar_file.extractall(download_dir_path)

elif not os.path.isdir(downloaded_file):
	print('Fatal error: unable to manage downloaded data.', file=stderr)
	exit(2)


# Root for ZSH

zsh_tree = ['bin', 'etc', 'lib', 'share', 'share/lib', 'share/share', 'usr']

for path in zsh_tree:
	try:
		os.mkdir(os.path.join(zsh_root_path, path), 0o755)
	except OSError as e:
		print(f'Error during mkdir: {e}')
		exit(3)

print(f'"{zsh_root_path}" root created.')


os.chdir(download_dir_path)

if args.debug:
	print('\n### DEBUG ###')
	print(f'COMPILE: {compile_cmd}')
	print(f'GENERATE: {generate_cmd}')
	print(f'CHECK: {check_cmd}')
	print(f'INSTALL: {install_cmd}')

run_cmd(compile_cmd).check_returncode()
run_cmd(generate_cmd).check_returncode()
run_cmd(check_cmd).check_returncode()
run_cmd(install_cmd).check_returncode()

if args.set_default_workaround:
	bashrc_path = os.path.expanduser('~/.bashrc')
	profile_path = os.path.expanduser('~/.bash_profile')
	zsh_bin = os.path.join(os.path.join(zsh_root_path, 'bin'), 'zsh')
	print(zsh_bin)
	workaround = f'export PATH=$PATH:{zsh_root_path}:{zsh_root_path}/bin\n[ -f "{zsh_bin}" ] && exec {zsh_bin} -l\nexit 0'

	if os.path.exists(bashrc_path):
		move(bashrc_path, bashrc_path + '.orig')

	bashrc_f = open(bashrc_path, 'w')
	bashrc_f.write(workaround)
	bashrc_f.close()

	if os.path.exists(profile_path):
		move(profile_path, profile_path + '.orig')

	profile_f = open(profile_path, 'w')
	profile_f.write(workaround)
	profile_f.close()

print('\nInstall Complete!')
exit(0)
