#!/bin/sh

# Sanity checks
[ "$(id -u)" -eq 0 ] && printf "This script cannot be run as root." >&2 && exit 1

dependencies='tar make curl'
for dep in $dependencies; do
	command -v "$dep" >/dev/null || (printf "Missing dependency: %s\n" "$dep" && exit 2)
done


# Arguments parsing
while getopts 'bhp:w' opt; do
	case "$opt" in
		'b')
			BYPASS_CHECK=1
			;;
		'h')
			cat << EOF
usage: $(basename "$0") [OPTION] <version>

Options:
	-b		bypass checks after compilation.
	-h		shows this help message.
	-p <path>	sets <path> as zsh_root instead of ~/zsh.
	-w 		activate shell's startup workaround.
EOF
			exit 0
			;;
		'p')
			zsh_root="$OPTARG"
			;;
		'w')
			SET_WORKAROUND=1
			;;
	esac
done
shift "$((OPTIND - 1))"

if [ $# -gt 1 ]; then
	echo 'Too many arguments.' >&2
	exit 3
elif [ $# -eq 1 ]; then
	version="zsh/$1/zsh-$1.tar.xz/download"
else
	version='latest'
fi

zsh_root=${zsh_root:-~/zsh}
src_url="https://sourceforge.net/projects/zsh/files/$version"
#if args.zsh_version == 'latest' else f'https://sourceforge.net/projects/zsh/files/zsh/{args.zsh_version}

compile="./configure --prefix=${zsh_root} --enable-multibyte --enable-function-subdirs --enable-fndir=${zsh_root}/usr/share/zsh/functions"

# Entering in build env
cd "$(mktemp -d)" || (printf 'Failed to cd.' && exit 130)

# Downloading source
# TODO: use "file" to detect file type. Let filename-match be a contingency solution.
curl -LJO "$src_url"
filename=$(ls zsh*)
echo "$filename"
case $filename in
	*.tar.xz)
		echo "XZ detected"
		tar Jxvf "$filename"
		;;
	*.tar.gz)
		echo "GZ detected"
		tar zxvf "$filename"
		;;
	*.tar.bz2)
		echo "BZ2 detected"
		tar jxvf "$filename"
		;;
	*)
		echo "Unable to decompress archive." >&2
		exit 4
		;;
esac

find . -type d -maxdepth 1 -name zsh-\* -exec mv '{}' zsh-sources \;
cd zsh-sources || exit 130
pwd

$compile && make
[ -n "$BYPASS_CHECK" ] || make check
[ "$?" -eq 0 ] && make install


# Set workaround, if specified.
if [ "$?" -eq 0 ] && [ -n "$SET_WORKAROUND" ]; then
	cat <<- EOF >> $HOME/.bashrc
	export $PATH:${zsh_root}/bin
	[ -x ${zsh_root}/bin/zsh ] && exec ${zsh_root}/bin/zsh -l && exit 0
	EOF
fi
