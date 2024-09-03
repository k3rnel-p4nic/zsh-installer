zsh-installer
=============
This script has been created to solve a very specific problem: I had access to a Linux machine as a regular user and couldn't install zsh on it. However, by compiling the application and setting up ~/.bashrc and ~/.bash_profile I was very confident that a layout similar to an 'installation' could have been achieved: I was right.

Thus, the scripts.
An initial Bash version solved the problem, but I thought that a Python version would have been a better idea: it worked, but always felt hacky. So, since in the meanwhile (~10 years ago...) the original Bash script was lost, I rewrote it as a fully POSIX-compliant shell script.

# zsh_installer.py
The purpose of this Python script is to fetch a zsh tarball (a specified one, or the latest available otherwise), compile it, install it and eventually apply a workaround to set it as 'default shell'.

Originally wrote when Python 3.4 came out, somewhere in the future to fix minor bugs and improve its readability (f-strings).

## Usage
Its usage is really simple:
```
$ python3 zsh_installer.py <version>
```

Additional parameters:
```
$ python3 zsh_installer.py -h
usage: zsh_installer.py [-h] [--debug] [-d DOWNLOAD_DIR] [-p ZSH_PATH] [--set-default-workaround] zsh_version

positional arguments:
  zsh_version

options:
  -h, --help            show this help message and exit
  --debug               Get debug messages
  -d DOWNLOAD_DIR, --download-dir DOWNLOAD_DIR
                        Set a custom download dir
  -p ZSH_PATH, --zsh-path ZSH_PATH
                        Set a different position to the zsh root path
  --set-default-workaround
                        Using a workaround, set ZSH as default shell.
```

## License
zsh_installer.py has been released under 3-clause BSD license.


# zsh_installer.sh
The purpose of this script is to fetch a zsh tarball (a specified one, or the latest available otherwise), compile it, install it and eventually apply a workaround to set it as 'default shell'.

## Usage
To retrieve and install the latest release available:
```
$ zsh_installer.sh
```

To retrieve and install zsh version 5.4.1:
```
$ zsh_installer.sh 5.4.1
```

To install ```zsh``` in a different path:
```
$ zsh_installer.sh -p <path>
```

To install ```zsh``` and apply the workaround:
```
$ zsh_installer.sh -w
```

```make check``` might fail under certain conditions: a specific flag to circumvent it has been created:
```
$ zsh_installer.sh -b
```

## License
zsh_installer.sh is released under GNU GPL v3.
