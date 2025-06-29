#!/usr/bin/env python

import os
from commands import getoutput
from platform import system as getOS
from sys import stderr, argv
from argparse import ArgumentParser
from time import sleep

# Setup Arguments

parser = ArgumentParser()

parser.add_argument("zsh_version", type=str)
parser.add_argument("-w", "--force-wget", help="Force download with wget", action="store_true")
parser.add_argument("--debug", help="Get Debug Messages", action="store_true")
parser.add_argument("--install-only", help="Installs only the ZSH", action="store_true")

args = parser.parse_args()

# Basic Functions

# which tries to recreate the "which" built-in bash command
# Usage: which("cmd_to_search", returnPath=True|False)
# returnPath default value is "False". If is set on true
# will return:
# In case of success --> The path of cmd
# Otherwise --> None

def which(cmd, returnPath=False):
    for path in os.environ["PATH"].split(os.pathsep):
        if os.path.exists(os.path.join(path,cmd)):
            if not returnPath:
                return True
            return os.path.join(path,cmd)
    if not returnPath:
        return False
    return None

def dw():
    if args.force_wget:
        return "wget --trust-server-names"
    _os = getOS()
    if _os == "Darwin":
        return "open -a safari"
    elif _os == "Linux":
        if getoutput("gsettings get org.gnome.system.proxy mode") == "'none'":
            return "wget --trust-server-names"
        elif os.path.exists("/etc/debian_version"):
            return "x-www-browser"
        elif (os.path.exists("/usr/bin/firefox") or which("firefox")):
            return which("firefox", True)
        else:
            return "xdg-open"
    else:
        return "NULL"

def getDownloadDir():
    if getOS() == "Darwin":
        return os.getenv("HOME") + "/Downloads"
    elif getOS() == "Linux":
        if os.path.exists(os.getenv("HOME") + "/Downloads"):
            return os.getenv("HOME") + "/Downloads"
        elif os.path.exists(os.getenv("HOME") + "/Scaricati"):
            return os.getenv("HOME") + "/Scaricati"
        else:
            return os.getenv("HOME")

def intOrFloat(str):
    for i in str:
        if i == '.':
            return "Float"
    return "Int"

if os.geteuid() == 0:
    print >>stderr, "This script cannot be run as root."
    exit(1)

if not which("tar"):
    print >>stderr, "Fatal Error: Tar not found."
    exit(2)

if not which("make"):
    print >>stderr, "Fatal Error: Make not found."
    exit(2)

# Basic Variables

home = os.environ.get('HOME') + '/'
zsh = home + "zsh/"
url = "http://sourceforge.net/projects/zsh/files/latest/download?source=files"
try:
    #zsh_version = args.zsh_version
    if intOrFloat(args.zsh_version) == "Int":
        zsh_version = int(args.zsh_version)
    else:
        zsh_version = float(args.zsh_version)
except ValueError:
    print >>stderr, "Invalid Input."
    exit(3)

new_url = "http://www.zsh.org/pub/zsh-" + str(zsh_version) + ".tar.xz"
source_dir = getDownloadDir() + "/zsh-" + str(zsh_version)

# Debug

if args.debug:
    print "\n### DEBUG SCREEN ###"
    print "Home: ", home
    print "ZSH DEST: ", zsh
    print "URL: ", url
    print "ZSH_VERSION: ", zsh_version
    print "New URL: ", new_url
    print "Download Manager: ", dw()
    print "Source Dir: ", source_dir
    print ""

# Fetching Source code and extracting it

try:
    os.chdir(getDownloadDir())
    if not os.path.exists(source_dir + ".tar.xz"):
        os.system(dw() + " " + new_url)
        if dw() != "wget --trust-server-names":
            for i in range(0,20):
                try:
                    if os.path.exists(source_dir + ".tar.xz"):
                        break
                    sleep(5)
                    if i == 19:
                        print >>stderr, "\nUnable to download Zsh package."
                        exit(5)
                except KeyboardInterrupt as e:
                    x = raw_input("Are you sure you want to quit? [y/N] ")
                    if x == "y" or x == "N":
                        exit(0)
                    else:
                        continue

    if os.path.exists(source_dir + ".tar.xz"):
        os.system("tar -Jxf zsh-" + str(zsh_version) + ".tar.xz")
        os.chdir(source_dir)
    else:
        print >>stderr, "\nImpossible to find \"" + source_dir + ".tar.xz\""
        exit(4)
except OSError:
    print >>stderr, "\nDirectory Internal Error."
    print >>stderr, "\nDebug\nDownload Dir: ", getDownloadDir()
    print >>stderr, "Source Dir: ", source_dir
    exit(4)

# Creating Root for ZSH

if not os.path.exists(zsh):
    try:
        os.mkdir(zsh, 0755)
        os.mkdir(zsh + "bin", 0755)
        os.mkdir(zsh + "etc", 0755)
        os.mkdir(zsh + "lib", 0755)
        os.mkdir(zsh + "share", 0755)
        os.mkdir(zsh + "share/lib", 0755)
        os.mkdir(zsh + "share/share", 0755)
        os.mkdir(zsh + "usr", 0755)
    except OSError as e:
        print >>stderr, "Error during dir creation."
        exit(4)
    else:
        print "\"" + zsh + "\" root created."
else:
    print >>stderr, "\"" + zsh + "\" already exists."
    exit(5)

# Compile & Install Zsh

if not os.getcwd() == source_dir:
    print >>stderr, "Unexpected Internal Error."
    exit(1)

compile_cmd = "./configure --prefix=" + zsh + " --enable-multibyte --enable-function-subdirs --enable-fndir=" + zsh + "/usr/share/zsh/functions --enable-scriptdir=" + zsh + "/usr/share/zsh/scripts --with-tcsetpgrp --enable-pcre --enable-cap --enable-zsh-secure-free --enable-etcdir=" + zsh + "/etc/zsh"
#install_cmd = "make && make check && make install"
generate_cmd = "make"
check_cmd = "make check"
install_cmd = "make install"

if args.debug:
    print "\nCompile Debug"
    print "Compile Cmd: ", compile_cmd
    print "Install Cmd: ", install_cmd

print "Compiling ZSH..."
os.system(compile_cmd)
os.system(generate_cmd)
os.system(check_cmd)
os.system(install_cmd)

del compile_cmd
del install_cmd

# User preferences

pref = raw_input("\nDo you want to setup the ZSH as your default Shell? [Y/n] ")
if pref == 'n' or pref == 'N':
    print ""
else:
    profile_f = open(os.getenv("HOME") + "/.profile", "w")
    profile_f.write("[ -f " + zsh + " ] && exec " + zsh + " -l")
    profile_f.close()

del pref

print "\n\nInstall Complete!"
exit(0)
