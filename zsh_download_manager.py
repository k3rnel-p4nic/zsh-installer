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

from urllib.request import urlretrieve, urlopen
from urllib.parse import urlparse

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