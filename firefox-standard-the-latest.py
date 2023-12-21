#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#**********************************************************************************
#*                                                                                *
#*                          Firefox Standard The Latest                           *
#*          ------------------------------------------------------------          *
#*                                                                                *
#**********************************************************************************
# Copyright 2023 Antonio Leal, Porto Salvo, Portugal
# All rights reserved.
#
# Redistribution and use of this script, with or without modification, is
# permitted provided that the following conditions are met:
#
# 1. Redistributions of this script must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#
#  THIS SOFTWARE IS PROVIDED BY THE AUTHOR "AS IS" AND ANY EXPRESS OR IMPLIED
#  WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
#  MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.  IN NO
#  EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#  SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
#  PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
#  OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
#  WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
#  OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
#  ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# $Id:$


#**********************************************************************************
#*                                                                                *
#*                                    Libraries                                   *
#*                                                                                *
#**********************************************************************************
import os
import time
import sys
import xml.etree.ElementTree as ET
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

#**********************************************************************************
#*                                                                                *
# Globals                                                                         *
#*                                                                                *
#**********************************************************************************
# Program variables
DOWNLOAD_LINK = "https://download.mozilla.org/?product=firefox-latest&os=linux64&lang=en-US"
BZ2_FILE = 'firefox-standard.tar.bz2'
APP_PATH = '/opt/firefox-standard-the-latest'
LASTRUN = APP_PATH + '/lastrun'
A_DAY_IN_SECONDS = 86400

MESSAGE_1 = """Hey, whatismybrowser.com reported a new Firefox Standard release.

Your version : %s
New version  : %s

Do you want to install it?
"""
MESSAGE_2 = """Firefox Standard is now at version %s
Please review the installation output below:
"""
MESSAGE_3 = """Firefox Standard versions available.

Your version   : %s
Latest version : %s

You can now install it for the first time or, if
applicable, upgrade to the newest version.
"""
command_confirm_upgrade = False
command_manual_install = False
builder = None

#**********************************************************************************
#*                                                                                *
#                                  Gui Handlers                                   *
#*                                                                                *
#**********************************************************************************
class ManualHandler:
    def onDestroy(self, *args):
        Gtk.main_quit()
    def onButtonInstallPressed(self, ButtonInstall):
        global builder, command_manual_install
        window = builder.get_object("manual-dialog")
        window.hide()
        Gtk.main_quit()
        command_manual_install = True
    def onButtonQuitPressed(self, ButtonQuit):
        Gtk.main_quit()

class PermissionHandler:
    def onDestroy(self, *args):
        Gtk.main_quit()
    def onButtonYesPressed(self, ButtonYes):
        global builder, command_confirm_upgrade
        window = builder.get_object("permission-dialog")
        window.hide()
        Gtk.main_quit()
        command_confirm_upgrade = True
    def onButtonNoPressed(self, ButtonNo):
        global command_confirm_upgrade
        Gtk.main_quit()
        command_confirm_upgrade = False

class EndHandler:
    def onDestroy(self, *args):
        Gtk.main_quit()
    def onButtonOKPressed(self, ButtonOK):
        Gtk.main_quit()

class NoVersionHandler:
    def onDestroy(self, *args):
        Gtk.main_quit()
    def onButtonDonePressed(self, ButtonDone):
        Gtk.main_quit()

#**********************************************************************************
#*                                                                                *
#                                    Dialogs                                      *
#*                                                                                *
#**********************************************************************************
def manual_dialog(current_version, new_version):
    global builder
    builder = Gtk.Builder()
    builder.add_from_file("manual-dialog.glade")
    builder.connect_signals(ManualHandler())
    window = builder.get_object("manual-dialog")
    LabelMessage = builder.get_object("LabelMessage")
    LabelMessage.set_text(MESSAGE_3 % (current_version, new_version))
    window.show_all()
    Gtk.main()

def permission_dialog(current_version, new_version):
    global builder
    builder = Gtk.Builder()
    builder.add_from_file("permission-dialog.glade")
    builder.connect_signals(PermissionHandler())
    window = builder.get_object("permission-dialog")
    LabelMessage = builder.get_object("LabelMessage")
    LabelMessage.set_text(MESSAGE_1 % (current_version, new_version))
    window.show_all()
    Gtk.main()

def end_dialog(new_version, log):
    global builder
    builder = Gtk.Builder()
    builder.add_from_file("end-dialog.glade")
    builder.connect_signals(EndHandler())
    window = builder.get_object("end-dialog")
    Log = builder.get_object("Label")
    Log.set_text(MESSAGE_2 % new_version)
    Log = builder.get_object("Log")
    Log.get_buffer().set_text(log)
    window.show_all()
    Gtk.main()

def no_version_dialog():
    global builder
    builder = Gtk.Builder()
    builder.add_from_file("no-version-dialog.glade")
    builder.connect_signals(NoVersionHandler())
    window = builder.get_object("no-version-dialog")
    window.show_all()
    Gtk.main()

#**********************************************************************************
#*                                                                                *
#                               Core functions                                    *
#*                                                                                *
#**********************************************************************************

# Check the current installed version, if there is one...
def get_current_version():
    try:
        current_version = os.popen("ls /var/log/packages/mozilla-firefox-standard-* | awk -F - '{print $4}'").read().split()[0].strip()
    except:
        current_version = 'not found'
    return current_version

# Check the web for latest Firefox Standard version.
def get_web_version():
    try:
        # We are expecting sometning like:
        # xmlstr = """
        #                        <tr>
        #                            <td>Firefox <strong>Standard Release</strong></td>
        #                            <td>Desktop</td>
        #                            <td>120.0.1</td>
        #                            <td>2023-11-30</td>
        #                        </tr>
        # """
        xmlstr=os.popen('curl -s https://www.whatismybrowser.com/guides/the-latest-version/firefox | grep -B 1 -A 4 "<td>Firefox <strong>Standard Release</strong></td>"').read()
        root = ET.fromstring(xmlstr)
        web_version = root[2].text.strip()
    except:
        web_version = 'undetermined'
    return web_version
    
# Download from mozi and confirm the release version
def get_new_version():
    os.system('/usr/bin/wget -O firefox-standard.tar.bz2 "%s"' % DOWNLOAD_LINK)
    return os.popen('tar -xOf firefox-standard.tar.bz2 firefox/application.ini | grep "^Version="').read().strip().split('=')[1].strip()

# Create a slackware package
def pack(version):
    os.system('rm -rf pkg/opt')
    os.system('mkdir -p pkg/opt')
    os.system('tar -xf firefox-standard.tar.bz2')
    os.system('mv firefox pkg/opt/firefox-standard')
    os.system('mkdir -p pkg/opt/firefox-standard/distribution')
    os.system('cp policies.json pkg/opt/firefox-standard/distribution')
    return os.popen("cd pkg && /sbin/makepkg -l y -c n /tmp/mozilla-firefox-standard-%s-x86_64-1_SBo.tgz" % version).read()

# Installing on you box
def install(version):
    return os.popen("/sbin/upgradepkg --install-new /tmp/mozilla-firefox-standard-%s-x86_64-1_SBo.tgz" % version).read()

# remove rpm file
def cleanup():
    os.system('rm -rf pkg/opt/firefox-standard')
    os.system('rm -rf firefox-standard.tar.bz2')

#**********************************************************************************
#*                                                                                *
#                                Main Function                                    *
#*                                                                                *
#**********************************************************************************
def main():
    global command_confirm_upgrade, command_manual_install
    os.chdir(APP_PATH)

    # Check if you are root
    if os.geteuid() != 0:
        print('You must run this script as root.')
        exit(0)
    
    # Read program arguments
    param_silent = False
    param_install_or_upgrade = False
    param_show_gui = False
    for a in sys.argv:
        if 'GUI' == a.upper():
            param_show_gui = True
        if 'INSTALL' == a.upper() or 'UPGRADE' == a.upper() or 'UPDATE' == a.upper():
            param_install_or_upgrade = True
        if 'SILENT' == a.upper():
            param_silent = True

    # Exit if $DISPLAY is not set
    if len(os.popen("echo $DISPLAY").read().strip()) == 0 and not param_silent:
        print('In order to run you must have an XServer running, otherwise use the "silent" program argument.')
        exit(0)

    # Only run once a day, even though we set cron.hourly
    if os.path.exists(LASTRUN) and not (param_install_or_upgrade or param_show_gui):
        ti_m = os.path.getmtime(LASTRUN)
        ti_n = time.time()
        if (ti_n - ti_m) < A_DAY_IN_SECONDS:
            exit(0)
    os.system('touch %s' % LASTRUN)

    # Core processing
    current_version = get_current_version()
    if param_show_gui:
        new_version = get_new_version()
        if current_version != new_version:
            manual_dialog(current_version, new_version)
            if command_manual_install:
                log = pack(new_version)
                log = log + install(new_version)
                end_dialog(new_version, log)
        else:
            no_version_dialog()
        cleanup()
    else:
        web_version = get_web_version()
        if current_version != web_version or param_install_or_upgrade:
            new_version = get_new_version()
            if current_version != new_version or param_install_or_upgrade:
                if not param_silent:
                    permission_dialog(current_version, new_version)
                else:
                    command_confirm_upgrade = True
                if command_confirm_upgrade:
                    log = pack(new_version)
                    log = log + install(new_version)
                    if not param_silent:
                        end_dialog(new_version, log)
            cleanup()

if __name__ == '__main__':
    # tests:
    #print("Web Version >>>", get_web_version())
    #print("Current Version >>>", get_current_version())
    #print("New Version >>>", get_new_version())

    main()
