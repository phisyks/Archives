#!/usr/bin/env python
#
# Reconstructor -- http://reconstructor.aperantis.com
#    Copyright (c) 2006-2007  Reconstructor Team <reconstructor@aperantis.com>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

import sys
import os
import time
import shutil
import optparse
import locale
import gettext
import re
import commands
import urllib
sys.path.append(os.getcwd() + '/lib/')
# import Reconstructor modules
from Reconstructor.PackageHelper import PackageHelper

try:
     import pygtk
     pygtk.require("2.0")
except Exception, detail:
    print detail
    pass
try:
    import gtk
    import gtk.glade
    import gobject
    import pango
except Exception, detail:
    print detail
    sys.exit(1)


class Reconstructor:

    """Reconstructor - Creates custom ubuntu cds..."""
    def __init__(self):
        # vars
        self.gladefile = os.getcwd() + '/glade/gui.glade'
        self.iconFile = os.getcwd() + '/glade/app.png'
        self.logoFile = os.getcwd() + '/glade/reconstructor.png'
        self.terminalIconFile = os.getcwd() + '/glade/terminal.png'
        self.updateIconFile = os.getcwd() + '/glade/update.png'

        self.appName = "Reconstructor"
        self.codeName = " \"Chartres\" "
        self.devInProgress = False
        self.updateId = "320"
        self.donateUrl = "https://www.paypal.com/cgi-bin/webscr?cmd=_xclick&business=ejhazlett%40gmail%2ecom&item_name=Reconstructor%20Donation&item_number=R_DONATE_001&no_shipping=2&no_note=1&tax=0&currency_code=USD&lc=US&bn=PP%2dDonationsBF&charset=UTF%2d8"
        #self.devRevision = time.strftime("%y%m%d", time.gmtime())
        self.devRevision = "070513"
        self.appVersion = "2.6"
        self.cdUbuntuVersion = ''
        self.altCdUbuntuVersion = ''
        self.altCdUbuntuArch = ''
        self.altCdUbuntuDist = ''
        self.ubuntuCodename = ''
        self.dapperVersion = '6.06'
        self.edgyVersion = '6.10'
        self.feistyVersion = '7.04'
        self.moduleDir = os.getcwd() + '/modules/'
        self.mountDir = '/media/cdrom'
        self.tmpDir = "tmp"
        self.altRemasterDir = "remaster_alt"
        self.altInitrdRoot = "initrd_alt"
        self.altRemasterRepo = "remaster_alt_repo"
        self.tmpPackageDir = "tmp_packages"
        # Alternate GPG Key vars
        self.altGpgKeyName = "Alternate Installation Automatic Signing Key"
        self.altGpgKeyComment = "Reconstructor Automatic Signing Key"
        #self.altGpgKeyEmail = "reconstructor@aperantis.com"
        #self.altGpgKeyPhrase = "titan"
        #self.altGpgKey = self.altGpgKeyName + " (" + self.altGpgKeyComment + ") <" + self.altGpgKeyEmail + ">"
        # type of disc (live/alt)
        self.discType = ""
        self.altBaseTypeStandard = 0
        self.altBaseTypeServer = 1
        self.altBaseTypeDesktop = 2
        self.customDir = ""
        self.createRemasterDir = False
        self.createCustomRoot = False
        self.createInitrdRoot = False
        self.createAltRemasterDir = False
        self.createAltInitrdRoot = False
        self.isoFilename = ""
        self.buildLiveCdFilename = ''
        self.setupComplete = False
        self.manualInstall = False
        self.watch = gtk.gdk.Cursor(gtk.gdk.WATCH)
        self.working = None
        self.workingDlg = None
        self.runningDebug = False
        self.interactiveEdit = False
        self.pageWelcome = 0
        self.pageDiscType = 1
        self.pageLiveSetup = 2
        self.pageLiveCustomize = 3
        self.pageLiveCustomizeGnome = 1
        self.pageLiveCustomizeOptimization = 3
        self.pageLiveBuild = 4
        self.pageAltSetup = 5
        self.pageAltCustomize = 6
        self.pageAltBuild = 7
        self.pageFinish = 8
        self.gdmBackgroundColor = None
        self.enableExperimental = False
        self.gnomeBinPath = '/usr/bin/gnome-session'
        self.f = sys.stdout
        self.webUrl = "http://reconstructor.aperantis.com"
        self.updateInfo = "http://reconstructor.aperantis.com/update/info"
        self.updateFile = "http://reconstructor.aperantis.com/update/update.tar.gz"
        self.treeModel = None
        self.treeView = None

        self.modEngineKey = 'RMOD_ENGINE'
        self.modCategoryKey = 'RMOD_CATEGORY'
        self.modSubCategoryKey = 'RMOD_SUBCATEGORY'
        self.modNameKey = 'RMOD_NAME'
        self.modAuthorKey = 'RMOD_AUTHOR'
        self.modDescriptionKey = 'RMOD_DESCRIPTION'
        self.modVersionKey = 'RMOD_VERSION'
        self.modRunInChrootKey = 'RMOD_RUN_IN_CHROOT'
        self.modUpdateUrlKey = 'RMOD_UPDATE_URL'
        self.modules =  {}

        self.regexUbuntuVersion = '^DISTRIB_RELEASE=([0-9.]+)\n'
        self.regexModEngine = '^RMOD_ENGINE=([A-Za-z0-9.\s\w]+)\n'
        self.regexModCategory = '^RMOD_CATEGORY=([A-Za-z0-9\'\"\w]+)\s'
        self.regexModSubCategory = '^RMOD_SUBCATEGORY=([A-Za-z0-9\'\"\w]+)\s'
        self.regexModName = '^RMOD_NAME=([A-Za-z0-9.\-\&\,\*\/\(\)\'\"\s\w]+)\n'
        self.regexModAuthor = '^RMOD_AUTHOR=([A-Za-z0-9.\(\)\'\":\s\w]+)\n'
        self.regexModDescription = '^RMOD_DESCRIPTION=([A-Za-z0-9.\-\&\*\_\,\/\\(\)\'\"\s\w]+)\n'
        self.regexModVersion = '^RMOD_VERSION=([A-Za-z0-9.\s\w]+)\s'
        self.regexModRunInChroot = '^RMOD_RUN_IN_CHROOT=([A-Za-z0-9\w]+)\s'
        self.regexModUpdateUrl = '^RMOD_UPDATE_URL=([A-Za-z0-9:.\-\&\*\_\,\/\\(\)\'\"\s\w]+)\n'
        self.regexUbuntuAltCdVersion = '^[a-zA-Z0-9-.]*\s+([0-9.]+)\s+'
        self.regexUbuntuAltCdInfo = '([\w-]+)\s+(\d+.\d+)\s+\D+Release\s(\w+)\s+'
        self.regexUbuntuAltPackages = '^Package:\s+(\S*)\n'

        self.iterCategoryAdministration = None
        self.iterCategoryEducation = None
        self.iterCategorySoftware = None
        self.iterCategoryServers = None
        self.iterCategoryGraphics = None
        self.iterCategoryMultimedia = None
        self.iterCategoryPlugins = None
        self.iterCategoryProductivity = None
        self.iterCategoryNetworking = None
        self.iterCategoryVirtualization = None
        self.iterCategoryMisc = None
        self.moduleColumnCategory = 0
        self.moduleColumnExecute = 1
        self.moduleColumnRunOnBoot = 2
        self.moduleColumnName = 3
        self.moduleColumnVersion = 4
        self.moduleColumnAuthor = 5
        self.moduleColumnDescription = 6
        self.moduleColumnRunInChroot = 7
        self.moduleColumnUpdateUrl = 8
        self.moduleColumnPath = 9
        self.execModulesEnabled = False
        self.bootModulesEnabled = False
        # time command for timing operations
        self.timeCmd = commands.getoutput('which time') + ' -f \"\nBuild Time: %E  CPU: %P\n\"'

        # startup daemon list for speedup
        #self.startupDaemons = ('ppp', 'hplip', 'cupsys', 'festival', 'laptop-mode', 'nvidia-kernel', 'rsync', 'bluez-utils', 'mdadm')
        # shutdown scripts - without the 'K' for looping -- see  https://wiki.ubuntu.com/Teardown  for explanation
        self.shutdownScripts = ('11anacron', '11atd', '19cupsys', '20acpi-support', '20apmd', '20bittorrent', '20dbus', '20festival', '20hotkey-setup', '20makedev', '20nvidia-kernel', '20powernowd', '20rsync', '20ssh', '21acpid', '21hplip', '74bluez-utils', '88pcmcia', '88pcmciautils', '89klogd', '90syslogd')

        APPDOMAIN='reconstructor'
        LANGDIR='lang'
        # locale
        locale.setlocale(locale.LC_ALL, '')
        gettext.bindtextdomain(APPDOMAIN, LANGDIR)
        gtk.glade.bindtextdomain(APPDOMAIN, LANGDIR)
        gtk.glade.textdomain(APPDOMAIN)
        gettext.textdomain(APPDOMAIN)
        gettext.install(APPDOMAIN, LANGDIR, unicode=1)

        # setup glade widget tree
        self.wTree = gtk.glade.XML(self.gladefile, domain='reconstructor')


        # check for user
        if os.getuid() != 0 :
            self.wTree.get_widget("windowMain").hide()

        # create signal dictionary and connect
        dic = { "on_buttonNext_clicked" : self.on_buttonNext_clicked,
            "on_buttonBack_clicked" : self.on_buttonBack_clicked,
            "on_buttonBrowseWorkingDir_clicked" : self.on_buttonBrowseWorkingDir_clicked,
            "on_buttonBrowseIsoFilename_clicked" : self.on_buttonBrowseIsoFilename_clicked,
            "on_checkbuttonBuildIso_toggled" : self.on_checkbuttonBuildIso_toggled,
            "on_buttonBrowseLiveCdFilename_clicked" : self.on_buttonBrowseLiveCdFilename_clicked,
            "on_buttonBrowseUsplashFilename_clicked" : self.on_buttonBrowseUsplashFilename_clicked,
            "on_buttonBrowseGnomeDesktopWallpaper_clicked" : self.on_buttonBrowseGnomeDesktopWallpaper_clicked,
            "on_buttonBrowseGnomeFont_clicked" : self.on_buttonBrowseGnomeFont_clicked,
            "on_buttonBrowseGnomeDocumentFont_clicked" : self.on_buttonBrowseGnomeDocumentFont_clicked,
            "on_buttonBrowseGnomeDesktopFont_clicked": self.on_buttonBrowseGnomeDesktopFont_clicked,
            "on_buttonBrowseGnomeDesktopTitleBarFont_clicked" : self.on_buttonBrowseGnomeDesktopTitleBarFont_clicked,
            "on_buttonBrowseGnomeFixedFont_clicked" : self.on_buttonBrowseGnomeFixedFont_clicked,
            "on_buttonImportGnomeTheme_clicked" : self.on_buttonImportGnomeTheme_clicked,
            "on_buttonImportGnomeThemeIcons_clicked" : self.on_buttonImportGnomeThemeIcons_clicked,
            "on_buttonImportGdmTheme_clicked" : self.on_buttonImportGdmTheme_clicked,
            "on_buttonBrowseGnomeSplashScreen_clicked" : self.on_buttonBrowseGnomeSplashScreen_clicked,
            "on_buttonBrowseLiveCdSplashFilename_clicked" : self.on_buttonBrowseLiveCdSplashFilename_clicked,
            "on_buttonSoftwareCalculateIsoSize_clicked" : self.on_buttonSoftwareCalculateIsoSize_clicked,
            "on_buttonSoftwareApply_clicked" : self.on_buttonSoftwareApply_clicked,
            "on_buttonInteractiveEditLaunch_clicked" : self.on_buttonInteractiveEditLaunch_clicked,
            "on_buttonInteractiveClear_clicked" : self.on_buttonInteractiveClear_clicked,
            "on_buttonUsplashGenerate_clicked" : self.on_buttonUsplashGenerate_clicked,
            "on_buttonOptimizeShutdownRestore_clicked" : self.on_buttonOptimizeShutdownRestore_clicked,
            "on_checkbuttonOptimizationStartupEnable_toggled" : self.on_checkbuttonOptimizationStartupEnable_toggled,
            "on_buttonCustomizeLaunchTerminal_clicked" : self.on_buttonCustomizeLaunchTerminal_clicked,
            "on_buttonBurnIso_clicked" : self.on_buttonBurnIso_clicked,
            "on_buttonCheckUpdates_clicked" : self.on_buttonCheckUpdates_clicked,
            "on_buttonModulesAddModule_clicked" : self.on_buttonModulesAddModule_clicked,
            "on_buttonModulesClearRunOnBoot_clicked" : self.on_buttonModulesClearRunOnBoot_clicked,
            "on_buttonBrowseAltWorkingDir_clicked" : self.on_buttonBrowseAltWorkingDir_clicked,
            "on_buttonBrowseAltIsoFilename_clicked" : self.on_buttonBrowseAltIsoFilename_clicked,
            "on_buttonAltIsoCalculate_clicked" : self.on_buttonAltIsoCalculate_clicked,
            "on_checkbuttonAltCreateRemasterDir_clicked" : self.on_checkbuttonAltCreateRemasterDir_clicked,
            "on_buttonAptRepoImportGpgKey_clicked" : self.on_buttonAptRepoImportGpgKey_clicked,
            "on_buttonAltPackagesImportGpgKey_clicked" : self.on_buttonAltPackagesImportGpgKey_clicked,
            "on_buttonAltPackagesApply_clicked" : self.on_buttonAltPackagesApply_clicked,
            "on_checkbuttonAltBuildIso_toggled" : self.on_checkbuttonAltBuildIso_toggled,
            "on_buttonBrowseAltCdFilename_clicked" : self.on_buttonBrowseAltCdFilename_clicked,
            "on_buttonDonate_clicked" : self.on_buttonDonate_clicked,
            "on_windowMain_delete_event" : gtk.main_quit,
            "on_windowMain_destroy" : self.exitApp }
        self.wTree.signal_autoconnect(dic)

        # add command option parser
        parser = optparse.OptionParser()
        parser.add_option("-d", "--debug",
                    action="store_true", dest="debug", default=False,
                    help="run as debug")
        parser.add_option("-v", "--version",
                    action="store_true", dest="version", default=False,
                    help="show version and exit")
        parser.add_option("-m", "--manual-install",
                    action="store_true", dest="manualinstall", default=False,
                    help="manually installs all .debs in apt cache before other software")
        parser.add_option("-e", "--experimental",
                    action="store_true", dest="experimental", default=False,
                    help="enable experimental features")
        parser.add_option("-u", "--update",
                    action="store_true", dest="update", default=False,
                    help="automatically update to latest version")
        (options, args) = parser.parse_args()

        if options.debug == True:
            self.runningDebug = True
            self.wTree.get_widget("notebookWizard").set_show_tabs(True)
            print _('INFO: Running Debug...')
        else:
            # hide tabs
            self.wTree.get_widget("notebookWizard").set_show_tabs(False)
        if options.version == True:
            print " "
            print self.appName + " -- (c) Reconstructor Team, 2006-2007"
            print "       Version: " + self.appVersion + " rev. " + self.updateId
            print "        http://reconstructor.aperantis.com"
            print " "
            #gtk.main_quit()
            sys.exit(0)
        if options.manualinstall == True:
            print _('INFO: Manually Installing .deb archives in cache...')
            self.manualInstall = True
        if options.experimental == True:
            print _('INFO: Enabling Experimental Features...')
            self.enableExperimental = True
        if options.update == True:
            print _('INFO: Updating...')
            self.update()

        # print copyright
        print " "
        print self.appName + " -- (c) Reconstructor Team, 2006"
        print "       Version: " + self.appVersion
        print "        http://reconstructor.aperantis.com"
        print " "

        # set icons & logo
        self.wTree.get_widget("windowMain").set_icon_from_file(self.iconFile)
        self.wTree.get_widget("imageLogo").set_from_file(self.logoFile)
        imgTerminal = gtk.Image()
        imgTerminal.set_from_file(self.terminalIconFile)
        self.wTree.get_widget("buttonCustomizeLaunchTerminal").set_image(imgTerminal)
        imgUpdate = gtk.Image()
        imgUpdate.set_from_file(self.updateIconFile)
        self.wTree.get_widget("buttonCheckUpdates").set_image(imgUpdate)
        imgModUpdate = gtk.Image()
        imgModUpdate.set_from_file(self.updateIconFile)
        self.wTree.get_widget("buttonModulesUpdateModule").set_image(imgModUpdate)

        # check for existing mount dir
        if os.path.exists(self.mountDir) == False:
            print _('INFO: Creating mount directory...')
            os.makedirs(self.mountDir)

        # set app title
        if self.devInProgress:
            self.wTree.get_widget("windowMain").set_title(self.appName + self.codeName + "  Build " + self.devRevision)
        else:
            self.wTree.get_widget("windowMain").set_title(self.appName)

        # check dependencies
        self.checkDependencies()

        # set version
        self.wTree.get_widget("labelVersion").set_text('version ' + self.appVersion)

        # hide back button initially
        self.wTree.get_widget("buttonBack").hide()
        # set default live cd text color
        self.wTree.get_widget("colorbuttonBrowseLiveCdTextColor").set_color(gtk.gdk.color_parse("#FFFFFF"))
        # set default working directory path
        self.wTree.get_widget("entryWorkingDir").set_text(os.path.join(os.environ['HOME'], "reconstructor"))
        self.wTree.get_widget("entryAltWorkingDir").set_text(os.path.join(os.environ['HOME'], "reconstructor"))
        # set default iso filenames
        self.wTree.get_widget("entryLiveIsoFilename").set_text(os.path.join(os.environ['HOME'], "ubuntu-custom-live.iso"))
        self.wTree.get_widget("entryAltBuildIsoFilename").set_text(os.path.join(os.environ['HOME'], "ubuntu-custom-alt.iso"))
        # set default descriptions
        cdDesc = _('Ubuntu Custom')
        self.wTree.get_widget("entryLiveCdDescription").set_text(cdDesc)
        self.wTree.get_widget("entryBuildAltCdDescription").set_text(cdDesc)
        # set default cd architectures
        self.wTree.get_widget("comboboxLiveCdArch").set_active(0)
        self.wTree.get_widget("comboboxAltBuildArch").set_active(0)

        # enable/disable experimental features
        if self.enableExperimental == True:
            self.wTree.get_widget("expanderGnomeInteractive").show()
            return
        else:
            self.wTree.get_widget("expanderGnomeInteractive").hide()
            return


    # Check for Application Dependencies
    def checkDependencies(self):
        print _('Checking dependencies...')
        dependList = ''
        if commands.getoutput('which mksquashfs') == '':
            print _('squashfs-tools NOT FOUND (needed for Root FS extraction)')
            dependList += 'squashfs-tools\n'
        if commands.getoutput('which chroot') == '':
            print _('chroot NOT FOUND (needed for Root FS customization)')
            dependList += 'chroot\n'
        if commands.getoutput('which mkisofs') == '':
            print _('mkisofs NOT FOUND (needed for ISO generation)')
            dependList += 'mkisofs\n'
        if commands.getoutput('which gcc') == '':
            print _('gcc NOT FOUND (needed for Usplash generation and VMWare/Qemu installation)')
            dependList += 'gcc\n'
        if commands.getoutput('which make') == '':
            print _('make NOT FOUND (needed for VMWare/Qemu installation)')
            dependList += 'make\n'
        if commands.getoutput('which rsync') == '':
            print _('rsync NOT FOUND (needed for Remastering ISO)')
            dependList += 'rsync\n'
        # dapper usplash dependency
        if os.path.exists('/usr/include/bogl') == False:
            print _('libbogl-dev NOT FOUND (needed for Dapper Usplash Generation)')
            dependList += 'libbogl-dev\n'
        # edgy usplash dependency
        if commands.getoutput('which pngtousplash') == '':
            print _('libusplash-dev NOT FOUND (needed for Usplash Generation)')
            dependList += 'libusplash-dev\n'
        # gpg
        if commands.getoutput('which gpg') == '':
            print _('gpg NOT FOUND (needed for Alternate Key Signing)')
            dependList += 'gpg\n'
        # dpkg-buildpackage
        if commands.getoutput('which dpkg-buildpackage') == '':
            print _('dpkg-dev NOT FOUND (needed for Alternate Key Package Building)')
            dependList += 'dpkg-dev\n'
        # fakeroot
        if commands.getoutput('which fakeroot') == '':
            print _('fakeroot NOT FOUND (needed for Alternate Key Package Building)')
            dependList += 'fakeroot\n'
        # apt-ftparchive
        if commands.getoutput('which apt-ftparchive') == '':
            print _('apt-utils NOT FOUND (needed for Extra Repository Generation)')
            dependList += 'apt-utils\n'
        if dependList != '':
            print _('\nThe following dependencies are not met: ')
            print dependList
            print _('Please install the dependencies and restart reconstructor.')
            # show warning dialog
            warnDlg = gtk.Dialog(title=self.appName, parent=None, flags=0, buttons=(gtk.STOCK_NO, gtk.RESPONSE_CANCEL, gtk.STOCK_YES, gtk.RESPONSE_OK))
            warnDlg.set_icon_from_file(self.iconFile)
            warnDlg.vbox.set_spacing(10)
            labelSpc = gtk.Label(" ")
            warnDlg.vbox.pack_start(labelSpc)
            labelSpc.show()
            lblText = _('  <b>Reconstructor may not work correctly.</b>\nThe following dependencies are not met: ')
            lbl = gtk.Label(lblText)
            lbl.set_use_markup(True)
            lblInfo = gtk.Label(dependList)
            lblFixText = _('Install the dependencies and restart reconstructor?')
            lblFix = gtk.Label(lblFixText)
            warnDlg.vbox.pack_start(lbl)
            warnDlg.vbox.pack_start(lblInfo)
            warnDlg.vbox.pack_start(lblFix)
            lbl.show()
            lblInfo.show()
            lblFix.show()
            #warnDlg.show()
            response = warnDlg.run()
            if response == gtk.RESPONSE_OK:
                warnDlg.destroy()
                # use apt to install
                #print 'apt-get install -y ' + dependList.replace('\n', ' ')
                installTxt = _('Installing dependencies: ')
                print installTxt + dependList.replace('\n', ' ')
                os.popen('apt-get install -y ' + dependList.replace('\n', ' '))
                sys.exit(0)
            else:
                warnDlg.destroy()

        else:
            print _('Ok.')


    # load live cd ubuntu version
    def loadCdVersion(self):
        if self.customDir != '':
            # reset version
            self.cdUbuntuVersion = 'unknown'
            # build regex
            r = re.compile(self.regexUbuntuVersion, re.IGNORECASE)
            f = file(os.path.join(self.customDir, "root/etc/lsb-release"), 'r')
            for l in f:
                if r.match(l) != None:
                    self.cdUbuntuVersion = r.match(l).group(1)
            f.close()

            print 'Ubuntu Version: ' + self.cdUbuntuVersion
            self.wTree.get_widget("labelCustomizeUbuntuLiveVersion").set_text(self.wTree.get_widget("labelCustomizeUbuntuLiveVersion").get_text() + " " + self.cdUbuntuVersion)
            if self.cdUbuntuVersion == self.edgyVersion:
                # HACK: hide optimization -- not working on edgy yet
                self.wTree.get_widget("notebookCustomize").get_nth_page(self.pageLiveCustomizeOptimization).hide()
            else:
                self.wTree.get_widget("notebookCustomize").get_nth_page(self.pageLiveCustomizeOptimization).show()
        return

    # Check for Updates (GUI)
    def checkForUpdates(self):
        urllib.urlretrieve(self.updateInfo, ".r-info")
        if os.path.exists('.r-info'):
            f = open('.r-info', 'r')
            updateVersion = f.readline()
            updateInfo = f.read()
            f.close()
            fApp = int(self.updateId)
            fUpdate = int(updateVersion)
            if fUpdate > fApp:
                updateDlg = gtk.Dialog(title=self.appName, parent=None, flags=0, buttons=(gtk.STOCK_NO, gtk.RESPONSE_NO, gtk.STOCK_YES, gtk.RESPONSE_OK))
                updateDlg.set_icon_from_file(self.iconFile)
                updateDlg.vbox.set_spacing(10)
                labelSpc = gtk.Label(" ")
                updateDlg.vbox.pack_start(labelSpc)
                labelSpc.show()
                lblNewVersion = gtk.Label('New version available...')
                updateDlg.vbox.pack_start(lblNewVersion)
                lblNewVersion.show()
                lblInfo = gtk.Label(updateInfo)
                lblInfo.set_use_markup(True)
                updateDlg.vbox.pack_start(lblInfo)
                lblInfo.show()
                lblConfirm = gtk.Label('Update?')
                updateDlg.vbox.pack_start(lblConfirm)
                lblConfirm.show()

                response = updateDlg.run()
                if response == gtk.RESPONSE_OK:
                    updateDlg.destroy()
                    self.setBusyCursor()
                    self.update(silent=True)
                    self.exitApp()
                else:
                    print _('Update cancelled...')
                    updateDlg.destroy()
            else:
                updateDlg = gtk.Dialog(title=self.appName, parent=None, flags=0, buttons=(gtk.STOCK_OK, gtk.RESPONSE_OK))
                updateDlg.set_icon_from_file(self.iconFile)
                updateDlg.vbox.set_spacing(10)
                labelSpc = gtk.Label(" ")
                updateDlg.vbox.pack_start(labelSpc)
                labelSpc.show()
                lblNewVersion = gtk.Label('Reconstructor is at the latest version.')
                updateDlg.vbox.pack_start(lblNewVersion)
                lblNewVersion.show()

                response = updateDlg.run()
                if response == gtk.RESPONSE_OK:
                    updateDlg.destroy()
                else:
                    updateDlg.destroy()

        self.setDefaultCursor()
        # cleanup
        if os.path.exists('.r-info'):
            os.popen('rm -f .r-info')
        if os.path.exists('.update.tar.gz'):
            os.popen('rm -f .update.tar.gz')

    def showDownloadProgress(self, transferCount, blockSize, totalSize):
        #f.write('------------ Download Progress ------------')
        self.f.flush()
        if (transferCount * blockSize) < totalSize:
            self.f.write(str((transferCount * blockSize) / 1000) + 'KB of ' + str(totalSize / 1000) + 'KB\n')
        else:
            # HACK: report the same size to avoid confusion by rounding
            self.f.write(str(totalSize / 1000) + 'KB of ' + str(totalSize / 1000) + 'KB\n')
        #f.write('-------------------------------------------')


    # Updates reconstructor
    def update(self,silent=False):
        try:
            # update
            #print _('Getting update info...')
            urllib.urlretrieve(self.updateInfo, ".r-info")
            if os.path.exists('.r-info'):
                f = open('.r-info', 'r')
                updateVersion = f.readline()
                updateInfo = f.read()
                f.close()
                fApp = int(self.updateId)
                fUpdate = int(updateVersion)
                #print ('Current: ' + str(fApp) + ' -- Available: ' + str(fUpdate))
                if fUpdate > fApp:
                    if silent == False:
                        print _('New version available...')
                        print updateInfo
                        updateText = _('Download and Install Update (y/n):')
                        doUpdate = raw_input(updateText)
                        if doUpdate.lower() == 'y':
                            print _('Getting update...')
                            urllib.urlretrieve(self.updateFile, ".update.tar.gz", self.showDownloadProgress)
                            print _('\nInstalling update...')
                            os.popen('tar zxf .update.tar.gz')
                            print _('Updated.  Please restart reconstructor.\n')
                        else:
                            print _('Update cancelled.')
                    else:
                        # silent passed
                        print _('Getting update...')
                        urllib.urlretrieve(self.updateFile, ".update.tar.gz", self.showDownloadProgress)
                        print _('\nInstalling update...')
                        os.popen('tar zxf .update.tar.gz')
                        print _('Updated.  Please restart reconstructor.\n')
                else:
                    print _('Reconstructor is at the latest version.\n')
                # cleanup
                if os.path.exists('.r-info'):
                    os.popen('rm -f .r-info')
                if os.path.exists('.update.tar.gz'):
                    os.popen('rm -f .update.tar.gz')
            sys.exit(0)
        except Exception, detail:
            # HACK: nasty hack - update always throws exception, so ignore...
            #print detail
            sys.exit(0)

    # Finds all available desktop environments and enables/disables options as needed
    def loadAvailableDesktops(self):
        try:
            # find gnome
            if os.path.exists(os.path.join(self.customDir, "root" + self.gnomeBinPath)):
                print _('Found Gnome Desktop Environment...')
                self.wTree.get_widget("notebookCustomize").get_nth_page(self.pageLiveCustomizeGnome).show()
                # get current gdm background color
                self.loadGdmBackgroundColor()
                # load comboboxes for customization
                self.loadGdmThemes()
                self.loadGnomeThemes()
            else:
                # gnome not found
                self.wTree.get_widget("notebookCustomize").get_nth_page(self.pageLiveCustomizeGnome).hide()
        except Exception, detail:
            print detail

    # Handle Module Properties
    def getModuleProperties(self, moduleName):
        print _('Loading module properties...')

        fMod = file(os.path.join(self.moduleDir, moduleName), 'r')

        properties = {}

        # search for mod properties
        modCategory = ''
        modSubCategory = ''
        modName = ''
        modVersion = ''
        modAuthor = ''
        modDescription = ''
        modRunInChroot = None
        modUpdateUrl = ''

      # HACK: regex through module to get info
        reModCategory = re.compile(self.regexModCategory, re.IGNORECASE)
        reModSubCategory = re.compile(self.regexModSubCategory, re.IGNORECASE)
        reModName = re.compile(self.regexModName, re.IGNORECASE)
        reModVersion = re.compile(self.regexModVersion, re.IGNORECASE)
        reModAuthor = re.compile(self.regexModAuthor, re.IGNORECASE)
        reModDescription = re.compile(self.regexModDescription, re.IGNORECASE)
        reModRunInChroot = re.compile(self.regexModRunInChroot, re.IGNORECASE)
        reModUpdateUrl = re.compile(self.regexModUpdateUrl, re.IGNORECASE)

        for line in fMod:
            if reModCategory.match(line) != None:
                modCategory = reModCategory.match(line).group(1)
            if reModSubCategory.match(line) != None:
                modSubCategory = reModSubCategory.match(line).group(1)
            if reModName.match(line) != None:
                modName = reModName.match(line).group(1)
            if reModVersion.match(line) != None:
                modVersion = reModVersion.match(line).group(1)
            if reModAuthor.match(line) != None:
                modAuthor = reModAuthor.match(line).group(1)
            if reModDescription.match(line) != None:
                modDescription = reModDescription.match(line).group(1)
            if reModRunInChroot.match(line) != None:
                modRunInChroot = reModRunInChroot.match(line).group(1)
            if reModUpdateUrl.match(line) != None:
                modUpdateUrl = reModUpdateUrl.match(line).group(1)
        fMod.close()

        # remove single and double quotes if any
        modCategory = modCategory.replace("'", "")
        modCategory = modCategory.replace('"', '')
        modSubCategory = modSubCategory.replace("'", "")
        modSubCategory = modSubCategory.replace('"', '')
        modName = modName.replace("'", "")
        modName = modName.replace('"', '')
        modAuthor = modAuthor.replace("'", "")
        modAuthor = modAuthor.replace('"', '')
        modDescription = modDescription.replace("'", "")
        modDescription = modDescription.replace('"', '')
        modUpdateUrl = modUpdateUrl.replace("'", "")
        modUpdateUrl = modUpdateUrl.replace('"', '')

        properties[self.modEngineKey] = 'None'
        properties[self.modCategoryKey] = modCategory
        properties[self.modSubCategoryKey] = modSubCategory
        properties[self.modNameKey] = modName
        properties[self.modAuthorKey] = modAuthor
        properties[self.modDescriptionKey] = modDescription
        properties[self.modRunInChrootKey] = modUpdateUrl
        properties[self.modVersionKey] = modVersion
        properties[self.modUpdateUrlKey] = modUpdateUrl

        return properties

    # Loads modules
    def loadModules(self):
        print _('Loading modules...')
        # generate model for treeview
        # create treestore of (install(bool), modulename, version, author, description, runInChroot(hidden), filepath(hidden))
        self.treeModel = None
        self.treeModel = gtk.TreeStore(gobject.TYPE_STRING, gobject.TYPE_BOOLEAN, gobject.TYPE_BOOLEAN, gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_BOOLEAN, gobject.TYPE_STRING, gobject.TYPE_STRING)
        # load categories self.treeModel
        # root categories
        self.iterCategorySoftware = self.treeModel.insert_before(None, None)
        self.treeModel.set_value(self.iterCategorySoftware, 0, 'Software')
        # administration
        self.iterCategoryAdministration = self.treeModel.insert_before(self.iterCategorySoftware, None)
        self.treeModel.set_value(self.iterCategoryAdministration, 0, 'Administration')
        # education
        self.iterCategoryEducation = self.treeModel.insert_before(self.iterCategorySoftware, None)
        self.treeModel.set_value(self.iterCategoryEducation, 0, 'Education')
        # servers
        self.iterCategoryServers = self.treeModel.insert_before(self.iterCategorySoftware, None)
        self.treeModel.set_value(self.iterCategoryServers, 0, 'Servers')
        # graphics
        self.iterCategoryGraphics = self.treeModel.insert_before(self.iterCategorySoftware, None)
        self.treeModel.set_value(self.iterCategoryGraphics, 0, 'Graphics')
        # multimedia
        self.iterCategoryMultimedia = self.treeModel.insert_before(self.iterCategorySoftware, None)
        self.treeModel.set_value(self.iterCategoryMultimedia, 0, 'Multimedia')
        # networking
        self.iterCategoryNetworking = self.treeModel.insert_before(self.iterCategorySoftware, None)
        self.treeModel.set_value(self.iterCategoryNetworking, 0, 'Networking')
        # plugins
        self.iterCategoryPlugins = self.treeModel.insert_before(self.iterCategorySoftware, None)
        self.treeModel.set_value(self.iterCategoryPlugins, 0, 'Plugins')
        # productivity
        self.iterCategoryProductivity = self.treeModel.insert_before(self.iterCategorySoftware, None)
        self.treeModel.set_value(self.iterCategoryProductivity, 0, 'Productivity')
        # virtualization
        self.iterCategoryVirtualization = self.treeModel.insert_before(self.iterCategorySoftware, None)
        self.treeModel.set_value(self.iterCategoryVirtualization, 0, 'Virtualization')
        # miscellaneous
        self.iterCategoryMisc = self.treeModel.insert_before(self.iterCategorySoftware, None)
        self.treeModel.set_value(self.iterCategoryMisc, 0, 'Miscellaneous')

        # load modules into the treestore
        for root, dirs, files in os.walk(self.moduleDir):
                for f in files:
                    r, ext = os.path.splitext(f)
                    if ext == '.rmod':
                        print 'Module: ' + f.replace('.rmod', '') + ' found...'

                        modPath = os.path.join(self.moduleDir, f)

                        # Refactoring! triplem
                        modProps = self.getModuleProperties(f)
                        modSubCategory = modProps[self.modSubCategoryKey]

                        if self.modules.has_key(modProps[self.modNameKey]):
                            print "The module is already present"

                        self.modules[modProps[self.modNameKey]] = modProps

                        # load into self.treeModel
                        #iter = self.treeModel.insert_before(iterCatOther, None)
                        if modSubCategory == 'Administration':
                            iter = self.treeModel.insert_before(self.iterCategoryAdministration, None)
                        elif modSubCategory == 'Education':
                            iter = self.treeModel.insert_before(self.iterCategoryEducation, None)
                        elif modSubCategory == 'Servers':
                            iter = self.treeModel.insert_before(self.iterCategoryServers, None)
                        elif modSubCategory == 'Graphics':
                            iter = self.treeModel.insert_before(self.iterCategoryGraphics, None)
                        elif modSubCategory == 'Multimedia':
                            iter = self.treeModel.insert_before(self.iterCategoryMultimedia, None)
                        elif modSubCategory == 'Networking':
                            iter = self.treeModel.insert_before(self.iterCategoryNetworking, None)
                        elif modSubCategory == 'Plugins':
                            iter = self.treeModel.insert_before(self.iterCategoryPlugins, None)
                        elif modSubCategory == 'Productivity':
                            iter = self.treeModel.insert_before(self.iterCategoryProductivity, None)
                        elif modSubCategory == 'Virtualization':
                            iter = self.treeModel.insert_before(self.iterCategoryVirtualization, None)
                        else:
                            iter = self.treeModel.insert_before(self.iterCategoryMisc, None)

                        self.treeModel.set_value(iter, self.moduleColumnExecute, False)
                        self.treeModel.set_value(iter, self.moduleColumnRunOnBoot, False)
                        self.treeModel.set_value(iter, self.moduleColumnName, modProps[self.modNameKey])
                        self.treeModel.set_value(iter, self.moduleColumnVersion, modProps[self.modVersionKey])
                        self.treeModel.set_value(iter, self.moduleColumnAuthor, modProps[self.modAuthorKey])
                        self.treeModel.set_value(iter, self.moduleColumnDescription, modProps[self.modDescriptionKey])
                        self.treeModel.set_value(iter, self.moduleColumnRunInChroot, bool(modProps[self.modRunInChrootKey]))
                        self.treeModel.set_value(iter, self.moduleColumnUpdateUrl, modProps[self.modUpdateUrlKey])
                        self.treeModel.set_value(iter, self.moduleColumnPath, modPath)
                        #print modName, modVersion, modAuthor, modDescription, modUseXterm, modRunInChroot, modPath
                        # set default sort by category
                        self.treeModel.set_sort_column_id(self.moduleColumnCategory, gtk.SORT_ASCENDING)
                        # build treeview
                        view = self.treeView
                        view = gtk.TreeView(self.treeModel)
                        view.get_selection().set_mode(gtk.SELECTION_SINGLE)
                        view.set_property('search-column', self.moduleColumnName)
                        view.set_reorderable(False)
                        view.set_enable_search(True)
                        view.set_headers_clickable(True)
                        view.set_rules_hint(True)
                        view.connect("row-activated", self.on_treeitem_row_activated)
                        self.wTree.get_widget("buttonModulesViewModule").connect("clicked", self.on_buttonModulesViewModule_clicked, view)
                        self.wTree.get_widget("buttonModulesUpdateModule").connect("clicked", self.on_buttonModulesUpdateModule_clicked, view)
                        #view.set_model(model)
                        # category column
                        rendererCategory = gtk.CellRendererText()
                        categoryText = _('Category')
                        columnCategory = gtk.TreeViewColumn(categoryText, rendererCategory, text=self.moduleColumnCategory)
                        columnCategory.set_sort_column_id(self.moduleColumnCategory)
                        view.append_column(columnCategory)
                        # execute column
                        rendererExecute = gtk.CellRendererToggle()
                        rendererExecute.set_property('activatable', True)
                        rendererExecute.connect("toggled", self.on_treeitemExecute_toggled, self.treeModel)
                        executeText = _('Execute')
                        columnExecute = gtk.TreeViewColumn(executeText, rendererExecute, active=self.moduleColumnExecute)
                        view.append_column(columnExecute)
                        # run on boot
                        rendererRunOnBoot = gtk.CellRendererToggle()
                        rendererRunOnBoot.set_property('activatable', True)
                        rendererRunOnBoot.connect("toggled", self.on_treeitemRunOnBoot_toggled, self.treeModel)
                        runOnBootText = _('Run on boot')
                        columnRunOnBoot = gtk.TreeViewColumn(runOnBootText, rendererRunOnBoot, active=self.moduleColumnRunOnBoot)
                        view.append_column(columnRunOnBoot)
                        # module name column
                        rendererModName = gtk.CellRendererText()
                        modNameText = _('Module')
                        columnModName = gtk.TreeViewColumn(modNameText, rendererModName, text=self.moduleColumnName)
                        columnModName.set_resizable(True)
                        columnModName.set_sort_column_id(self.moduleColumnName)
                        view.append_column(columnModName)
                        # module version column
                        rendererModVersion = gtk.CellRendererText()
                        rendererModVersion.set_property('xalign', 0.5)
                        modVersionText = _(' Module Version')
                        columnModVersion = gtk.TreeViewColumn(modVersionText, rendererModVersion, text=self.moduleColumnVersion)
                        view.append_column(columnModVersion)
                        # module author column
                        rendererModAuthor = gtk.CellRendererText()
                        modAuthorText = _('Author')
                        columnModAuthor = gtk.TreeViewColumn(modAuthorText, rendererModAuthor, text=self.moduleColumnAuthor)
                        columnModAuthor.set_resizable(True)
                        columnModAuthor.set_sort_column_id(self.moduleColumnAuthor)
                        view.append_column(columnModAuthor)
                        # module description column
                        rendererModDescription = gtk.CellRendererText()
                        modDescriptionText = _('Description')
                        columnModDescription = gtk.TreeViewColumn(modDescriptionText, rendererModDescription, text=self.moduleColumnDescription)
                        columnModDescription.set_resizable(True)
                        view.append_column(columnModDescription)
                        # module run in chroot column
                        rendererModRunInChroot = gtk.CellRendererToggle()
                        modRunInChrootText = _('Run in Chroot')
                        columnModRunInChroot = gtk.TreeViewColumn(modRunInChrootText, rendererModRunInChroot, active=self.moduleColumnRunInChroot)
                        # show column if running debug
                        if self.runningDebug == True:
                            columnModRunInChroot.set_property('visible', True)
                        else:
                            columnModRunInChroot.set_property('visible', False)
                        view.append_column(columnModRunInChroot)
                        # module update url column
                        rendererModUpdateUrl = gtk.CellRendererText()
                        modUpdateUrlText = _('Update URL')
                        columnModUpdateUrl = gtk.TreeViewColumn(modUpdateUrlText, rendererModUpdateUrl, text=self.moduleColumnUpdateUrl)
                        # show column if running debug
                        if self.runningDebug == True:
                            columnModUpdateUrl.set_property('visible', True)
                        else:
                            columnModUpdateUrl.set_property('visible', False)
                        view.append_column(columnModUpdateUrl)
                        # module path column
                        rendererModPath = gtk.CellRendererText()
                        modPathText = _('Path')
                        columnModPath = gtk.TreeViewColumn(modPathText, rendererModPath, text=self.moduleColumnPath)
                        columnModPath.set_resizable(True)
                        # show column if running debug
                        if self.runningDebug == True:
                            columnModPath.set_property('visible', True)
                        else:
                            columnModPath.set_property('visible', False)
                        view.append_column(columnModPath)
                        self.wTree.get_widget("scrolledwindowModules").add(view)
                        view.show()
                        # expand Software section
                        view.expand_to_path('0')
                        self.setDefaultCursor()

    def addModule(self, modulePath, updating=False):
        try:
            # if not updating, copy to modules dir
            if updating == False:
                r, ext = os.path.splitext(modulePath)
                if ext == '.rmod':
                    installText = _('Installing Module: ')
                    print installText + os.path.basename(modulePath)
                    shutil.copy(modulePath, self.moduleDir)
                    os.popen('chmod -R 777 \"' + self.moduleDir + '\"')
                    # parse and add module to model

                    modPath = os.path.join(self.moduleDir, r)

                    # Refactoring! triplem
                    modProps = self.getModuleProperties(os.path.basename(modulePath))
                    modSubCategory = modProps[self.modSubCategoryKey]

                    if self.modules.has_key(modProps[self.modNameKey]):
                        print "The module is already present"

                    if modSubCategory == 'Administration':
                        iter = self.treeModel.insert_before(self.iterCategoryAdministration, None)
                    elif modSubCategory == 'Education':
                        iter = self.treeModel.insert_before(self.iterCategoryEducation, None)
                    elif modSubCategory == 'Servers':
                        iter = self.treeModel.insert_before(self.iterCategoryServers, None)
                    elif modSubCategory == 'Graphics':
                        iter = self.treeModel.insert_before(self.iterCategoryGraphics, None)
                    elif modSubCategory == 'Multimedia':
                        iter = self.treeModel.insert_before(self.iterCategoryMultimedia, None)
                    elif modSubCategory == 'Networking':
                        iter = self.treeModel.insert_before(self.iterCategoryNetworking, None)
                    elif modSubCategory == 'Plugins':
                        iter = self.treeModel.insert_before(self.iterCategoryPlugins, None)
                    elif modSubCategory == 'Productivity':
                        iter = self.treeModel.insert_before(self.iterCategoryProductivity, None)
                    elif modSubCategory == 'Virtualization':
                        iter = self.treeModel.insert_before(self.iterCategoryVirtualization, None)
                    else:
                        iter = self.treeModel.insert_before(self.iterCategoryMisc, None)

                    self.treeModel.set_value(iter, self.moduleColumnExecute, False)
                    self.treeModel.set_value(iter, self.moduleColumnRunOnBoot, False)
                    self.treeModel.set_value(iter, self.moduleColumnName, modProps[self.modNameKey])
                    self.treeModel.set_value(iter, self.moduleColumnVersion, modProps[self.modVersionKey])
                    self.treeModel.set_value(iter, self.moduleColumnAuthor, modProps[self.modAuthorKey])
                    self.treeModel.set_value(iter, self.moduleColumnDescription, modProps[self.modDescriptionKey])
                    self.treeModel.set_value(iter, self.moduleColumnRunInChroot, bool(modProps[self.modRunInChrootKey]))
                    self.treeModel.set_value(iter, self.moduleColumnUpdateUrl, modProps[self.modUpdateUrlKey])
                    self.treeModel.set_value(iter, self.moduleColumnPath, modPath)

        except Exception, detail:
            errText = _('Error installing module: ')
            print errText, modulePath + ': ', detail

    def updateModule(self, moduleName, moduleVersion, moduleFullPath, moduleUpdateUrl, treeview):
        try:
            selection = treeview.get_selection()
            model, iter = selection.get_selected()

            # check for update url
            if moduleUpdateUrl == '':
                updTxt = _('Updating not available for module: ')
                print updTxt, moduleName
            # check for updates
            else:
                updTxt = _('Checking updates for module: ')
                print updTxt, moduleName + '...'
                urllib.urlretrieve(moduleUpdateUrl + os.path.basename(moduleFullPath), "/tmp/r-mod-update.tmp")
                if os.path.exists('/tmp/r-mod-update.tmp'):
                    f = open('/tmp/r-mod-update.tmp', 'r')

                    # Refactoring! triplem
                    newModProps = self.getModuleProperties('/tmp/r-mod-update.tmp')
                    newModSubCategory = newModProps[self.modSubCategoryKey]

                    # check for valid update
                    if newModProps[self.modNameKey] != '':
                        fModVer = float(moduleVersion)
                        fModNewVer = float(newModProps[self.modVersionKey])
                        #print ('Current Module Version: ' + str(fModVer) + ' -- Available: ' + str(fModNewVer))
                        if fModNewVer > fModVer:
                            # update module
                            verTxt = _('Found new version: ')
                            # prompt for installation
                            updateDlg = gtk.Dialog(title="Module Update", parent=None, flags=0, buttons=(gtk.STOCK_NO, gtk.RESPONSE_NO, gtk.STOCK_YES, gtk.RESPONSE_OK))
                            updateDlg.set_icon_from_file(self.iconFile)
                            updateDlg.vbox.set_spacing(10)
                            labelSpc = gtk.Label(" ")
                            updateDlg.vbox.pack_start(labelSpc)
                            labelSpc.show()
                            # module name label
                            lblModName = gtk.Label('Reconstructor Module: ' + '<b>' + moduleName + '</b>')
                            lblModName.set_use_markup(True)
                            updateDlg.vbox.pack_start(lblModName)
                            lblModName.show()
                            # module author label
                            lblModAuthor = gtk.Label('Author: ' + newModProps[self.modAuthorKey])
                            lblModAuthor.set_use_markup(True)
                            updateDlg.vbox.pack_start(lblModAuthor)
                            lblModAuthor.show()
                            # module version label
                            lblNewVersionTxt = _('New version available: ')
                            lblNewVersion = gtk.Label(lblNewVersionTxt + '<b>' + newModProps[self.modVersionKey] + '</b>')
                            lblNewVersion.set_use_markup(True)
                            updateDlg.vbox.pack_start(lblNewVersion)
                            lblNewVersion.show()
                            #lblInfo = gtk.Label(updateInfo)
                            #lblInfo.set_use_markup(True)
                            #updateDlg.vbox.pack_start(lblInfo)
                            #lblInfo.show()
                            lblConfirm = gtk.Label('Update?')
                            updateDlg.vbox.pack_start(lblConfirm)
                            lblConfirm.show()

                            response = updateDlg.run()
                            if response == gtk.RESPONSE_OK:
                                updateDlg.destroy()
                                updateText = _('Updating...')
                                print updateText
                                # copy update to modules
                                os.popen('cp -Rf /tmp/r-mod-update.tmp ' + '\"' + os.path.join(self.moduleDir, os.path.basename(moduleFullPath)) + '"')
                                # remove old from treemodel
                                self.treeModel.remove(iter)
                                # add new version to treemodel
                                self.addModule(moduleFullPath, updating=True)
                                modUpdatedTxt = _('Module updated.')
                                print modUpdatedTxt
                            else:
                                print _('Module update cancelled.')
                                updateDlg.destroy()
                        else:
                            # latest version
                            print _('Module is at the latest version.')
                    else:
                        errUpdTxt = _('Could not find a valid update for module: ')
                        print errUpdTxt, moduleName
                else:
                    print 'Updating not available...'
            # cleanup
            if os.path.exists('/tmp/r-mod-update.tmp'):
                os.popen('rm -f /tmp/r-mod-update.tmp')
            # set default cursor
            self.setDefaultCursor()

        except Exception, detail:
            # cleanup
            #if os.path.exists('/tmp/r-mod-update.tmp'):
            #    os.popen('rm -f /tmp/r-mod-update.tmp')
            # set default cursor
            self.setDefaultCursor()
            errText = _('Error updating module: ')
            print errText, detail


    def updateSelectedModule(self):
        try:
            selection = self.treeView.get_selection()
            model, iter = selection.get_selected()
            modName = ''
            modVersion = ''
            modPath = None
            modUpdateUrl = ''
            if iter:
                path = model.get_path(iter)
                modName = model.get_value(iter, self.moduleColumnName)
                modVersion = model.get_value(iter, self.moduleColumnVersion)
                modPath = model.get_value(iter, self.moduleColumnPath)
                modUpdateUrl = model.get_value(iter, self.moduleColumnUpdateUrl)

            # check for valid module and update
            if modPath != None:
                mTxt = _('Checking updates for module: ')
                print mTxt, modName
                print modUpdateUrl + os.path.basename(modPath)
                urllib.urlretrieve(modUpdateUrl + os.path.basename(modPath), "/tmp/r-mod-update.tmp")
                if os.path.exists('/tmp/r-mod-update.tmp'):
                    f = open('/tmp/r-mod-update.tmp', 'r')
                    # parse module and get info
                    newModCategory = ''
                    newModSubCategory = ''
                    newModName = ''
                    newModVersion = ''
                    newModAuthor = ''
                    newModDescription = ''
                    newModRunInChroot = None
                    newModUpdateUrl = ''
                    newModPath = os.path.join(self.moduleDir, os.path.basename(modPath))
                    # HACK: regex through module to get info
                    reModCategory = re.compile(self.regexModCategory, re.IGNORECASE)
                    reModSubCategory = re.compile(self.regexModSubCategory, re.IGNORECASE)
                    reModName = re.compile(self.regexModName, re.IGNORECASE)
                    reModVersion = re.compile(self.regexModVersion, re.IGNORECASE)
                    reModAuthor = re.compile(self.regexModAuthor, re.IGNORECASE)
                    reModDescription = re.compile(self.regexModDescription, re.IGNORECASE)
                    reModRunInChroot = re.compile(self.regexModRunInChroot, re.IGNORECASE)
                    reModUpdateUrl = re.compile(self.regexModUpdateUrl, re.IGNORECASE)

                    for line in fMod:
                        if reModCategory.match(line) != None:
                            newModCategory = reModCategory.match(line).group(1)
                        if reModSubCategory.match(line) != None:
                            newModSubCategory = reModSubCategory.match(line).group(1)
                        if reModName.match(line) != None:
                            newModName = reModName.match(line).group(1)
                        if reModVersion.match(line) != None:
                            newModVersion = reModVersion.match(line).group(1)
                        if reModAuthor.match(line) != None:
                            newModAuthor = reModAuthor.match(line).group(1)
                        if reModDescription.match(line) != None:
                            newModDescription = reModDescription.match(line).group(1)
                        if reModRunInChroot.match(line) != None:
                            newModRunInChroot = reModRunInChroot.match(line).group(1)
                        if reModUpdateUrl.match(line) != None:
                            newModUpdateUrl = reModUpdateUrl.match(line).group(1)
                    f.close()
                    fModVer = float(modVersion)
                    fModNewVer = float(newModVersion)
                    print ('Current Module Version: ' + str(fModVer) + ' -- Available: ' + str(fModNewVer))
                    if fUpdate > fApp:
                        # update module
                        updateText = _('Updating Module: ')
                        print updateText, modName + '...'
                    else:
                        # latest version
                        print _('Module is at the latest version.\n')
                    # cleanup
                    if os.path.exists('/tmp/r-mod-update.tmp'):
                        os.popen('rm -f /tmp/r-mod-update.tmp')
                # set default cursor
                self.setDefaultCursor()

        except Exception, detail:
            errText = _('Error updating module: ')
            print errText, detail





    def on_treeitemExecute_toggled(self, cell, path_str, model):
            # get toggled iter
            iter = model.get_iter_from_string(path_str)
            toggle_item = cell.get_active()

            # change value
            toggle_item = not toggle_item

            # clear run on boot if enabled
            if model.get_value(iter, self.moduleColumnRunOnBoot) == True:
                # set to false
                model.set(iter, self.moduleColumnRunOnBoot, False)

            # set new value
            model.set(iter, self.moduleColumnExecute, toggle_item)

            # toggle all child nodes
            if model.iter_n_children(iter) > 0:
                for i in range(model.iter_n_children(iter)):
                    childToggled = model.get_value(model.iter_nth_child(iter, i), self.moduleColumnExecute)
                    model.set(model.iter_nth_child(iter, i), self.moduleColumnExecute, toggle_item)

    def on_treeitemRunOnBoot_toggled(self, cell, path_str, model):
            # get toggled iter
            iter = model.get_iter_from_string(path_str)
            toggle_item = cell.get_active()

            # change value
            toggle_item = not toggle_item

            # clear execute if enabled
            if model.get_value(iter, self.moduleColumnExecute) == True:
                # set to false
                model.set(iter, self.moduleColumnExecute, False)

            # set new value
            model.set(iter, self.moduleColumnRunOnBoot, toggle_item)

            # toggle all child nodes
            if model.iter_n_children(iter) > 0:
                for i in range(model.iter_n_children(iter)):
                    model.set(model.iter_nth_child(iter, i), self.moduleColumnRunOnBoot, toggle_item)

    def on_treeitem_row_activated(self, treeview, path, column):
        self.showModuleSource(treeview)

    def showModuleSource(self, treeview):
        try:
            selection = treeview.get_selection()
            model, iter = selection.get_selected()
            modName = ''
            modPath = None
            if iter:
                path = model.get_path(iter)
                modName = model.get_value(iter, self.moduleColumnName)
                modPath = model.get_value(iter, self.moduleColumnPath)

            if modPath:
                f = file(modPath, 'r')
                scr = f.read()
                f.close()
                # create dialog
                modDlg = gtk.Dialog(title="Module:  " + modName, parent=None, flags=0, buttons=(gtk.STOCK_CLOSE, gtk.RESPONSE_OK))

                modDlg.set_default_size(512, 512)
                modDlg.set_icon_from_file(self.iconFile)
                modDlg.vbox.set_spacing(10)
                labelSpc = gtk.Label(" ")
                modDlg.vbox.pack_start(labelSpc, False, False)
                labelSpc.show()
                # scrolled window for module text
                sw = gtk.ScrolledWindow()
                sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
                sw.set_shadow_type(gtk.SHADOW_IN)
                # text buffer for module
                tBuffer = gtk.TextBuffer()
                tBuffer.set_text(scr)
                textviewModule = gtk.TextView(tBuffer)
                textviewModule.set_editable(False)
                sw.add(textviewModule)
                modDlg.vbox.pack_start(sw, True, True)

                textviewModule.show()
                sw.show()
                #modDlg.show()
                response = modDlg.run()
                if response != None:
                    modDlg.destroy()


        except Exception, detail:
            print detail
            pass

    def copyExecuteModule(self, model, path, iter):
        modName = model.get_value(iter, self.moduleColumnName)
        modExecute = model.get_value(iter, self.moduleColumnExecute)
        modPath = model.get_value(iter, self.moduleColumnPath)
        modRunInChroot = model.get_value(iter, self.moduleColumnRunInChroot)
        # check for module and skip category
        if modPath != None:
            # check for execute
            if modExecute == True:
                #print modName, modRunInChroot
                if modRunInChroot == True:
                    #print modName + ' - Running in chroot...'
                    os.popen('cp -R \"' + modPath + '\" \"' + os.path.join(self.customDir, "root/tmp/") + '\"')
                    os.popen('chmod a+x \"' + os.path.join(self.customDir, "root/tmp/") + os.path.basename(modPath) + '\"')

                else:
                    print modName + ' - Running in custom directory...'
                    os.popen('cp -R \"' + modPath + '\" \"' + self.customDir + '\"')
                    os.popen('chmod a+x \"' + os.path.join(self.customDir, os.path.basename(modPath)) + '\"')

    def copyRunOnBootModule(self, model, path, iter):
        modName = model.get_value(iter, self.moduleColumnName)
        modRunOnBoot = model.get_value(iter, self.moduleColumnRunOnBoot)
        modPath = model.get_value(iter, self.moduleColumnPath)
        # check for module and skip category
        if modPath != None:
            # check for run on boot
            if modRunOnBoot == True:
                # check for script dir
                if os.path.exists(os.path.join(self.customDir, "root/usr/share/reconstructor/scripts/")) == False:
                    os.popen('mkdir -p \"' + os.path.join(self.customDir, "root/usr/share/reconstructor/scripts/") + '\"')
                # copy module
                os.popen('cp -R \"' + modPath + '\" \"' + os.path.join(self.customDir, "root/usr/share/reconstructor/scripts/") + '\"')
                os.popen('chmod a+x \"' + os.path.join(self.customDir, "root/usr/share/reconstructor/scripts/") + os.path.basename(modPath) + '\"')
                txt = _('Copied module: ')
                print txt, modName

    def checkExecModuleEnabled(self, model, path, iter):
        modExecute = model.get_value(iter, self.moduleColumnExecute)
        if modExecute == True:
            self.execModulesEnabled = True

    def checkBootModuleEnabled(self, model, path, iter):
        modRunOnBoot = model.get_value(iter, self.moduleColumnRunOnBoot)
        if modRunOnBoot == True:
            self.bootModulesEnabled = True

    def clearRunOnBootModules(self):
        try:
            # remove all run on boot modules and scripts
            print _('Clearing all run on boot modules and scripts...')
            os.popen('rm -Rf \"' + os.path.join(self.customDir, "root/etc/skel/.gnomerc") + '\"')
            os.popen('rm -Rf \"' + os.path.join(self.customDir, "root/usr/share/reconstructor/") + '\"')
        except Exception, detail:
            errText = _('Error clearing run on boot modules: ')
            print errText, detail

    def checkSetup(self):
        setup = False
        if self.createRemasterDir == True:
            setup = True
        elif self.createCustomRoot == True:
            setup = True
        elif self.createInitrdRoot == True:
            setup = True
        else:
            # nothing to be done
            setup = False
        return setup

    def checkAltSetup(self):
        setup = False
        if self.createAltRemasterDir == True:
            setup = True
        elif self.createAltInitrdRoot == True:
            setup = True
        else:
            # nothing to be done
            setup = False
        return setup

    def checkCustomDir(self):
        if self.customDir == "":
            return False
        else:
            if os.path.exists(self.customDir) == False:
                os.makedirs(self.customDir)
            return True

    def setPage(self, pageNum):
        self.wTree.get_widget("notebookWizard").set_current_page(pageNum)

    def setBusyCursor(self):
        self.working = True
        self.wTree.get_widget("windowMain").window.set_cursor(gtk.gdk.Cursor(gtk.gdk.WATCH))

    def setDefaultCursor(self):
        self.working = False
        self.wTree.get_widget("windowMain").window.set_cursor(None)

    def showWorking(self):
        self.workingDlg = gtk.Dialog(title="Working")
        self.workingDlg.set_modal(True)
        self.workingDlg.show()

    def hideWorking(self):
        self.workingDlg.hide()

    def checkWindowsPrograms(self):
        apps = False
        if os.path.exists(os.path.join(self.customDir, "remaster/bin")):
            apps = True
        if os.path.exists(os.path.join(self.customDir, "remaster/programs")):
            apps = True
        return apps

    # checks if user entered custom password matches
    def checkUserPassword(self):
        if self.wTree.get_widget("entryLiveCdUserPassword").get_text() == self.wTree.get_widget("entryLiveCdUserPasswordCheck").get_text():
            return True
        else:
            return False

    def checkSoftware(self):
        install = False
        # custom apt-get
        if self.wTree.get_widget("entryCustomAptInstall").get_text() != "":
            install = True
        # software removal
        # custom
        if self.wTree.get_widget("entryCustomAptRemove").get_text() != "":
            install = True

        return install

    def checkCustomRepos(self):
        customRepos = False
        if self.wTree.get_widget("checkbuttonAptRepoUbuntuOfficial").get_active() == True:
            #print "Selected Ubuntu Official apt archive..."
            customRepos = True
        elif self.wTree.get_widget("checkbuttonAptRepoUbuntuRestricted").get_active() == True:
            #print "Selected Ubuntu Restricted apt archive..."
            customRepos = True
        elif self.wTree.get_widget("checkbuttonAptRepoUbuntuUniverse").get_active() == True:
            #print "Selected Ubuntu Universe apt archive..."
            customRepos = True
        elif self.wTree.get_widget("checkbuttonAptRepoUbuntuMultiverse").get_active() == True:
            #print "Selected Ubuntu Multiverse apt archive..."
            customRepos = True
        else:
            #print "No custom apt repos.  Using defaults."
            customRepos = False
        return customRepos

    def checkAltCustomRepos(self):
        customRepos = False
        if self.wTree.get_widget("checkbuttonAltUbuntuOfficialRepo").get_active() == True:
            #print "Selected Ubuntu Official apt archive..."
            customRepos = True
        elif self.wTree.get_widget("checkbuttonAltUbuntuRestrictedRepo").get_active() == True:
            #print "Selected Ubuntu Restricted apt archive..."
            customRepos = True
        elif self.wTree.get_widget("checkbuttonAltUbuntuUniverseRepo").get_active() == True:
            #print "Selected Ubuntu Universe apt archive..."
            customRepos = True
        elif self.wTree.get_widget("checkbuttonAltUbuntuMultiverseRepo").get_active() == True:
            #print "Selected Ubuntu Multiverse apt archive..."
            customRepos = True
        else:
            #print "No custom apt repos.  Using defaults."
            customRepos = False
        return customRepos

    def checkCustomGdm(self):
        customGdm = False
        if self.wTree.get_widget("comboboxentryGnomeGdmTheme").get_active_text() != "":
            customGdm = True
        if self.wTree.get_widget("checkbuttonGdmSounds").get_active() == True:
            customGdm = True
        if self.wTree.get_widget("checkbuttonGdmRootLogin").get_active() == True:
            customGdm = True
        if self.wTree.get_widget("checkbuttonGdmXdmcp").get_active() == True:
            customGdm = True
        color = self.wTree.get_widget("colorbuttonBrowseGdmBackgroundColor").get_color()
        rgbColor = color.red/255, color.green/255, color.blue/255
        hexColor = '%02x%02x%02x' % rgbColor
        if self.gdmBackgroundColor != str(hexColor):
            customGdm = True
        return customGdm

    def checkWorkingDir(self):
        # check for existing directories; if not warn...
        remasterExists = None
        rootExists = None
        initrdExists = None
        if os.path.exists(os.path.join(self.customDir, "remaster")) == False:
            if self.wTree.get_widget("checkbuttonCreateRemaster").get_active() == False:
                remasterExists = False
        if os.path.exists(os.path.join(self.customDir, "root")) == False:
            if self.wTree.get_widget("checkbuttonCreateRoot").get_active() == False:
                rootExists = False
        if os.path.exists(os.path.join(self.customDir, "initrd")) == False:
            if self.wTree.get_widget("checkbuttonCreateInitRd").get_active() == False:
                initrdExists = False
        workingDirOk = True
        if remasterExists == False:
            workingDirOk = False
        if rootExists == False:
            workingDirOk = False
        if initrdExists == False:
            workingDirOk = False
        if workingDirOk == False:
            warnDlg = gtk.Dialog(title=self.appName, parent=None, flags=0, buttons=(gtk.STOCK_OK, gtk.RESPONSE_OK))
            warnDlg.set_icon_from_file(self.iconFile)
            warnDlg.vbox.set_spacing(10)
            labelSpc = gtk.Label(" ")
            warnDlg.vbox.pack_start(labelSpc)
            labelSpc.show()
            lblWarningText = _("  <b>Please fix the errors below before continuing.</b>   ")
            lblRemasterText = _("  There is no remaster directory.  Please select create remaster option.  ")
            lblRootText = _("  There is no root directory.  Please select create root option.  ")
            lblInitrdText = _("  There is no initrd directory.  Please select create initrd option.  ")
            labelWarning = gtk.Label(lblWarningText)
            labelRemaster = gtk.Label(lblRemasterText)
            labelRoot = gtk.Label(lblRootText)
            labelInitrd = gtk.Label(lblInitrdText)

            labelWarning.set_use_markup(True)
            labelRemaster.set_use_markup(True)
            labelRoot.set_use_markup(True)
            labelInitrd.set_use_markup(True)
            warnDlg.vbox.pack_start(labelWarning)
            warnDlg.vbox.pack_start(labelRemaster)
            warnDlg.vbox.pack_start(labelRoot)
            warnDlg.vbox.pack_start(labelInitrd)
            labelWarning.show()

            if remasterExists == False:
                labelRemaster.show()
            if rootExists == False:
                labelRoot.show()
            if initrdExists == False:
                labelInitrd.show()

            #warnDlg.show()
            response = warnDlg.run()
            # HACK: return False no matter what
            if response == gtk.RESPONSE_OK:
                warnDlg.destroy()
            else:
                warnDlg.destroy()

        return workingDirOk

    def checkAltWorkingDir(self):
        # check for existing directories; if not warn...
        remasterExists = None
        initrdExists = None
        if os.path.exists(os.path.join(self.customDir, self.altRemasterDir)) == False:
            if self.wTree.get_widget("checkbuttonAltCreateRemasterDir").get_active() == False:
                remasterExists = False
        if os.path.exists(os.path.join(self.customDir, self.altInitrdRoot)) == False:
            if self.wTree.get_widget("checkbuttonAltCreateInitrdDir").get_active() == False:
                initrdExists = False
        workingDirOk = True
        if remasterExists == False:
            workingDirOk = False
        if initrdExists == False:
            workingDirOk = False
        if workingDirOk == False:
            warnDlg = gtk.Dialog(title=self.appName, parent=None, flags=0, buttons=(gtk.STOCK_OK, gtk.RESPONSE_OK))
            warnDlg.set_icon_from_file(self.iconFile)
            warnDlg.vbox.set_spacing(10)
            labelSpc = gtk.Label(" ")
            warnDlg.vbox.pack_start(labelSpc)
            labelSpc.show()
            lblWarningText = _("  <b>Please fix the errors below before continuing.</b>   ")
            lblRemasterText = _("  There is no remaster directory.  Please select create remaster option.  ")
            lblInitrdText = _("  There is no initrd directory.  Please select create initrd option.  ")
            labelWarning = gtk.Label(lblWarningText)
            labelRemaster = gtk.Label(lblRemasterText)
            labelInitrd = gtk.Label(lblInitrdText)

            labelWarning.set_use_markup(True)
            labelRemaster.set_use_markup(True)
            labelInitrd.set_use_markup(True)
            warnDlg.vbox.pack_start(labelWarning)
            warnDlg.vbox.pack_start(labelRemaster)
            warnDlg.vbox.pack_start(labelInitrd)
            labelWarning.show()

            if remasterExists == False:
                labelRemaster.show()
            if initrdExists == False:
                labelInitrd.show()

            #warnDlg.show()
            response = warnDlg.run()
            # HACK: return False no matter what
            if response == gtk.RESPONSE_OK:
                warnDlg.destroy()
            else:
                warnDlg.destroy()

        return workingDirOk


    def checkPage(self, pageNum):
        if self.runningDebug == True:
            print "CheckPage: " + str(pageNum)
            #print " "
        if pageNum == self.pageWelcome:
            # intro
            self.setPage(self.pageDiscType)
            return True
        elif pageNum == self.pageDiscType:
            typeText = _("Disc Type:")
            # continue based on disc type (live/alt)
            if self.wTree.get_widget("radiobuttonDiscTypeLive").get_active() == True:
                # set disc type
                self.discType = "live"
                print typeText, " " + self.discType
                self.setPage(self.pageLiveSetup)
            elif self.wTree.get_widget("radiobuttonDiscTypeAlt").get_active() == True:
                # set disc type
                self.discType = "alt"
                print typeText, " " + self.discType
                self.setPage(self.pageAltSetup)
        elif pageNum == self.pageLiveSetup:
            # setup
            self.saveSetupInfo()
            # reset interactive edit
            self.interactiveEdit = False
            # check for custom dir
            if self.checkCustomDir() == True:
                if self.checkSetup() == True:
                    if self.checkWorkingDir() == True:
                        warnDlg = gtk.Dialog(title=self.appName, parent=None, flags=0, buttons=    (gtk.STOCK_NO, gtk.RESPONSE_CANCEL, gtk.STOCK_YES, gtk.RESPONSE_OK))
                        warnDlg.set_icon_from_file(self.iconFile)
                        warnDlg.vbox.set_spacing(10)
                        labelSpc = gtk.Label(" ")
                        warnDlg.vbox.pack_start(labelSpc)
                        labelSpc.show()
                        lblContinueText = _("  <b>Continue?</b>  ")
                        lblContinueInfo = _("     This may take a few minutes.  Please wait...     ")
                        label = gtk.Label(lblContinueText)
                        lblInfo = gtk.Label(lblContinueInfo)
                        label.set_use_markup(True)
                        warnDlg.vbox.pack_start(label)
                        warnDlg.vbox.pack_start(lblInfo)
                        lblInfo.show()
                        label.show()
                        #warnDlg.show()
                        response = warnDlg.run()
                        if response == gtk.RESPONSE_OK:
                            warnDlg.destroy()
                            self.setBusyCursor()
                            gobject.idle_add(self.setupWorkingDirectory)
                            # load modules
                            gobject.idle_add(self.loadModules)
                            self.setBusyCursor()
                            # calculate iso size
                            gobject.idle_add(self.calculateIsoSize)
                            #self.calculateIsoSize()
                            return True
                        else:
                            warnDlg.destroy()
                            return False
                    else:
                        return False
                else:
                    if self.checkWorkingDir() == True:
                        # get ubuntu version
                        self.loadCdVersion()
                        # get current boot options menu text color
                        self.loadBootMenuColor()
                        # load desktop environments
                        self.loadAvailableDesktops()
                        self.setBusyCursor()
                        # load modules
                        gobject.idle_add(self.loadModules)
                        # calculate iso size in the background
                        gobject.idle_add(self.calculateIsoSize)
                        #self.calculateIsoSize()
                        return True
                    else:
                        return False
            else:
                warnDlg = gtk.Dialog(title=self.appName, parent=None, flags=0, buttons=(gtk.STOCK_OK, gtk.RESPONSE_OK))
                warnDlg.set_icon_from_file(self.iconFile)
                warnDlg.vbox.set_spacing(10)
                labelSpc = gtk.Label(" ")
                warnDlg.vbox.pack_start(labelSpc)
                labelSpc.show()
                lblWorkingDirText = _("  <b>You must enter a working directory.</b>  ")
                label = gtk.Label(lblWorkingDirText)
                #lblInfo = gtk.Label("     This may take a few minutes.  Please     wait...     ")
                label.set_use_markup(True)
                warnDlg.vbox.pack_start(label)
                #warnDlg.vbox.pack_start(lblInfo)
                #lblInfo.show()
                label.show()
                #warnDlg.show()
                response = warnDlg.run()
                # HACK: return False no matter what
                if response == gtk.RESPONSE_OK:
                    warnDlg.destroy()
                    return False
                else:
                    warnDlg.destroy()
                    return False
        elif pageNum == self.pageLiveCustomize:
            warnDlg = gtk.Dialog(title=self.appName, parent=None, flags=0, buttons=(gtk.STOCK_NO, gtk.RESPONSE_CANCEL, gtk.STOCK_YES, gtk.RESPONSE_OK))
            warnDlg.set_icon_from_file(self.iconFile)
            warnDlg.vbox.set_spacing(10)
            labelSpc = gtk.Label(" ")
            warnDlg.vbox.pack_start(labelSpc)
            labelSpc.show()
            lblContinueText = _("  <b>Continue?</b>  ")
            label = gtk.Label(lblContinueText)
            label.set_use_markup(True)
            lblApplyText = _("Be sure to click <b>Apply</b> to apply changes before continuing.")
            lblApply = gtk.Label(lblApplyText)
            lblApply.set_use_markup(True)
            warnDlg.vbox.pack_start(label)
            warnDlg.vbox.pack_start(lblApply)
            label.show()
            lblApply.show()
            #warnDlg.show()
            response = warnDlg.run()
            if response == gtk.RESPONSE_OK:
                warnDlg.destroy()
                self.setPage(self.pageLiveBuild)
                # check for windows apps and enable/disable checkbox as necessary
                if self.checkWindowsPrograms() == True:
                    self.wTree.get_widget("checkbuttonLiveCdRemoveWin32Programs").set_sensitive(True)
                else:
                    self.wTree.get_widget("checkbuttonLiveCdRemoveWin32Programs").set_sensitive(False)
                # HACK: check in case "create iso" option is unchecked
                # enable/disable iso burn
                self.checkEnableBurnIso()
                return True
            else:
                warnDlg.destroy()
                return False

        elif pageNum == self.pageLiveBuild:
            # build
            warnDlg = gtk.Dialog(title=self.appName, parent=None, flags=0, buttons=(gtk.STOCK_NO, gtk.RESPONSE_CANCEL, gtk.STOCK_YES, gtk.RESPONSE_OK))
            warnDlg.set_icon_from_file(self.iconFile)
            warnDlg.vbox.set_spacing(10)
            labelSpc = gtk.Label(" ")
            warnDlg.vbox.pack_start(labelSpc)
            labelSpc.show()
            lblBuildText = _("  <b>Build Live CD?</b>  ")
            lblBuildInfo = _("     This may take a few minutes.  Please wait...     ")
            label = gtk.Label(lblBuildText)
            lblInfo = gtk.Label(lblBuildInfo)
            label.set_use_markup(True)
            warnDlg.vbox.pack_start(label)
            warnDlg.vbox.pack_start(lblInfo)
            lblInfo.show()
            label.show()
            #warnDlg.show()
            response = warnDlg.run()
            if response == gtk.RESPONSE_OK:
                warnDlg.destroy()
                self.setBusyCursor()
                gobject.idle_add(self.build)
                # change Next text to Finish
                self.wTree.get_widget("buttonNext").set_label("Finish")
                return True
            else:
                warnDlg.destroy()
                return False

        elif pageNum == self.pageAltSetup:
            # setup
            self.saveAltSetupInfo()
            # check for custom dir
            if self.checkCustomDir() == True:
                if self.checkAltSetup() == True:
                    if self.checkAltWorkingDir() == True:
                        warnDlg = gtk.Dialog(title=self.appName, parent=None, flags=0, buttons=    (gtk.STOCK_NO, gtk.RESPONSE_CANCEL, gtk.STOCK_YES, gtk.RESPONSE_OK))
                        warnDlg.set_icon_from_file(self.iconFile)
                        warnDlg.vbox.set_spacing(10)
                        labelSpc = gtk.Label(" ")
                        warnDlg.vbox.pack_start(labelSpc)
                        labelSpc.show()
                        lblContinueText = _("  <b>Continue?</b>  ")
                        lblContinueInfo = _("     This may take a few minutes.  Please wait...     ")
                        label = gtk.Label(lblContinueText)
                        lblInfo = gtk.Label(lblContinueInfo)
                        label.set_use_markup(True)
                        warnDlg.vbox.pack_start(label)
                        warnDlg.vbox.pack_start(lblInfo)
                        lblInfo.show()
                        label.show()
                        #warnDlg.show()
                        response = warnDlg.run()
                        if response == gtk.RESPONSE_OK:
                            warnDlg.destroy()
                            self.setBusyCursor()
                            gobject.idle_add(self.setupAltWorkingDirectory)
                            return True
                        else:
                            warnDlg.destroy()
                            return False
                    else:

                        return False
                else:
                    if self.checkAltWorkingDir() == True:
                        self.setBusyCursor()
                        # calculate iso size in the background
                        gobject.idle_add(self.calculateAltIsoSize)
                        return True
                    else:
                        return False
            else:
                warnDlg = gtk.Dialog(title=self.appName, parent=None, flags=0, buttons=(gtk.STOCK_OK, gtk.RESPONSE_OK))
                warnDlg.set_icon_from_file(self.iconFile)
                warnDlg.vbox.set_spacing(10)
                labelSpc = gtk.Label(" ")
                warnDlg.vbox.pack_start(labelSpc)
                labelSpc.show()
                lblWorkingDirText = _("  <b>You must enter a working directory.</b>  ")
                label = gtk.Label(lblWorkingDirText)
                #lblInfo = gtk.Label("     This may take a few minutes.  Please     wait...     ")
                label.set_use_markup(True)
                warnDlg.vbox.pack_start(label)
                #warnDlg.vbox.pack_start(lblInfo)
                #lblInfo.show()
                label.show()
                #warnDlg.show()
                response = warnDlg.run()
                # HACK: return False no matter what
                if response == gtk.RESPONSE_OK:
                    warnDlg.destroy()
                    return False
                else:
                    warnDlg.destroy()
                    return False
        elif pageNum == self.pageAltCustomize:
            warnDlg = gtk.Dialog(title=self.appName, parent=None, flags=0, buttons=(gtk.STOCK_NO, gtk.RESPONSE_CANCEL, gtk.STOCK_YES, gtk.RESPONSE_OK))
            warnDlg.set_icon_from_file(self.iconFile)
            warnDlg.vbox.set_spacing(10)
            labelSpc = gtk.Label(" ")
            warnDlg.vbox.pack_start(labelSpc)
            labelSpc.show()
            lblContinueText = _("  <b>Continue?</b>  ")
            label = gtk.Label(lblContinueText)
            label.set_use_markup(True)
            lblApplyText = _("Be sure to click <b>Apply</b> to apply changes before continuing.")
            lblApply = gtk.Label(lblApplyText)
            lblApply.set_use_markup(True)
            warnDlg.vbox.pack_start(label)
            warnDlg.vbox.pack_start(lblApply)
            label.show()
            lblApply.show()
            #warnDlg.show()
            response = warnDlg.run()
            if response == gtk.RESPONSE_OK:
                warnDlg.destroy()
                self.setPage(self.pageAltBuild)
                # HACK: check in case "create iso" option is unchecked
                # enable/disable iso burn
                self.checkEnableBurnIso()
                return True
            else:
                warnDlg.destroy()
                return False
        elif pageNum == self.pageAltBuild:
            # build
            warnDlg = gtk.Dialog(title=self.appName, parent=None, flags=0, buttons=(gtk.STOCK_NO, gtk.RESPONSE_CANCEL, gtk.STOCK_YES, gtk.RESPONSE_OK))
            warnDlg.set_icon_from_file(self.iconFile)
            warnDlg.vbox.set_spacing(10)
            labelSpc = gtk.Label(" ")
            warnDlg.vbox.pack_start(labelSpc)
            labelSpc.show()
            lblBuildText = _("  <b>Build Alternate CD?</b>  ")
            lblBuildInfo = _("     This may take a few minutes.  Please wait...     ")
            label = gtk.Label(lblBuildText)
            lblInfo = gtk.Label(lblBuildInfo)
            label.set_use_markup(True)
            warnDlg.vbox.pack_start(label)
            warnDlg.vbox.pack_start(lblInfo)
            lblInfo.show()
            label.show()
            #warnDlg.show()
            response = warnDlg.run()
            if response == gtk.RESPONSE_OK:
                warnDlg.destroy()
                self.setBusyCursor()
                gobject.idle_add(self.buildAlternate)
                # change Next text to Finish
                self.wTree.get_widget("buttonNext").set_label("Finish")
                return True
            else:
                warnDlg.destroy()
                return False

        elif pageNum == self.pageFinish:
            # finished... exit
            print _("Exiting...")
            gtk.main_quit()
            sys.exit(0)

    def checkEnableBurnIso(self):
        # show burn iso button if nautilus-cd-burner exists
        if commands.getoutput('which nautilus-cd-burner') != '':
            # make sure iso isn't blank
            if os.path.exists(self.wTree.get_widget("entryLiveIsoFilename").get_text()):
                self.wTree.get_widget("buttonBurnIso").show()
            else:
                self.wTree.get_widget("buttonBurnIso").hide()
        else:
            self.wTree.get_widget("buttonBurnIso").hide()

    def checkEnableBurnAltIso(self):
        # show burn iso button if nautilus-cd-burner exists
        if commands.getoutput('which nautilus-cd-burner') != '':
            # make sure iso isn't blank
            if os.path.exists(self.wTree.get_widget("entryAltBuildIsoFilename").get_text()):
                self.wTree.get_widget("buttonBurnIso").show()
            else:
                self.wTree.get_widget("buttonBurnIso").hide()
        else:
            self.wTree.get_widget("buttonBurnIso").hide()

    def exitApp(self):
        gtk.main_quit()
        sys.exit(0)

    # VMWare Player installation
    def installVmwarePlayer(self):
        try:
            print _("Installing VMWare Player...")
            # tar archive for install
            vmfile = 'VMware-player-1.0.1-19317.tar.gz'
            # check for previously downloaded archive
            if os.path.exists(os.path.join(self.customDir, "root/tmp/vmware-player.tar.gz")) == False:
                # download file
                print _("Downloading VMWare Player archive...")
                # HACK: using wget to download file
                os.popen('wget http://download3.vmware.com/software/vmplayer/' + vmfile + ' -O ' + os.path.join(self.customDir, "root/tmp/vmware-player.tar.gz"))
            # extract
            print _("Extracting VMWare Player archive...")
            os.popen('chroot \"' + os.path.join(self.customDir, "root/") + '\"' + ' tar zxf /tmp/vmware-player.tar.gz -C /tmp/ 1>&2 2>/dev/null')
            print _("Installing dependencies for VMWare Player...")
            os.popen('chroot \"' + os.path.join(self.customDir, "root/") + '\"' + ' apt-get install --assume-yes --force-yes -d gcc make linux-headers-$(uname -r)')
            os.popen('chroot \"' + os.path.join(self.customDir, "root/") + '\"' + ' dpkg -i -R /var/cache/apt/archives/ 1>&2 2>/dev/null')
            os.popen('chroot \"' + os.path.join(self.customDir, "root/") + '\"' + ' apt-get clean')
            os.popen('chroot \"' + os.path.join(self.customDir, "root/") + '\"' + ' apt-get autoclean')
            # create symlink /usr/src/linux
            os.popen('chroot \"' + os.path.join(self.customDir, "root/") + '\"' + ' ln -sf /usr/src/linux-headers-$(uname -r) /usr/src/linux')
            # install (launch xterm for installation/configuration)
            # HACK: write temporary script for chroot & install
            scr = '#!/bin/sh\ncd /tmp/vmware-player-distrib/\n\n/tmp/vmware-player-distrib/vmware-install.pl -d\n'
            f=open(os.path.join(self.customDir, "root/tmp/vmware-player-install.sh"), 'w')
            f.write(scr)
            f.close()
            os.popen('chmod a+x ' + os.path.join(self.customDir, "root/tmp/vmware-player-install.sh"))
            os.popen('xterm -title \'VMWare Player Installation\' -e chroot \"' + os.path.join(self.customDir, "root/") + '\" /tmp/vmware-player-install.sh')

            # cleanup if not running debug
            if self.runningDebug == False:
                print _("Cleaning Up Temporary Files...")
                os.popen('rm -Rf \"' + os.path.join(self.customDir, "root/") + 'tmp/vmware-player-distrib/\"')
                os.popen('rm -Rf \"' + os.path.join(self.customDir, "root/") + 'tmp/vmware-player-install.sh\"')
                os.popen('rm -Rf \"' + os.path.join(self.customDir, "root/") + 'tmp/vmware-player.tar.gz\"')
        except Exception, detail:
            errText = _('Error installing VMWare Player: ')
            print errText, detail
            pass

    # Qemu installation
    def installQemu(self):
        try:
            print _('Installing Qemu Emulator with KQemu Accelerator module...')
            qemuFile = 'qemu-0.8.2-i386.tar.gz'
            kqemuFile = 'kqemu-1.3.0pre9.tar.gz'
            kqemuDir = 'kqemu-1.3.0pre9'
            # check for previously downloaded archive
            if os.path.exists(os.path.join(self.customDir, "root/tmp/qemu.tar.gz")) == False:
                # download file
                print _('Downloading Qemu archive...')
                # HACK: using wget to download file
                os.popen('wget http://fabrice.bellard.free.fr/qemu/' + qemuFile + ' -O ' + os.path.join(self.customDir, "root/tmp/qemu.tar.gz"))
            # check for previously downloaded archive
            if os.path.exists(os.path.join(self.customDir, "root/tmp/kqemu.tar.gz")) == False:
                # download file
                print _('Downloading KQemu module archive...')
                # HACK: using wget to download file
                os.popen('wget http://fabrice.bellard.free.fr/qemu/' + kqemuFile + ' -O ' + os.path.join(self.customDir, "root/tmp/kqemu.tar.gz"))

            # extract to root dir
            print _('Extracting Qemu into /usr/local...')
            os.popen('chroot \"' + os.path.join(self.customDir, "root/") + '\"' + ' tar zxf /tmp/qemu.tar.gz -C / 1>&2 2>/dev/null')
            print _('Extracting KQemu module...')
            os.popen('chroot \"' + os.path.join(self.customDir, "root/") + '\"' + ' tar zxf /tmp/kqemu.tar.gz -C /tmp/ 1>&2 2>/dev/null')
            print _("Installing dependencies for KQemu Compilation...")
            os.popen('chroot \"' + os.path.join(self.customDir, "root/") + '\"' + ' apt-get install --assume-yes --force-yes -d gcc make linux-headers-$(uname -r)')
            os.popen('chroot \"' + os.path.join(self.customDir, "root/") + '\"' + ' dpkg -i -R /var/cache/apt/archives/ 1>&2 2>/dev/null')
            os.popen('chroot \"' + os.path.join(self.customDir, "root/") + '\"' + ' apt-get clean')
            os.popen('chroot \"' + os.path.join(self.customDir, "root/") + '\"' + ' apt-get autoclean')
            # create symlink /usr/src/linux
            # compile kqemu
            print _('Installing KQemu module...')
            # HACK: write temporary script for chroot & install
            scr = '#!/bin/sh\ncd /tmp/' + kqemuDir + '/\n\n./configure 1>&2 2>/dev/null\n make install\n'
            f=open(os.path.join(self.customDir, "root/tmp/kqemu-install.sh"), 'w')
            f.write(scr)
            f.close()
            os.popen('chmod a+x ' + os.path.join(self.customDir, "root/tmp/kqemu-install.sh"))
            os.popen('chroot \"' + os.path.join(self.customDir, "root/") + '\" /tmp/kqemu-install.sh')

            # add module load to sys startup
            print _("Setting KQemu module to load on startup...")
            modExists = False
            f = file(os.path.join(self.customDir, "root/etc/modules"), 'r')
            lines = []
            r = re.compile('kqemu', re.IGNORECASE)
            # find config string
            for line in f:
                if r.search(line) != None:
                    # mark as found
                    modExists = True
                lines.append(line)

            f.close()
            # rewrite if necessary
            if modExists == False:
                f = file(os.path.join(self.customDir, "root/etc/modules"), 'w')
                f.writelines(lines)
                f.write('kqemu\n')
                f.close()

            # cleanup if not running debug
            if self.runningDebug == False:
                print _("Cleaning Up Temporary Files...")
                os.popen('rm -Rf \"' + os.path.join(self.customDir, "root/") + 'tmp/*\"')

        except Exception, detail:
            errText = _('Error Installing QEmu: ')
            print errText, detail
            pass

    # Java installation
    def installJava(self):
        try:
            print _('Installing Java...')
            # HACK: write temporary script for chroot & install
            scr = '#!/bin/sh\napt-get install -y j2re1.4\napt-get clean\napt-get autoclean\nsleep 3\n'
            f=open(os.path.join(self.customDir, "root/tmp/java-install.sh"), 'w')
            f.write(scr)
            f.close()
            os.popen('chmod a+x ' + os.path.join(self.customDir, "root/tmp/java-install.sh"))
            os.popen('xterm -title \'Java Installation\' -e chroot \"' + os.path.join(self.customDir, "root/") + '\" /tmp/java-install.sh')
            # cleanup
            os.popen('rm -Rf \"' + os.path.join(self.customDir, "root/") + 'tmp/java-install.sh\"')

        except Exception, detail:
            os.popen('rm -Rf \"' + os.path.join(self.customDir, "root/") + 'tmp/java-install.sh\"')
            errText = _('Error installing Java: ')
            print errText, detail
            pass

    # Flash installation
    def installFlash(self):
        try:
            print _('Installing Flash...')
            # HACK: write temporary script for chroot & install
            scr = '#!/bin/sh\napt-get install -y flashplugin-nonfree\napt-get clean\napt-get autoclean\nsleep 3\n'
            f=open(os.path.join(self.customDir, "root/tmp/flash-install.sh"), 'w')
            f.write(scr)
            f.close()
            os.popen('chmod a+x ' + os.path.join(self.customDir, "root/tmp/flash-install.sh"))
            os.popen('xterm -title \'Flash Installation\' -e chroot \"' + os.path.join(self.customDir, "root/") + '\" /tmp/flash-install.sh')
            # cleanup
            os.popen('rm -Rf \"' + os.path.join(self.customDir, "root/") + 'tmp/flash-install.sh\"')

        except Exception, detail:
            os.popen('rm -Rf \"' + os.path.join(self.customDir, "root/") + 'tmp/flash-install.sh\"')
            errText = _('Error installing Flash: ')
            print errText, detail
            pass

    # Usplash Generation
    def generateUsplash(self, pngFilename, outputFilename):
        try:
            print _('Generating Usplash library...')
            if self.cdUbuntuVersion == self.dapperVersion:
                # create tmp working dir
                os.popen('mkdir /tmp/usplash')
                # copy png to tmp dir
                os.popen('cp ' + pngFilename + ' /tmp/usplash/usplash-artwork.png')
                # generate usplash
                os.popen('cd /tmp/usplash ; pngtobogl usplash-artwork.png > usplash-artwork.c')
                os.popen('cd /tmp/usplash ; gcc -Os -g -I/usr/include/bogl -fPIC -c usplash-artwork.c -o usplash-artwork.o')
                os.popen('cd /tmp/usplash ; gcc -shared -Wl,-soname,usplash-artwork.so usplash-artwork.o -o ' + outputFilename)
                # cleanup
                os.popen('rm -Rf /tmp/usplash')
            else:
                # create tmp working dir
                if os.path.exists("/tmp/usplash") != True:
                    os.makedirs("/tmp/usplash")
                # copy user's .png
                os.popen('cp -f \"' + pngFilename + '\" ' + '/tmp/usplash/usplash.png')
                # copy needed libraries and .png's
                os.popen('cp -f \"' + os.getcwd() + '/lib/usplash-theme.c\" ' + '/tmp/usplash/')
                os.popen('cp -f \"' + os.getcwd() + '/lib/throbber_back.png\" ' + '/tmp/usplash/')
                os.popen('cp -f \"' + os.getcwd() + '/lib/throbber_fore.png\" ' + '/tmp/usplash/')
                # generate .c source
                print _("Generating .c source files...")
                os.popen('cd /tmp/usplash ; pngtousplash usplash.png > usplash.c')
                os.popen('cd /tmp/usplash ; pngtousplash throbber_back.png > throbber_back.c')
                os.popen('cd /tmp/usplash ; pngtousplash throbber_fore.png > throbber_fore.c')
                # compile .c to .o
                print _("Compiling .c source files...")
                os.popen('cd /tmp/usplash ; gcc -g -Wall -fPIC -o usplash.o -c usplash.c')
                os.popen('cd /tmp/usplash ; gcc -g -Wall -fPIC -o throbber_back.o -c throbber_back.c')
                os.popen('cd /tmp/usplash ; gcc -g -Wall -fPIC -o throbber_fore.o -c throbber_fore.c')
                os.popen('cd /tmp/usplash ; gcc -g -Wall -fPIC -o usplash-theme.o -c usplash-theme.c')
                # compile to shared library
                print _("Compiling to .so...")
                #os.popen('gcc -g -Wall -fPIC -shared -o \"' + outputFilename + '\" ' + '/tmp/usplash/usplash_artwork.o /tmp/usplash/throbber_back.o /tmp/usplash/throbber_fore.o /tmp/usplash/usplash-theme.o')
                os.popen('cd /tmp/usplash ; gcc -g -Wall -fPIC -shared -o \"' + outputFilename + '\" ' + '*.o')
                # cleanup
                os.popen('rm -Rf /tmp/usplash')

        except Exception, detail:
            # cleanup
            os.popen('rm -Rf /tmp/usplash')
            errText = _('Error generating Usplash library: ')
            print errText, detail
            pass

    # launch chroot terminal
    def launchTerminal(self):
        try:
            # setup environment
            # copy dns info
            print _("Copying DNS info...")
            os.popen('cp -f /etc/resolv.conf ' + os.path.join(self.customDir, "root/etc/resolv.conf"))
            # mount /proc
            print _("Mounting /proc filesystem...")
            os.popen('mount --bind /proc \"' + os.path.join(self.customDir, "root/proc") + '\"')
            # copy apt.conf
            print _("Copying apt.conf configuration...")
            os.popen('cp -f /etc/apt/apt.conf ' + os.path.join(self.customDir, "root/etc/apt/apt.conf"))
            # copy wgetrc
            print _("Copying wgetrc configuration...")
            # backup
            os.popen('mv -f \"' + os.path.join(self.customDir, "root/etc/wgetrc") + '\" \"' + os.path.join(self.customDir, "root/etc/wgetrc.orig") + '\"')
            os.popen('cp -f /etc/wgetrc ' + os.path.join(self.customDir, "root/etc/wgetrc"))
            # HACK: create temporary script for chrooting
            scr = '#!/bin/sh\n#\n#\t(c) reconstructor, 2006\n#\nchroot ' + os.path.join(self.customDir, "root/") + '\n'
            f=open('/tmp/reconstructor-terminal.sh', 'w')
            f.write(scr)
            f.close()
            os.popen('chmod a+x ' + os.path.join(self.customDir, "/tmp/reconstructor-terminal.sh"))
            # TODO: replace default terminal title with "Reconstructor Terminal"
            # use gnome-terminal if available -- more features
            if commands.getoutput('which gnome-terminal') != '':
                print _('Launching Gnome-Terminal for advanced customization...')
                os.popen('export HOME=/root ; gnome-terminal --hide-menubar -t \"Reconstructor Terminal\" -e \"/tmp/reconstructor-terminal.sh\"')
            else:
                print _('Launching Xterm for advanced customization...')
                # use xterm if gnome-terminal isn't available
                os.popen('export HOME=/root ; xterm -bg black -fg white -rightbar -title \"Reconstructor Terminal\" -e /tmp/reconstructor-terminal.sh')

            # restore wgetrc
            print _("Restoring wgetrc configuration...")
            os.popen('mv -f \"' + os.path.join(self.customDir, "root/etc/wgetrc.orig") + '\" \"' + os.path.join(self.customDir, "root/etc/wgetrc") + '\"')
            # remove apt.conf
            print _("Removing apt.conf configuration...")
            os.popen('rm -Rf \"' + os.path.join(self.customDir, "root/etc/apt/apt.conf") + '\"')
            # remove dns info
            print _("Removing DNS info...")
            os.popen('rm -Rf \"' + os.path.join(self.customDir, "root/etc/resolv.conf") + '\"')
            # umount /proc
            print _("Umounting /proc...")
            os.popen('umount \"' + os.path.join(self.customDir, "root/proc/") + '\"')
            # remove temp script
            os.popen('rm -Rf /tmp/reconstructor-terminal.sh')

        except Exception, detail:
            # restore settings
            # restore wgetrc
            print _("Restoring wgetrc configuration...")
            os.popen('mv -f \"' + os.path.join(self.customDir, "root/etc/wgetrc.orig") + '\" \"' + os.path.join(self.customDir, "root/etc/wgetrc") + '\"')
            # remove apt.conf
            print _("Removing apt.conf configuration...")
            os.popen('rm -Rf \"' + os.path.join(self.customDir, "root/etc/apt/apt.conf") + '\"')
            # remove dns info
            print _("Removing DNS info...")
            os.popen('rm -Rf \"' + os.path.join(self.customDir, "root/etc/resolv.conf") + '\"')
            # umount /proc
            print _("Umounting /proc...")
            os.popen('umount \"' + os.path.join(self.customDir, "root/proc/") + '\"')
            # remove temp script
            os.popen('rm -Rf /tmp/reconstructor-terminal.sh')

            errText = _('Error launching terminal: ')
            print errText, detail
            pass

        return

    # Sets live cd information (username, full name, hostname) for live cd
    def setLiveCdInfo(self, username, userFullname, userPassword, hostname):
        try:
            reUsername = None
            reFullname = None
            reHost = None
            conf = ''
            # dapper
            if self.cdUbuntuVersion == self.dapperVersion:
                # set live cd info
                f = open(os.path.join(self.customDir, "initrd/scripts/casper"), 'r')
                # regex for username
                reUsername = re.compile('USERNAME=\S+', re.IGNORECASE)
                # regex for user full name
                reFullname = re.compile('USERFULLNAME=\S+', re.IGNORECASE)
                # regex for hostname
                reHost = re.compile('HOST=\S+', re.IGNORECASE)
                # search
                for l in f:
                    if reUsername.search(l) != None:
                        if username != '':
                            #print ('Username: ' + l)
                            usernameText = _('Live CD Username: ')
                            print usernameText + username
                            l = 'USERNAME=\"' + username + '\"\n'
                    if reFullname.search(l) != None:
                        if userFullname != '':
                            #print ('User Full Name: ' + l)
                            userFullnameText = _('Live CD User Full name: ')
                            print userFullnameText + userFullname
                            l = 'USERFULLNAME=\"' + userFullname + '\"\n'
                    if reHost.search(l) != None:
                        if hostname != '':
                            #print ('Hostname: ' + l)
                            hostnameText = _('Live CD Hostname: ')
                            print hostnameText + hostname
                            l = 'HOST=\"' + hostname + '\"\n'

                    conf += l
            # edgy
            elif self.cdUbuntuVersion == self.edgyVersion or self.cdUbuntuVersion == self.feistyVersion:
                # set live cd info
                f = open(os.path.join(self.customDir, "initrd/etc/casper.conf"), 'r')
                # regex for username
                reUsername = re.compile('export\sUSERNAME=\S+', re.IGNORECASE)
                # regex for user full name
                reFullname = re.compile('export\sUSERFULLNAME=\S+', re.IGNORECASE)
                # regex for hostname
                reHost = re.compile('export\sHOST=\S+', re.IGNORECASE)
                # search
                for l in f:
                    if reUsername.search(l) != None:
                        if username != '':
                            #print ('Username: ' + l)
                            usernameText = _('Live CD Username: ')
                            print usernameText + username
                            l = 'export USERNAME=\"' + username + '\"\n'
                    if reFullname.search(l) != None:
                        if userFullname != '':
                            #print ('User Full Name: ' + l)
                            userFullnameText = _('Live CD User Full name: ')
                            print userFullnameText + userFullname
                            l = 'export USERFULLNAME=\"' + userFullname + '\"\n'
                    if reHost.search(l) != None:
                        if hostname != '':
                            #print ('Hostname: ' + l)
                            hostnameText = _('Live CD Hostname: ')
                            print hostnameText + hostname
                            l = 'export HOST=\"' + hostname + '\"\n'

                    conf += l

                # close file
                f.close()

            # dapper
            if self.cdUbuntuVersion == self.dapperVersion:
                # re-write new file
                fc = open(os.path.join(self.customDir, "initrd/scripts/casper"), 'w')
                fc.write(conf)
                fc.close()
                # set execute bit for script
                os.popen('chmod a+x \"' + os.path.join(self.customDir, "initrd/scripts/casper") + '\"')
            # edgy
            elif self.cdUbuntuVersion == self.edgyVersion or self.cdUbuntuVersion == self.feistyVersion:
                # re-write new file
                fc = open(os.path.join(self.customDir, "initrd/etc/casper.conf"), 'w')
                fc.write(conf)
                fc.close()
                # set execute bit for script
                os.popen('chmod a+x \"' + os.path.join(self.customDir, "initrd/etc/casper.conf") + '\"')
            # unknown
            else:
                print _('Unknown Ubuntu Version.  Cannot set user/host info.')

            # set password
            fp = open(os.path.join(self.customDir, "initrd/scripts/casper-bottom/10adduser"), 'r')
            # regex for username
            rePassword = re.compile('set passwd/user-password-crypted\s\w+', re.IGNORECASE)
            conf = ''
            # search
            for l in fp:
                if rePassword.search(l) != None:
                    if userPassword != '':
                        #print ('Password: ' + l)
                        passwordText = _('Setting Live CD Password... ')
                        print passwordText
                        #print "DEBUG: Password: " + userPassword + " des Hash: " + commands.getoutput('echo ' + userPassword + ' | mkpasswd -s -H des')
                        l = 'set passwd/user-password-crypted ' + commands.getoutput('echo ' + userPassword + ' | mkpasswd -s -H des') + '\n'

                conf += l
            # close file
            fp.close()

            # re-write new file
            fpc = open(os.path.join(self.customDir, "initrd/scripts/casper-bottom/10adduser"), 'w')
            fpc.write(conf)
            fpc.close()
            # set execute bit for script
            os.popen('chmod a+x \"' + os.path.join(self.customDir, "initrd/scripts/casper-bottom/10adduser") + '\"')

        except Exception, detail:
            errText = _('Error setting user info: ')
            print errText, detail
            pass

    # Burns ISO
    def burnIso(self):
        try:
            if commands.getoutput('which nautilus-cd-burner') != '':
                print _('Burning ISO...')
                os.popen('nautilus-cd-burner --source-iso=\"' + self.buildLiveCdFilename + '\"')
            else:
                print _('Error: nautilus-cd-burner is needed for burning iso files... ')

        except Exception, detail:
            errText = _('Error burning ISO: ')
            print errText, detail
            pass

    def burnAltIso(self):
        try:
            if commands.getoutput('which nautilus-cd-burner') != '':
                print _('Burning ISO...')
                os.popen('nautilus-cd-burner --source-iso=\"' + self.buildAltCdFilename + '\"')
            else:
                print _('Error: nautilus-cd-burner is needed for burning iso files... ')

        except Exception, detail:
            errText = _('Error burning ISO: ')
            print errText, detail
            pass

    def loadBootMenuColor(self):
        try:
            print _("Loading Boot Menu Color...")
            if os.path.exists(os.path.join(self.customDir, "remaster/isolinux/isolinux.cfg")):
                #color = self.wTree.get_widget("colorbuttonBrowseLiveCdTextColor").get_color()
                #rgbColor = color.red/255, color.green/255, color.blue/255
                #hexColor = '%02x%02x%02x' % rgbColor
                # find text color config line in isolinux.cfg
                f = file(os.path.join(self.customDir, "remaster/isolinux/isolinux.cfg"), 'r')
                color = ''
                line = ''
                # config line regex
                r = re.compile('GFXBOOT-BACKGROUND*', re.IGNORECASE)
                # find config string
                for l in f:
                    if r.search(l) != None:
                        line = l

                f.close()
                # color regex
                r = re.compile('\w+-\w+\s\d\w(\w+)', re.IGNORECASE)
                m = r.match(line)
                color = m.group(1)
                print _('Live CD Text Color: ') + color
                # set colorbutton to color
                self.wTree.get_widget("colorbuttonBrowseLiveCdTextColor").set_color(gtk.gdk.color_parse('#' + color))
        except Exception, detail:
            errText = _("Error getting boot menu color: ")
            print errText, detail
            pass

    def loadGdmBackgroundColor(self):
        try:
            print _("Loading GDM Background Color...")
            if os.path.exists(os.path.join(self.customDir, "root/etc/gdm/gdm.conf-custom")):
                # find text color config line in gdm.conf-custom
                f = file(os.path.join(self.customDir, "root/etc/gdm/gdm.conf-custom"), 'r')
                color = ''
                line = ''
                # config line regex
                r = re.compile('GraphicalThemedColor*', re.IGNORECASE)
                # find config string
                for l in f:
                    if r.search(l) != None:
                        line = l

                f.close()
                if line == '':
                    print _('GDM background color not found in gdm.conf-custom. Using gdm.conf...')
                    # get from gdm.conf
                    # find text color config line in gdm.conf
                    f = file(os.path.join(self.customDir, "root/etc/gdm/gdm.conf"), 'r')
                    color = ''
                    line = ''
                    # config line regex
                    r = re.compile('GraphicalThemedColor*', re.IGNORECASE)
                    # find config string
                    for l in f:
                        if r.search(l) != None:
                            line = l

                    f.close()
                # color regex
                r = re.compile('\w+=#(\w+)', re.IGNORECASE)
                m = r.match(line)
                color = m.group(1)
                print _('GDM Background Color: ') + color
                # set var & colorbutton to color
                self.gdmBackgroundColor = color
                self.wTree.get_widget("colorbuttonBrowseGdmBackgroundColor").set_color(gtk.gdk.color_parse('#' + color))

        except Exception, detail:
            errText = _("Error getting GDM background color: ")
            print errText, detail
            pass

    # startup optimization
    def optimizeStartup(self):
        try:
            print _('Optimizing Startup...')
            # HACK: create temp script to set links...
            scr = '#!/bin/sh\n#\n# startup-optimize.sh\n#\t(c) reconstructor team, 2006\n\n'
            # get startup daemons and set accordingly
            # ppp
            if self.wTree.get_widget("checkbuttonStartupPpp").get_active() == True:
                print _('Enabling Startup Daemon: ppp')
                scr += 'cd /etc/rc2.d ; ln -s ../init.d/ppp S14ppp 1>&2 2>/dev/null\n'
                scr += 'cd /etc/rc3.d ; ln -s ../init.d/ppp S14ppp 1>&2 2>/dev/null\n'
                scr += 'cd /etc/rc4.d ; ln -s ../init.d/ppp S14ppp 1>&2 2>/dev/null\n'
                scr += 'cd /etc/rc5.d ; ln -s ../init.d/ppp S14ppp 1>&2 2>/dev/null\n'
            else:
                print _('Disabling Startup Daemon: ppp')
                scr += 'rm /etc/rc2.d/S14ppp 1>&2 2>/dev/null\n'
                scr += 'rm /etc/rc3.d/S14ppp 1>&2 2>/dev/null\n'
                scr += 'rm /etc/rc4.d/S14ppp 1>&2 2>/dev/null\n'
                scr += 'rm /etc/rc5.d/S14ppp 1>&2 2>/dev/null\n'
            # hplip
            if self.wTree.get_widget("checkbuttonStartupHplip").get_active() == True:
                print _('Enabling Startup Daemon: hplip')
                scr += 'cd /etc/rc2.d ; ln -s ../init.d/hplip S18hplip 1>&2 2>/dev/null\n'
                scr += 'cd /etc/rc3.d ; ln -s ../init.d/hplip S18hplip 1>&2 2>/dev/null\n'
                scr += 'cd /etc/rc4.d ; ln -s ../init.d/hplip S18hplip 1>&2 2>/dev/null\n'
                scr += 'cd /etc/rc5.d ; ln -s ../init.d/hplip S18hplip 1>&2 2>/dev/null\n'
            else:
                print _('Disabling Startup Daemon: hplip')
                scr += 'rm /etc/rc2.d/S18hplip 1>&2 2>/dev/null\n'
                scr += 'rm /etc/rc3.d/S18hplip 1>&2 2>/dev/null\n'
                scr += 'rm /etc/rc4.d/S18hplip 1>&2 2>/dev/null\n'
                scr += 'rm /etc/rc5.d/S18hplip 1>&2 2>/dev/null\n'
            # cupsys
            if self.wTree.get_widget("checkbuttonStartupCupsys").get_active() == True:
                print _('Enabling Startup Daemon: cupsys')
                scr += 'cd /etc/rc2.d ; ln -s ../init.d/cupsys S19cupsys 1>&2 2>/dev/null\n'
                scr += 'cd /etc/rc3.d ; ln -s ../init.d/cupsys S19cupsys 1>&2 2>/dev/null\n'
                scr += 'cd /etc/rc4.d ; ln -s ../init.d/cupsys S19cupsys 1>&2 2>/dev/null\n'
                scr += 'cd /etc/rc5.d ; ln -s ../init.d/cupsys S19cupsys 1>&2 2>/dev/null\n'
            else:
                print _('Disabling Startup Daemon: cupsys')
                scr += 'rm /etc/rc2.d/S19cupsys 1>&2 2>/dev/null\n'
                scr += 'rm /etc/rc3.d/S19cupsys 1>&2 2>/dev/null\n'
                scr += 'rm /etc/rc4.d/S19cupsys 1>&2 2>/dev/null\n'
                scr += 'rm /etc/rc5.d/S19cupsys 1>&2 2>/dev/null\n'
            # festival
            if self.wTree.get_widget("checkbuttonStartupFestival").get_active() == True:
                print _('Enabling Startup Daemon: festival')
                scr += 'cd /etc/rc2.d ; ln -s ../init.d/festival S20festival 1>&2 2>/dev/null\n'
                scr += 'cd /etc/rc3.d ; ln -s ../init.d/festival S20festival 1>&2 2>/dev/null\n'
                scr += 'cd /etc/rc4.d ; ln -s ../init.d/festival S20festival 1>&2 2>/dev/null\n'
                scr += 'cd /etc/rc5.d ; ln -s ../init.d/festival S20festival 1>&2 2>/dev/null\n'
            else:
                print _('Disabling Startup Daemon: festival')
                scr += 'rm /etc/rc2.d/S20festival 1>&2 2>/dev/null\n'
                scr += 'rm /etc/rc3.d/S20festival 1>&2 2>/dev/null\n'
                scr += 'rm /etc/rc4.d/S20festival 1>&2 2>/dev/null\n'
                scr += 'rm /etc/rc5.d/S20festival 1>&2 2>/dev/null\n'
            # laptop-mode
            if self.wTree.get_widget("checkbuttonStartupLaptopMode").get_active() == True:
                print _('Enabling Startup Daemon: laptop-mode')
                scr += 'cd /etc/rc2.d ; ln -s ../init.d/laptop-mode S20laptop-mode 1>&2 2>/dev/null\n'
                scr += 'cd /etc/rc3.d ; ln -s ../init.d/laptop-mode S20laptop-mode 1>&2 2>/dev/null\n'
                scr += 'cd /etc/rc4.d ; ln -s ../init.d/laptop-mode S20laptop-mode 1>&2 2>/dev/null\n'
                scr += 'cd /etc/rc5.d ; ln -s ../init.d/laptop-mode S20laptop-mode 1>&2 2>/dev/null\n'
            else:
                print _('Disabling Startup Daemon: laptop-mode')
                scr += 'rm /etc/rc2.d/S20laptop-mode 1>&2 2>/dev/null\n'
                scr += 'rm /etc/rc3.d/S20laptop-mode 1>&2 2>/dev/null\n'
                scr += 'rm /etc/rc4.d/S20laptop-mode 1>&2 2>/dev/null\n'
                scr += 'rm /etc/rc5.d/S20laptop-mode 1>&2 2>/dev/null\n'
            # nvidia-kernel
            if self.wTree.get_widget("checkbuttonStartupNvidiaKernel").get_active() == True:
                print _('Enabling Startup Daemon: nvidia-kernel')
                scr += 'cd /etc/rc2.d ; ln -s ../init.d/nvidia-kernel S20nvidia-kernel 1>&2 2>/dev/null\n'
                scr += 'cd /etc/rc3.d ; ln -s ../init.d/nvidia-kernel S20nvidia-kernel 1>&2 2>/dev/null\n'
                scr += 'cd /etc/rc4.d ; ln -s ../init.d/nvidia-kernel S20nvidia-kernel 1>&2 2>/dev/null\n'
                scr += 'cd /etc/rc5.d ; ln -s ../init.d/nvidia-kernel S20nvidia-kernel 1>&2 2>/dev/null\n'
            else:
                print _('Disabling Startup Daemon: nvidia-kernel')
                scr += 'rm /etc/rc2.d/S20nvidia-kernel 1>&2 2>/dev/null\n'
                scr += 'rm /etc/rc3.d/S20nvidia-kernel 1>&2 2>/dev/null\n'
                scr += 'rm /etc/rc4.d/S20nvidia-kernel 1>&2 2>/dev/null\n'
                scr += 'rm /etc/rc5.d/S20nvidia-kernel 1>&2 2>/dev/null\n'
            # rsync
            if self.wTree.get_widget("checkbuttonStartupRsync").get_active() == True:
                print _('Enabling Startup Daemon: rsync')
                scr += 'cd /etc/rc2.d ; ln -s ../init.d/rsync S20rsync 1>&2 2>/dev/null\n'
                scr += 'cd /etc/rc3.d ; ln -s ../init.d/rsync S20rsync 1>&2 2>/dev/null\n'
                scr += 'cd /etc/rc4.d ; ln -s ../init.d/rsync S20rsync 1>&2 2>/dev/null\n'
                scr += 'cd /etc/rc5.d ; ln -s ../init.d/rsync S20rsync 1>&2 2>/dev/null\n'
            else:
                print _('Disabling Startup Daemon: rsync')
                scr += 'rm /etc/rc2.d/S20rsync 1>&2 2>/dev/null\n'
                scr += 'rm /etc/rc3.d/S20rsync 1>&2 2>/dev/null\n'
                scr += 'rm /etc/rc4.d/S20rsync 1>&2 2>/dev/null\n'
                scr += 'rm /etc/rc5.d/S20rsync 1>&2 2>/dev/null\n'
            # bluez-utils
            if self.wTree.get_widget("checkbuttonStartupBluezUtils").get_active() == True:
                print _('Enabling Startup Daemon: bluez-utils')
                scr += 'cd /etc/rc2.d ; ln -s ../init.d/bluez-utils S25bluez-utils 1>&2 2>/dev/null\n'
                scr += 'cd /etc/rc3.d ; ln -s ../init.d/bluez-utils S25bluez-utils 1>&2 2>/dev/null\n'
                scr += 'cd /etc/rc4.d ; ln -s ../init.d/bluez-utils S25bluez-utils 1>&2 2>/dev/null\n'
                scr += 'cd /etc/rc5.d ; ln -s ../init.d/bluez-utils S25bluez-utils 1>&2 2>/dev/null\n'
            else:
                print _('Disabling Startup Daemon: bluez-utils')
                scr += 'rm /etc/rc2.d/S25bluez-utils 1>&2 2>/dev/null\n'
                scr += 'rm /etc/rc3.d/S25bluez-utils 1>&2 2>/dev/null\n'
                scr += 'rm /etc/rc4.d/S25bluez-utils 1>&2 2>/dev/null\n'
                scr += 'rm /etc/rc5.d/S25bluez-utils 1>&2 2>/dev/null\n'
            # mdadm
            if self.wTree.get_widget("checkbuttonStartupMdadm").get_active() == True:
                print _('Enabling Startup Daemon: mdadm')
                scr += 'cd /etc/rc2.d ; ln -s ../init.d/mdadm S25mdadm 1>&2 2>/dev/null\n'
                scr += 'cd /etc/rc3.d ; ln -s ../init.d/mdadm S25mdadm 1>&2 2>/dev/null\n'
                scr += 'cd /etc/rc4.d ; ln -s ../init.d/mdadm S25mdadm 1>&2 2>/dev/null\n'
                scr += 'cd /etc/rc5.d ; ln -s ../init.d/mdadm S25mdadm 1>&2 2>/dev/null\n'
            else:
                print _('Disabling Startup Daemon: mdadm')
                scr += 'rm /etc/rc2.d/S25mdadm 1>&2 2>/dev/null\n'
                scr += 'rm /etc/rc3.d/S25mdadm 1>&2 2>/dev/null\n'
                scr += 'rm /etc/rc4.d/S25mdadm 1>&2 2>/dev/null\n'
                scr += 'rm /etc/rc5.d/S25mdadm 1>&2 2>/dev/null\n'



            f=open(os.path.join(self.customDir, "root/tmp/startup-optimize.sh"), 'w')
            f.write(scr)
            f.close()
            os.popen('chmod a+x \"' + os.path.join(self.customDir, "root/tmp/startup-optimize.sh") + '\"')
            os.popen('chroot \"' + os.path.join(self.customDir, "root/") + '\" /tmp/startup-optimize.sh')
            # cleanup
            os.popen('rm -Rf \"' + os.path.join(self.customDir, "root/tmp/startup-optimize.sh") + '\"')

        except Exception, detail:
            self.setDefaultCursor()
            errText = _('Error setting startup daemons: ')
            print errText, detail
            pass

    # shutdown optimization
    def optimizeShutdown(self):
        try:
            print _('Optimizing shutdown scripts...')
            for s in self.shutdownScripts:
                # rename script to make inactive
                os.popen('mv ' + os.path.join(self.customDir, "root/etc/rc0.d/") + 'K' + s + ' ' + os.path.join(self.customDir, "root/etc/rc0.d/") + '_' + s + ' 1>&2 2>/dev/null')
        except Exception, detail:
            errText = _('Error optimizing shutdown scripts: ')
            print errText, detail
            pass

    # restore original shutdown
    def restoreShutdown(self):
        try:
            print _('Restoring original shutdown scripts...')
            for s in self.shutdownScripts:
                # rename script to make active
                os.popen('mv ' + os.path.join(self.customDir, "root/etc/rc0.d/") + '_' + s + ' ' + os.path.join(self.customDir, "root/etc/rc0.d/") + 'K' + s + ' 1>&2 2>/dev/null')
            # unselect optimization
            self.wTree.get_widget("checkbuttonOptimizationShutdown").set_active(False)
            self.setDefaultCursor()
        except Exception, detail:
            self.setDefaultCursor()
            errText = _('Error restoring original shutdown scripts: ')
            print errText, detail
            pass

    def loadGdmThemes(self):
        try:
            print _("Loading GDM Themes...")
            themesDir = None
            if os.path.exists(os.path.join(self.customDir, "root/usr/share/gdm/themes/")):
                themesDir = os.path.join(self.customDir, "root/usr/share/gdm/themes/")
            themes = []
            # find themes
            if themesDir != None:
                for themeItem in os.listdir(themesDir):
                    # if dir, check
                    themeItemDir = os.path.join(themesDir, themeItem)
                    if os.path.isdir(themeItemDir):
                        # check for theme
                        if os.path.exists(os.path.join(themeItemDir, "GdmGreeterTheme.desktop")):
                            # is theme, add to list
                            themes.append(themeItem)

            # add items to combobox
            themeList = gtk.ListStore(gobject.TYPE_STRING)
            for theme in themes:
                themeList.append([theme])

            self.wTree.get_widget("comboboxentryGnomeGdmTheme").set_model(themeList)
            self.wTree.get_widget("comboboxentryGnomeGdmTheme").set_text_column(0)
        except Exception, detail:
            errText = _("Error loading GDM Themes: ")
            print errText, detail
            pass
    def loadGnomeThemes(self):
        try:
            print _("Loading Gnome Themes and Icons...")
            themesDir = None
            iconsDir = None
            if os.path.exists(os.path.join(self.customDir, "root/usr/share/themes/")):
                themesDir = os.path.join(self.customDir, "root/usr/share/themes/")
            if os.path.exists(os.path.join(self.customDir, "root/usr/share/icons/")):
                iconsDir = os.path.join(self.customDir, "root/usr/share/icons/")
            themes = []
            borders = []
            icons = []
            # find themes
            if themesDir != None:
                for themeItem in os.listdir(themesDir):
                    # if dir, check
                    themeItemDir = os.path.join(themesDir, themeItem)
                    if os.path.isdir(themeItemDir):
                        # check for theme
                        if os.path.exists(os.path.join(themeItemDir, "gtk-2.0/")):
                            # is theme, add to list
                            themes.append(themeItem)
                        # check for controls
                        if os.path.exists(os.path.join(themeItemDir, "metacity-1/")):
                            borders.append(themeItem)

            # find icons
            if iconsDir != None:
                for iconItem in os.listdir(iconsDir):
                    # if dir, check for icons
                    iconItemDir = os.path.join(iconsDir, iconItem)
                    if os.path.isdir(iconItemDir):
                        # check for icon index
                        if os.path.exists(os.path.join(iconItemDir, "index.theme")):
                            # index exists, add to list
                            icons.append(iconItem)

            # add items to comboboxes
            themeList = gtk.ListStore(gobject.TYPE_STRING)
            borderList = gtk.ListStore(gobject.TYPE_STRING)
            iconList = gtk.ListStore(gobject.TYPE_STRING)
            for theme in themes:
                themeList.append([theme])
            for border in borders:
                borderList.append([border])
            for icon in icons:
                iconList.append([icon])

            self.wTree.get_widget("comboboxentryGnomeTheme").set_model(themeList)
            self.wTree.get_widget("comboboxentryGnomeTheme").set_text_column(0)
            self.wTree.get_widget("comboboxentryGnomeThemeWindowBorders").set_model(borderList)
            self.wTree.get_widget("comboboxentryGnomeThemeWindowBorders").set_text_column(0)
            self.wTree.get_widget("comboboxentryGnomeThemeIcons").set_model(iconList)
            self.wTree.get_widget("comboboxentryGnomeThemeIcons").set_text_column(0)
        except Exception, detail:
            errText = _("Error loading Gnome themes: ")
            print errText, detail
            pass

    def calculateIsoSize(self):
        try:
            # reset current size
            self.wTree.get_widget("labelSoftwareIsoSize").set_text("")
            totalSize = None
            remasterSize = 0
            rootSize = 0
            squashSize = 0
            print _('Calculating Live ISO Size...')
            # regex for extracting size
            r = re.compile('(\d+)\s', re.IGNORECASE)
            # get size of remaster dir - use du -s (it's faster)
            remaster = commands.getoutput('du -s ' + os.path.join(self.customDir, "remaster/"))
            mRemaster = r.match(remaster)
            remasterSize = int(mRemaster.group(1))
            # subtract squashfs root
            if os.path.exists(os.path.join(self.customDir, "remaster/casper/filesystem.squashfs")):
                squash = commands.getoutput('du -s ' + os.path.join(self.customDir, "remaster/casper/filesystem.squashfs"))
                mSquash = r.match(squash)
                squashSize = int(mSquash.group(1))

            remasterSize -= squashSize
            # get size of root dir
            root = commands.getoutput('du -s ' + os.path.join(self.customDir, "root/"))
            mRoot = r.match(root)
            rootSize = int(mRoot.group(1))

            # divide root size to simulate squash compression
            self.wTree.get_widget("labelSoftwareIsoSize").set_text( '~ ' + str(int(round((remasterSize + (rootSize/3.185))/1024))) + ' MB')
            self.setDefaultCursor()
            # set page here - since this is run on a background thread,
            # the next page will show too quickly if set in self.checkPage()
            self.setPage(self.pageLiveCustomize)
        except Exception, detail:
            errText = _("Error calculating estimated iso size: ")
            print errText, detail
            pass

    def calculateAltIsoSize(self):
        try:
            # reset current size
            self.wTree.get_widget("labelAltIsoSize").set_text("")
            totalSize = None
            remasterSize = 0
            print _('Calculating Alternate ISO Size...')
            # regex for extracting size
            r = re.compile('(\d+)\s', re.IGNORECASE)
            # get size of remaster dir - use du -s (it's faster)
            remaster = commands.getoutput('du -s ' + os.path.join(self.customDir, self.altRemasterDir))
            mRemaster = r.match(remaster)
            remasterSize = int(mRemaster.group(1))

            self.wTree.get_widget("labelAltIsoSize").set_text( '~ ' + str(int(round(remasterSize/1024))) + ' MB')
            self.setDefaultCursor()
            # set page here - since this is run on a background thread,
            # the next page will show too quickly if set in self.checkPage()
            self.setPage(self.pageAltCustomize)
        except Exception, detail:
            errText = _("Error calculating estimated iso size: ")
            print errText, detail
            pass

    def startInteractiveEdit(self):
        print _('Beginning Interactive Editing...')
        # set interactive edit tag
        self.interactiveEdit = True
        # check for template user home directory; create if necessary
        #print ('useradd -d /home/reconstructor -m -s /bin/bash -p ' + str(os.urandom(8)))
        if os.path.exists('/home/reconstructor') == False:
            # create user with random password
            password = 'r0714'
            os.popen('useradd -d /home/reconstructor -s /bin/bash -p ' + password +' reconstructor')
            # create home dir
            os.popen('mkdir -p /home/reconstructor')
            # change owner of home
            os.popen('chown -R reconstructor /home/reconstructor')
        # launch Xnest in background
        try:
            print _('Starting Xnest in the background...')
            os.popen('Xnest :1 -ac -once & 1>&2 2>/dev/null')
        except Exception, detail:
            errXnest = _("Error starting Xnest: ")
            print errXnest, detail
            return
        # try to start gnome-session with template user
        try:
            print _('Starting Gnome-Session....')
            #os.popen('chroot \"' + os.path.join(self.customDir, "root/") + '\" ' + 'su -c \"export DISPLAY=localhost:1 ; gnome-session\" 1>&2 2>/dev/null\"')
            #os.popen("chroot /home/ehazlett/reconstructor/root \"/tmp/test.sh\"")
            os.popen('su reconstructor -c \"export DISPLAY=:1 ; gnome-session\" 1>&2 2>/dev/null')
        except Exception, detail:
            errGnome = _("Error starting Gnome-Session: ")
            print errGnome, detail
            return

    def clearInteractiveSettings(self):
        try:
            print _('Clearing Interactive Settings...')
            print _('Removing \'reconstructor\' user...')
            os.popen('userdel reconstructor')
            print _('Removing \'reconstructor\' home directory...')
            os.popen('rm -Rf /home/reconstructor')
            self.setDefaultCursor()
        except Exception, detail:
            self.setDefaultCursor()
            errText = _('Error clearing interactive settings: ')
            print errText, detail
            pass

    def getGpgKeyInfo(self):
        # show dialog for key info
        keyDlg = gtk.Dialog(title="Installation Key", parent=None, flags=0, buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OK, gtk.RESPONSE_OK))
        keyDlg.set_icon_from_file('glade/app.png')
        keyDlg.vbox.set_spacing(10)
        labelSpc = gtk.Label(" ")
        keyDlg.vbox.pack_start(labelSpc)
        labelSpc.show()
        infoText = _("<b>GPG Installation Key Information</b>")
        lblInfo = gtk.Label(infoText)
        lblInfo.set_use_markup(True)
        # email entry
        hboxEmail = gtk.HBox()
        emailText = _("Email:")
        labelEmail = gtk.Label(emailText)
        hboxEmail.pack_start(labelEmail, expand=False, fill=False, padding=5)
        entryEmail = gtk.Entry()
        hboxEmail.pack_start(entryEmail, expand=True, fill=True)
        # password entry
        hboxPassword = gtk.HBox()
        passText = _("Password:")
        labelPassword = gtk.Label(passText)
        hboxPassword.pack_start(labelPassword, expand=False, fill=False, padding=5)
        entryPassword = gtk.Entry()
        entryPassword.set_visibility(False)
        hboxPassword.pack_start(entryPassword, expand=True, fill=True)
        # password confirm entry
        hboxPasswordConfirm = gtk.HBox()
        passConfirmText = _("Confirm:")
        labelPasswordConfirm = gtk.Label(passConfirmText)
        hboxPasswordConfirm.pack_start(labelPasswordConfirm, expand=False, fill=False, padding=11)
        entryPasswordConfirm = gtk.Entry()
        entryPasswordConfirm.set_visibility(False)
        hboxPasswordConfirm.pack_start(entryPasswordConfirm, expand=True, fill=True)

        keyDlg.vbox.pack_start(lblInfo, expand=False, fill=False)
        #keyDlg.vbox.pack_start(labelEmail)
        #keyDlg.vbox.pack_start(entryEmail)
        keyDlg.vbox.pack_start(hboxEmail)
        keyDlg.vbox.pack_start(hboxPassword)
        keyDlg.vbox.pack_start(hboxPasswordConfirm)
        #keyDlg.vbox.pack_start(labelPassword)
        #keyDlg.vbox.pack_start(entryPassword)
        #keyDlg.vbox.pack_start(entryPasswordConfirm)
        lblInfo.show()
        labelEmail.show()
        entryEmail.show()
        hboxEmail.show()
        labelPassword.show()
        entryPassword.show()
        labelPasswordConfirm.show()
        entryPasswordConfirm.show()
        hboxPassword.show()
        hboxPasswordConfirm.show()
        response = keyDlg.run()
        info = None
        if response == gtk.RESPONSE_OK :
            if entryPassword.get_text() == entryPasswordConfirm.get_text():
                info = (entryEmail.get_text(), entryPasswordConfirm.get_text())
            else:
                print _("Passwords do not match...")
        else:
            print _("GPG generation cancelled...")

        keyDlg.destroy()
        return info

    def on_buttonBack_clicked(self, widget):
        # HACK: back pressed so change buttonNext text
        self.wTree.get_widget("buttonNext").set_label("Next")
        # HACK: get_current_page() returns after the click, so check for 1 page ahead
        # check for first step; disable if needed
        if self.wTree.get_widget("notebookWizard").get_current_page() == 1:
            self.wTree.get_widget("buttonBack").hide()
        # check for disc type and move to proper locations
        if self.wTree.get_widget("notebookWizard").get_current_page() == self.pageAltSetup:
            self.setPage(self.pageDiscType)
        elif self.wTree.get_widget("notebookWizard").get_current_page() == self.pageFinish:
            # on finish page; move to proper disc type build
            if self.discType == "live":
                self.setPage(self.pageLiveBuild)
            elif self.discType == "alt":
                self.setPage(self.pageAltBuild)
        else:
            self.wTree.get_widget("notebookWizard").prev_page()

    def on_buttonNext_clicked(self, widget):
        page = self.wTree.get_widget("notebookWizard").get_current_page()
        # HACK: show back button
        self.wTree.get_widget("buttonBack").show()
        #if (self.checkPage(page)):
        #    self.wTree.get_widget("notebookWizard").next_page()
        self.checkPage(page)

    def on_buttonBrowseWorkingDir_clicked(self, widget):
        dlgTitle = _('Select Working Directory')
        workingDlg = gtk.FileChooserDialog(title=dlgTitle, parent=self.wTree.get_widget("windowMain"), action=gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER, buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK), backend=None)
        workingDlg.set_uri(os.environ['HOME'] + '/reconstructor')
        response = workingDlg.run()
        if response == gtk.RESPONSE_OK :
            filename = workingDlg.get_current_folder()
            self.wTree.get_widget("entryWorkingDir").set_text(workingDlg.get_filename())
            workingDlg.hide()
        elif response == gtk.RESPONSE_CANCEL :
            workingDlg.destroy()

    def on_buttonBrowseIsoFilename_clicked(self, widget):
        # filter only iso files
        isoFilter = gtk.FileFilter()
        isoFilter.set_name("ISO Files (.iso)")
        isoFilter.add_pattern("*.iso")
        # create dialog
        dlgTitle = _('Select Live CD ISO')
        isoDlg = gtk.FileChooserDialog(title=dlgTitle, parent=self.wTree.get_widget("windowMain"), action=gtk.FILE_CHOOSER_ACTION_OPEN, buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK), backend=None)
        isoDlg.add_filter(isoFilter)
        isoDlg.set_current_folder(os.environ['HOME'])
        response = isoDlg.run()
        if response == gtk.RESPONSE_OK :
            self.wTree.get_widget("entryIsoFilename").set_text(isoDlg.get_filename())
            isoDlg.hide()
        elif response == gtk.RESPONSE_CANCEL :
            isoDlg.destroy()

    def on_buttonBrowseLiveCdFilename_clicked(self, widget):
        # filter only iso files
        isoFilter = gtk.FileFilter()
        isoFilter.set_name("ISO Files")
        isoFilter.add_pattern("*.iso")
        # create dialog
        dlgTitle = _('Select Live CD Filename')
        isoDlg = gtk.FileChooserDialog(title=dlgTitle, parent=self.wTree.get_widget("windowMain"), action=gtk.FILE_CHOOSER_ACTION_SAVE, buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_SAVE, gtk.RESPONSE_OK), backend=None)
        isoDlg.add_filter(isoFilter)
        isoDlg.set_select_multiple(False)
        isoDlg.set_current_folder(os.environ['HOME'])
        response = isoDlg.run()
        if response == gtk.RESPONSE_OK :
            self.wTree.get_widget("entryLiveIsoFilename").set_text(isoDlg.get_filename())
            isoDlg.hide()
        elif response == gtk.RESPONSE_CANCEL :
            isoDlg.destroy()

    def on_buttonBrowseAltCdFilename_clicked(self, widget):
        # filter only iso files
        isoFilter = gtk.FileFilter()
        isoFilter.set_name("ISO Files")
        isoFilter.add_pattern("*.iso")
        # create dialog
        dlgTitle = _('Select Alternate CD Filename')
        isoDlg = gtk.FileChooserDialog(title=dlgTitle, parent=self.wTree.get_widget("windowMain"), action=gtk.FILE_CHOOSER_ACTION_SAVE, buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_SAVE, gtk.RESPONSE_OK), backend=None)
        isoDlg.add_filter(isoFilter)
        isoDlg.set_select_multiple(False)
        isoDlg.set_current_folder(os.environ['HOME'])
        response = isoDlg.run()
        if response == gtk.RESPONSE_OK :
            self.wTree.get_widget("entryAltBuildIsoFilename").set_text(isoDlg.get_filename())
            isoDlg.hide()
        elif response == gtk.RESPONSE_CANCEL :
            isoDlg.destroy()

    def on_checkbuttonBuildIso_toggled(self, widget):
        if self.wTree.get_widget("checkbuttonBuildIso").get_active() == True:
            # show filename, description, etc. entry
            self.wTree.get_widget("tableLiveCd").show()
        else:
            # hide filename entry
            self.wTree.get_widget("tableLiveCd").hide()

    def on_checkbuttonAltBuildIso_toggled(self, widget):
        if self.wTree.get_widget("checkbuttonAltBuildIso").get_active() == True:
            # show filename, description, etc. entry
            self.wTree.get_widget("tableAltCd").show()
        else:
            # hide filename entry
            self.wTree.get_widget("tableAltCd").hide()

    def on_buttonBrowseUsplashFilename_clicked(self, widget):
        # filter only so files
        soFilter = gtk.FileFilter()
        soFilter.set_name("Usplash Library Files (.so)")
        soFilter.add_pattern("*.so")
        # create dialog
        dlgTitle = _('Select Usplash')
        soDlg = gtk.FileChooserDialog(title=dlgTitle, parent=self.wTree.get_widget("windowMain"), action=gtk.FILE_CHOOSER_ACTION_OPEN, buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK), backend=None)
        soDlg.add_filter(soFilter)
        soDlg.set_select_multiple(False)
        response = soDlg.run()
        if response == gtk.RESPONSE_OK :
            self.wTree.get_widget("entryUsplashFilename").set_text(soDlg.get_filename())
            soDlg.hide()
        elif response == gtk.RESPONSE_CANCEL :
            soDlg.destroy()

    def on_buttonBrowseLiveCdSplashFilename_clicked(self, widget):
        # filter only pcx files
        pcxFilter = gtk.FileFilter()
        pcxFilter.set_name("PCX Images (.pcx)")
        pcxFilter.add_pattern("*.pcx")
        # create dialog
        dlgTitle = _('Select Live CD Splash Image')
        pxcDlg = gtk.FileChooserDialog(title=dlgTitle, parent=self.wTree.get_widget("windowMain"), action=gtk.FILE_CHOOSER_ACTION_OPEN, buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK), backend=None)
        pxcDlg.add_filter(pcxFilter)
        pxcDlg.set_select_multiple(False)
        response = pxcDlg.run()
        if response == gtk.RESPONSE_OK:
            self.wTree.get_widget("entryLiveCdSplashImage").set_text(pxcDlg.get_filename())
            pxcDlg.hide()
        elif response == gtk.RESPONSE_CANCEL:
            pxcDlg.destroy()


    def on_buttonBrowseGnomeDesktopWallpaper_clicked(self, widget):
        # filter only image files
        imgFilter = gtk.FileFilter()
        imgFilter.set_name("Images (.jpg, .png, .bmp)")
        imgFilter.add_pattern("*jpeg")
        imgFilter.add_pattern("*.jpg")
        imgFilter.add_pattern("*.png")
        imgFilter.add_pattern("*.bmp")
        # create dialog
        dlgTitle = _('Select Wallpaper')
        imgDlg = gtk.FileChooserDialog(title=dlgTitle, parent=self.wTree.get_widget("windowMain"), action=gtk.FILE_CHOOSER_ACTION_OPEN, buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK), backend=None)
        imgDlg.add_filter(imgFilter)
        imgDlg.set_select_multiple(False)
        response = imgDlg.run()
        if response == gtk.RESPONSE_OK :
            self.wTree.get_widget("entryGnomeDesktopWallpaperFilename").set_text(imgDlg.get_filename())
            imgDlg.hide()
        elif response == gtk.RESPONSE_CANCEL :
            imgDlg.destroy()

    def on_buttonBrowseGnomeSplashScreen_clicked(self, widget):
        # filter only image files
        imgFilter = gtk.FileFilter()
        imgFilter.set_name("Images (.jpg, .png, .bmp)")
        imgFilter.add_pattern("*jpeg")
        imgFilter.add_pattern("*.jpg")
        imgFilter.add_pattern("*.png")
        imgFilter.add_pattern("*.bmp")
        # create dialog
        dlgTitle = _('Select Splash Screen')
        imgDlg = gtk.FileChooserDialog(title=dlgTitle, parent=self.wTree.get_widget("windowMain"), action=gtk.FILE_CHOOSER_ACTION_OPEN, buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK), backend=None)
        imgDlg.add_filter(imgFilter)
        imgDlg.set_select_multiple(False)
        response = imgDlg.run()
        if response == gtk.RESPONSE_OK :
            self.wTree.get_widget("entryGnomeSplashScreenFilename").set_text(imgDlg.get_filename())
            imgDlg.hide()
        elif response == gtk.RESPONSE_CANCEL :
            imgDlg.destroy()

    def on_buttonBrowseGnomeFont_clicked(self, widget):
        # font selection dialog
        fontDialog = gtk.FontSelectionDialog(title="Select Font")
        response = fontDialog.run()
        if response == gtk.RESPONSE_OK :
            self.wTree.get_widget("labelGnomeDesktopApplicationFontValue").set_text(fontDialog.get_font_name())
            fontDialog.destroy()
        else:
            fontDialog.destroy()

    def on_buttonBrowseGnomeDocumentFont_clicked(self, widget):
        # font selection dialog
        dlgTitle = _('Select Font')
        fontDialog = gtk.FontSelectionDialog(title=dlgTitle)
        response = fontDialog.run()
        if response == gtk.RESPONSE_OK :
            self.wTree.get_widget("labelGnomeDesktopDocumentFontValue").set_text(fontDialog.get_font_name())
            fontDialog.destroy()
        else:
            fontDialog.destroy()

    def on_buttonBrowseGnomeDesktopFont_clicked(self, widget):
        # font selection dialog
        dlgTitle = _('Select Font')
        fontDialog = gtk.FontSelectionDialog(title=dlgTitle)
        response = fontDialog.run()
        if response == gtk.RESPONSE_OK :
            self.wTree.get_widget("labelGnomeDesktopFontValue").set_text(fontDialog.get_font_name())
            fontDialog.destroy()
        else:
            fontDialog.destroy()

    def on_buttonBrowseGnomeDesktopTitleBarFont_clicked(self, widget):
        # font selection dialog
        dlgTitle = _('Select Font')
        fontDialog = gtk.FontSelectionDialog(title=dlgTitle)
        response = fontDialog.run()
        if response == gtk.RESPONSE_OK :
            self.wTree.get_widget("labelGnomeDesktopTitleBarFontValue").set_text(fontDialog.get_font_name())
            fontDialog.destroy()
        else:
            fontDialog.destroy()

    def on_buttonBrowseGnomeFixedFont_clicked(self, widget):
        # font selection dialog
        dlgTitle = _('Select Font')
        fontDialog = gtk.FontSelectionDialog(title=dlgTitle)
        response = fontDialog.run()
        if response == gtk.RESPONSE_OK :
            self.wTree.get_widget("labelGnomeDesktopFixedFontValue").set_text(fontDialog.get_font_name())
            fontDialog.destroy()
        else:
            fontDialog.destroy()

    def on_buttonImportGnomeTheme_clicked(self, widget):
        print _("Importing Theme...")
        # filter only tar.gz files
        dlgFilter = gtk.FileFilter()
        dlgFilter.set_name("Archives (.tar.gz, .tar.bz2)")
        dlgFilter.add_pattern("*tar.gz")
        dlgFilter.add_pattern("*tar.bz2")
        # create dialog
        dlgTitle = _('Select Theme Package')
        dlg = gtk.FileChooserDialog(title=dlgTitle, parent=self.wTree.get_widget("windowMain"), action=gtk.FILE_CHOOSER_ACTION_OPEN, buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK), backend=None)
        dlg.add_filter(dlgFilter)
        dlg.set_select_multiple(False)
        response = dlg.run()
        if response == gtk.RESPONSE_OK :
            # extract theme into root
            # check for bzip or gzip
            fname, ext = os.path.splitext(dlg.get_filename())
            if ext == ".gz":
                # gzip
                os.popen('tar zxf \"' + dlg.get_filename() + '\" -C \"' + os.path.join(self.customDir, "root/usr/share/themes/") + '\"')
            elif ext == ".bz2":
                # bzip
                os.popen('tar jxf \"' + dlg.get_filename() + '\" -C \"' + os.path.join(self.customDir, "root/usr/share/themes/") + '\"')

            # reload gnome themes
            self.loadGnomeThemes()
            dlg.hide()
        elif response == gtk.RESPONSE_CANCEL :
            print _("Import Cancelled...")
            dlg.destroy()

    def on_buttonImportGnomeThemeIcons_clicked(self, widget):
        print _("Importing Icons...")
        # filter only tar.gz files
        dlgFilter = gtk.FileFilter()
        dlgFilter.set_name("Archives (.tar.gz, .tar.bz2)")
        dlgFilter.add_pattern("*tar.gz")
        dlgFilter.add_pattern("*tar.bz2")
        # create dialog
        dlgTitle = _('Select Icon Package')
        dlg = gtk.FileChooserDialog(title=dlgTitle, parent=self.wTree.get_widget("windowMain"), action=gtk.FILE_CHOOSER_ACTION_OPEN, buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK), backend=None)
        dlg.add_filter(dlgFilter)
        dlg.set_select_multiple(False)
        response = dlg.run()
        if response == gtk.RESPONSE_OK :
            # extract theme into root
            # check for bzip or gzip
            fname, ext = os.path.splitext(dlg.get_filename())
            if ext == ".gz":
                # gzip
                os.popen('tar zxf \"' + dlg.get_filename() + '\" -C \"' + os.path.join(self.customDir, "root/usr/share/icons/") + '\"')
            elif ext == ".bz2":
                # bzip
                os.popen('tar jxf \"' + dlg.get_filename() + '\" -C \"' + os.path.join(self.customDir, "root/usr/share/icons/") + '\"')

            # reload gnome themes
            self.loadGnomeThemes()
            dlg.hide()
        elif response == gtk.RESPONSE_CANCEL :
            print _("Import Cancelled...")
            dlg.destroy()

    def on_buttonImportGdmTheme_clicked(self, widget):
        print _("Importing GDM Theme...")
        # filter only tar.gz files
        dlgFilter = gtk.FileFilter()
        dlgFilter.set_name("Archives (.tar.gz, .tar.bz2)")
        dlgFilter.add_pattern("*tar.gz")
        dlgFilter.add_pattern("*tar.bz2")
        # create dialog
        dlgTitle = _('Select GDM Theme Package')
        dlg = gtk.FileChooserDialog(title=dlgTitle, parent=self.wTree.get_widget("windowMain"), action=gtk.FILE_CHOOSER_ACTION_OPEN, buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK), backend=None)
        dlg.add_filter(dlgFilter)
        dlg.set_select_multiple(False)
        response = dlg.run()
        if response == gtk.RESPONSE_OK :
            # extract theme into root
            # check for bzip or gzip
            fname, ext = os.path.splitext(dlg.get_filename())
            if ext == ".gz":
                # gzip
                os.popen('tar zxf \"' + dlg.get_filename() + '\" -C \"' + os.path.join(self.customDir, "root/usr/share/gdm/themes/") + '\"')
            elif ext == ".bz2":
                # bzip
                os.popen('tar jxf \"' + dlg.get_filename() + '\" -C \"' + os.path.join(self.customDir, "root/usr/share/gdm/themes/") + '\"')
            # reload gnome themes
            self.loadGdmThemes()
            dlg.hide()
        elif response == gtk.RESPONSE_CANCEL :
            print _("Import Cancelled...")
            dlg.destroy()

    def on_buttonSoftwareApply_clicked(self, widget):
        # customize distro
        warnDlg = gtk.Dialog(title=self.appName, parent=None, flags=0, buttons=(gtk.STOCK_NO, gtk.RESPONSE_CANCEL, gtk.STOCK_OK, gtk.RESPONSE_OK))
        warnDlg.set_icon_from_file(self.iconFile)
        warnDlg.vbox.set_spacing(10)
        labelSpc = gtk.Label(" ")
        warnDlg.vbox.pack_start(labelSpc)
        labelSpc.show()
        lblContinueText = _("  <b>Continue?</b>  ")
        lblContinueInfo = _("     This may take a few minutes.  Please wait...     ")
        label = gtk.Label(lblContinueText)
        lblInfo = gtk.Label(lblContinueInfo)
        label.set_use_markup(True)
        warnDlg.vbox.pack_start(label)
        warnDlg.vbox.pack_start(lblInfo)
        lblInfo.show()
        label.show()
        #warnDlg.show()
        response = warnDlg.run()
        if response == gtk.RESPONSE_OK:
            warnDlg.destroy()
            self.setBusyCursor()
            gobject.idle_add(self.customize)
            gobject.idle_add(self.calculateIsoSize)
        else:
            warnDlg.destroy()

    def on_buttonSoftwareCalculateIsoSize_clicked(self, widget):
        self.setBusyCursor()
        gobject.idle_add(self.calculateIsoSize)

    def on_buttonAltIsoCalculate_clicked(self, widget):
        self.setBusyCursor()
        gobject.idle_add(self.calculateAltIsoSize)

    def on_buttonInteractiveEditLaunch_clicked(self, widget):
        self.startInteractiveEdit()

    def on_buttonInteractiveClear_clicked(self, widget):
        warnDlg = gtk.Dialog(title=self.appName, parent=None, flags=0, buttons=(gtk.STOCK_NO, gtk.RESPONSE_CANCEL, gtk.STOCK_OK, gtk.RESPONSE_OK))
        warnDlg.set_icon_from_file(self.iconFile)
        warnDlg.vbox.set_spacing(10)
        labelSpc = gtk.Label(" ")
        warnDlg.vbox.pack_start(labelSpc)
        labelSpc.show()
        lblContinueText = _("  <b>Delete?</b>  ")
        label = gtk.Label(lblContinueText)
        label.set_use_markup(True)
        warnDlg.vbox.pack_start(label)
        label.show()
        #warnDlg.show()
        response = warnDlg.run()
        if response == gtk.RESPONSE_OK:
            warnDlg.destroy()
            self.setBusyCursor()
            # clear settings
            gobject.idle_add(self.clearInteractiveSettings)
        else:
            warnDlg.destroy()

    def on_buttonUsplashGenerate_clicked(self,widget):
        pngFile = None
        outputFile = None
        # filter only tar.gz files
        dlgFilter = gtk.FileFilter()
        dlgFilter.set_name("PNG Images (.png)")
        dlgFilter.add_pattern("*.png")
        # create dialog
        dlgTitle = _('Select PNG Image')
        dlg = gtk.FileChooserDialog(title=dlgTitle, parent=self.wTree.get_widget("windowMain"), action=gtk.FILE_CHOOSER_ACTION_OPEN, buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK), backend=None)
        dlg.add_filter(dlgFilter)
        dlg.set_select_multiple(False)
        dlg.set_current_folder(os.environ['HOME'])
        response = dlg.run()
        if response == gtk.RESPONSE_OK :
            # set var
            pngFile = dlg.get_filename()
            dlg.destroy()
        elif response == gtk.RESPONSE_CANCEL :
            dlg.destroy()

        # if pngFile is selected, launch dialog for output file
        if pngFile != None:
            # filter only iso files
            soFilter = gtk.FileFilter()
            soFilter.set_name("Usplash Library Files")
            soFilter.add_pattern("*.so")
            # create dialog
            dlgTitle = _('Save Usplash As...')
            soDlg = gtk.FileChooserDialog(title=dlgTitle, parent=self.wTree.get_widget("windowMain"), action=gtk.FILE_CHOOSER_ACTION_SAVE, buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_SAVE, gtk.RESPONSE_OK), backend=None)
            soDlg.add_filter(soFilter)
            soDlg.set_select_multiple(False)
            soDlg.set_current_folder(os.environ['HOME'])
            response = soDlg.run()
            if response == gtk.RESPONSE_OK :
                outputFile = soDlg.get_filename()
                soDlg.destroy()
            elif response == gtk.RESPONSE_CANCEL :
                soDlg.destroy()

        if pngFile != None and outputFile != None:
            # generate .so
            self.generateUsplash(pngFile, outputFile)
            # check for file and assign .so splash image field
            if os.path.exists(outputFile):
                self.wTree.get_widget("entryUsplashFilename").set_text(outputFile)

    def on_buttonOptimizeShutdownRestore_clicked(self, widget):
        self.setBusyCursor()
        gobject.idle_add(self.restoreShutdown)

    def on_checkbuttonOptimizationStartupEnable_toggled(self, widget):
        if self.wTree.get_widget("checkbuttonOptimizationStartupEnable").get_active() == True:
            self.wTree.get_widget("labelOptimizationStartupInfo").show()
            self.wTree.get_widget("tableOptimizationStartup").show()
        else:
            self.wTree.get_widget("labelOptimizationStartupInfo").hide()
            self.wTree.get_widget("tableOptimizationStartup").hide()

    def on_buttonCustomizeLaunchTerminal_clicked(self, widget):
        self.launchTerminal()

    def on_buttonBurnIso_clicked(self, widget):
        # check for disc type
        if self.discType == 'live':
            self.burnIso()
        elif self.discType == 'alt':
            self.burnAltIso()
        else:
            print _("Error: Cannot burn iso... Unknown disc type...")

    def on_buttonCheckUpdates_clicked(self, widget):
        self.setBusyCursor()
        gobject.idle_add(self.checkForUpdates)

    def on_buttonModulesAddModule_clicked(self, widget):
        # filter only tar.gz files
        dlgFilter = gtk.FileFilter()
        dlgFilter.set_name("Modules (.rmod)")
        dlgFilter.add_pattern("*.rmod")
        # create dialog
        dlgTitle = _('Select Reconstructor Module')
        dlg = gtk.FileChooserDialog(title=dlgTitle, parent=self.wTree.get_widget("windowMain"), action=gtk.FILE_CHOOSER_ACTION_OPEN, buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK), backend=None)
        dlg.add_filter(dlgFilter)
        dlg.set_select_multiple(False)
        response = dlg.run()
        if response == gtk.RESPONSE_OK :
            self.addModule(dlg.get_filename())
            dlg.destroy()
        elif response == gtk.RESPONSE_CANCEL :
            print _("Module installation cancelled...")
            dlg.destroy()

    def on_buttonModulesViewModule_clicked(self, widget, treeview):
        self.showModuleSource(treeview)

    def on_buttonModulesUpdateModule_clicked(self, widget, treeview):
        selection = treeview.get_selection()
        model, iter = selection.get_selected()
        modName = ''
        modVersion = ''
        modPath = None
        modUpdateUrl = ''
        if iter:
            path = model.get_path(iter)
            modName = model.get_value(iter, self.moduleColumnName)
            modVersion = model.get_value(iter, self.moduleColumnVersion)
            modPath = model.get_value(iter, self.moduleColumnPath)
            modUpdateUrl = model.get_value(iter, self.moduleColumnUpdateUrl)
        # check for valid module and update
        if modPath != None:
            self.setBusyCursor()
            gobject.idle_add(self.updateModule, modName, modVersion, modPath, modUpdateUrl, treeview)

    def on_buttonModulesClearRunOnBoot_clicked(self, widget):
        warnDlg = gtk.Dialog(title=self.appName, parent=None, flags=0, buttons=(gtk.STOCK_NO, gtk.RESPONSE_CANCEL, gtk.STOCK_YES, gtk.RESPONSE_OK))
        warnDlg.set_icon_from_file(self.iconFile)
        warnDlg.vbox.set_spacing(10)
        labelSpc = gtk.Label(" ")
        warnDlg.vbox.pack_start(labelSpc)
        labelSpc.show()
        lblContinueText = _("  <b>Clear all run on boot modules?</b>  ")
        label = gtk.Label(lblContinueText)
        label.set_use_markup(True)
        warnDlg.vbox.pack_start(label)
        label.show()
        #warnDlg.show()
        response = warnDlg.run()
        if response == gtk.RESPONSE_OK:
            warnDlg.destroy()
            # clear run on boot modules
            self.clearRunOnBootModules()
        else:
            warnDlg.destroy()

    def on_buttonBrowseAltWorkingDir_clicked(self, widget):
        dlgTitle = _('Select Working Directory')
        workingDlg = gtk.FileChooserDialog(title=dlgTitle, parent=self.wTree.get_widget("windowMain"), action=gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER, buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK), backend=None)
        workingDlg.set_uri(os.environ['HOME'] + '/reconstructor')
        response = workingDlg.run()
        if response == gtk.RESPONSE_OK :
            filename = workingDlg.get_current_folder()
            self.wTree.get_widget("entryAltWorkingDir").set_text(workingDlg.get_filename())
            workingDlg.hide()
        elif response == gtk.RESPONSE_CANCEL :
            workingDlg.destroy()

    def on_buttonBrowseAltIsoFilename_clicked(self, widget):
        # filter only iso files
        isoFilter = gtk.FileFilter()
        isoFilter.set_name("ISO Files (.iso)")
        isoFilter.add_pattern("*.iso")
        # create dialog
        dlgTitle = _('Select Alternate CD ISO')
        isoDlg = gtk.FileChooserDialog(title=dlgTitle, parent=self.wTree.get_widget("windowMain"), action=gtk.FILE_CHOOSER_ACTION_OPEN, buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK), backend=None)
        isoDlg.add_filter(isoFilter)
        isoDlg.set_current_folder(os.environ['HOME'])
        response = isoDlg.run()
        if response == gtk.RESPONSE_OK :
            self.wTree.get_widget("entryAltIsoFilename").set_text(isoDlg.get_filename())
            isoDlg.hide()
        elif response == gtk.RESPONSE_CANCEL :
            isoDlg.destroy()

    def on_checkbuttonAltCreateRemasterDir_clicked(self, widget):
        if self.wTree.get_widget("checkbuttonAltCreateRemasterDir").get_active() == True:
            self.wTree.get_widget("hboxAltBase").set_sensitive(True)
        else:
            self.wTree.get_widget("hboxAltBase").set_sensitive(False)
    def on_buttonAptRepoImportGpgKey_clicked(self, widget):
        # filter only iso files
        gpgFilter = gtk.FileFilter()
        gpgFilter.set_name("GPG Key Files (.gpg, .key)")
        gpgFilter.add_pattern("*.gpg")
        # create dialog
        dlgTitle = _('Select GPG Key File')
        gpgDlg = gtk.FileChooserDialog(title=dlgTitle, parent=self.wTree.get_widget("windowMain"), action=gtk.FILE_CHOOSER_ACTION_OPEN, buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK), backend=None)
        gpgDlg.add_filter(gpgFilter)
        gpgDlg.set_current_folder(os.environ['HOME'])
        response = gpgDlg.run()
        if response == gtk.RESPONSE_OK :
            print _('Importing GPG Key...')
            try:
                os.popen('cp -Rf \"' + gpgDlg.get_filename() + '\" \"' + os.path.join(self.customDir, "root") + '/tmp/apt_key.gpg\"')
                os.popen('chroot \"' + os.path.join(self.customDir, "root/") + '\"' + ' apt-key add /tmp/apt_key.gpg')
                os.popen('rm -Rf \"' + os.path.join(self.customDir, "root") + '/tmp/apt_key.gpg\"')
                print _('GPG Key successfully imported...')
            except Exception, detail:
                errImport = _('Error importing GPG key: ')
                print errImport, detail
                pass
            gpgDlg.hide()
        elif response == gtk.RESPONSE_CANCEL :
            gpgDlg.destroy()

    def on_buttonAltPackagesImportGpgKey_clicked(self, widget):
        # filter only iso files
        gpgFilter = gtk.FileFilter()
        gpgFilter.set_name("GPG Key Files (.gpg, .key)")
        gpgFilter.add_pattern("*.gpg")
        # create dialog
        dlgTitle = _('Select GPG Key File')
        gpgDlg = gtk.FileChooserDialog(title=dlgTitle, parent=self.wTree.get_widget("windowMain"), action=gtk.FILE_CHOOSER_ACTION_OPEN, buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK), backend=None)
        gpgDlg.add_filter(gpgFilter)
        gpgDlg.set_current_folder(os.environ['HOME'])
        response = gpgDlg.run()
        if response == gtk.RESPONSE_OK :
            print _('Importing GPG Key...')
            try:
                os.popen('apt-key add \"' + gpgDlg.get_filename() + '\"')
                print _('GPG Key successfully imported...')
            except Exception, detail:
                errImport = _('Error importing GPG key: ')
                print errImport, detail
                pass
            gpgDlg.hide()
        elif response == gtk.RESPONSE_CANCEL :
            gpgDlg.destroy()

    def on_buttonAltPackagesApply_clicked(self, widget):
        # customize alternate
        warnDlg = gtk.Dialog(title=self.appName, parent=None, flags=0, buttons=(gtk.STOCK_NO, gtk.RESPONSE_CANCEL, gtk.STOCK_OK, gtk.RESPONSE_OK))
        warnDlg.set_icon_from_file(self.iconFile)
        warnDlg.vbox.set_spacing(10)
        labelSpc = gtk.Label(" ")
        warnDlg.vbox.pack_start(labelSpc)
        labelSpc.show()
        lblContinueText = _("  <b>Continue?</b>  ")
        lblContinueInfo = _("     This may take a few minutes.  Please wait...     ")
        label = gtk.Label(lblContinueText)
        lblInfo = gtk.Label(lblContinueInfo)
        label.set_use_markup(True)
        warnDlg.vbox.pack_start(label)
        warnDlg.vbox.pack_start(lblInfo)
        lblInfo.show()
        label.show()
        #warnDlg.show()
        response = warnDlg.run()
        if response == gtk.RESPONSE_OK:
            warnDlg.destroy()
            self.setBusyCursor()
            gobject.idle_add(self.customizeAlt)
        else:
            warnDlg.destroy()


    def on_buttonDonate_clicked(self, widget):
        # go to web to donate
        if commands.getoutput('which firefox') != '':
            user = os.getlogin()
            os.popen('su ' + user + ' firefox \"' + self.donateUrl + '\"')
        else:
            print _("Cannot find system web browser.  Please copy and paste the following link in your browser.")
            print self.donateUrl
            print ""

    def saveSetupInfo(self):
        # do setup - check and create dirs as needed
        print _("INFO: Saving working directory information...")
        self.customDir = self.wTree.get_widget("entryWorkingDir").get_text()
        self.createRemasterDir = self.wTree.get_widget("checkbuttonCreateRemaster").get_active()
        self.createCustomRoot = self.wTree.get_widget("checkbuttonCreateRoot").get_active()
        self.createInitrdRoot = self.wTree.get_widget("checkbuttonCreateInitRd").get_active()
        self.isoFilename = self.wTree.get_widget("entryIsoFilename").get_text()
        # debug
        print "Custom Directory: " + str(self.customDir)
        print "Create Remaster Directory: " + str(self.createRemasterDir)
        print "Create Custom Root: " + str(self.createCustomRoot)
        print "Create Initrd Root: " + str(self.createInitrdRoot)
        print "ISO Filename: " + str(self.isoFilename)

    def saveAltSetupInfo(self):
        # do setup - check and create dirs as needed
        print _("INFO: Saving working directory information...")
        self.customDir = self.wTree.get_widget("entryAltWorkingDir").get_text()
        self.createAltRemasterDir = self.wTree.get_widget("checkbuttonAltCreateRemasterDir").get_active()
        self.createAltInitrdRoot = self.wTree.get_widget("checkbuttonAltCreateInitrdDir").get_active()
        self.isoFilename = self.wTree.get_widget("entryAltIsoFilename").get_text()
        # debug
        print "Custom Directory: " + str(self.customDir)
        print "Create Remaster Directory: " + str(self.createAltRemasterDir)
        print "Create Initrd Root: " + str(self.createAltInitrdRoot)
        print "ISO Filename: " + str(self.isoFilename)


# ---------- Setup ---------- #
    def setupWorkingDirectory(self):
        print _("INFO: Setting up working directory...")
        # remaster dir
        if self.createRemasterDir == True:
            # check for existing directories and remove if necessary
            #if os.path.exists(os.path.join(self.customDir, "remaster")):
            #    print _("INFO: Removing existing Remaster directory...")
            #    os.popen('rm -Rf \"' + os.path.join(self.customDir, "remaster/") + '\"')
            if os.path.exists(os.path.join(self.customDir, "remaster")) == False:
                print "INFO: Creating Remaster directory..."
                os.makedirs(os.path.join(self.customDir, "remaster"))
            # check for iso
            if self.isoFilename == "":
                mntDlg = gtk.Dialog(title=self.appName, parent=None, flags=0, buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OK, gtk.RESPONSE_OK))
                mntDlg.set_icon_from_file(self.iconFile)
                mntDlg.vbox.set_spacing(10)
                labelSpc = gtk.Label(" ")
                mntDlg.vbox.pack_start(labelSpc)
                labelSpc.show()
                lblText = _("  <b>Please insert Ubuntu Live CD and click OK</b>  ")
                label = gtk.Label(lblText)
                label.set_use_markup(True)
                mntDlg.vbox.pack_start(label)
                label.show()
                #warnDlg.show()
                response = mntDlg.run()
                if response == gtk.RESPONSE_OK:
                    print _("Using Live CD for remastering...")
                    mntDlg.destroy()
                    os.popen("mount " + self.mountDir)
                else:
                    mntDlg.destroy()
                    self.setDefaultCursor()
                    return
            else:
                print _("Using ISO for remastering...")
                os.popen('mount -o loop \"' + self.isoFilename + '\" ' + self.mountDir)

            print _("Copying files...")

            # copy remaster files
            os.popen('rsync -at --del ' + self.mountDir + '/ \"' + os.path.join(self.customDir, "remaster") + '\"')
            print _("Finished copying files...")

            # unmount iso/cd-rom
            os.popen("umount " + self.mountDir)
        # custom root dir
        if self.createCustomRoot == True:
            #if os.path.exists(os.path.join(self.customDir, "root")):
            #    print _("INFO: Removing existing Custom Root directory...")

            #    os.popen('rm -Rf \"' + os.path.join(self.customDir, "root/") + '\"')
            if os.path.exists(os.path.join(self.customDir, "root")) == False:
                print _("INFO: Creating Custom Root directory...")
                os.makedirs(os.path.join(self.customDir, "root"))
            # check for existing directories and remove if necessary
            if os.path.exists(os.path.join(self.customDir, "tmpsquash")):
                print _("INFO: Removing existing tmpsquash directory...")

                os.popen('rm -Rf \"' + os.path.join(self.customDir, "tmpsquash") + '\"')

            # extract squashfs into custom root
            # check for iso
            if self.isoFilename == "":
                mntDlg = gtk.Dialog(title=self.appName, parent=None, flags=0, buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OK, gtk.RESPONSE_OK))
                mntDlg.set_icon_from_file(self.iconFile)
                mntDlg.vbox.set_spacing(10)
                labelSpc = gtk.Label(" ")
                mntDlg.vbox.pack_start(labelSpc)
                labelSpc.show()
                lblText = _("  <b>Please insert Ubuntu Live CD and click OK</b>  ")
                label = gtk.Label(lblText)
                label.set_use_markup(True)
                mntDlg.vbox.pack_start(label)
                label.show()
                response = mntDlg.run()
                if response == gtk.RESPONSE_OK:
                    print _("Using Live CD for squashfs root...")
                    mntDlg.destroy()
                    os.popen("mount " + self.mountDir)
                else:
                    mntDlg.destroy()
                    self.setDefaultCursor()
                    return
            else:
                print _("Using ISO for squashfs root...")
                os.popen('mount -o loop \"' + self.isoFilename + '\" ' + self.mountDir)

            # copy remaster files
            os.mkdir(os.path.join(self.customDir, "tmpsquash"))
            # mount squashfs root
            print _("Mounting squashfs...")
            os.popen('mount -t squashfs -o loop ' + self.mountDir + '/casper/filesystem.squashfs \"' + os.path.join(self.customDir, "tmpsquash") + '\"')
            print _("Extracting squashfs root...")

            # copy squashfs root
            os.popen('rsync -at --del \"' + os.path.join(self.customDir, "tmpsquash") + '\"/ \"' + os.path.join(self.customDir, "root/") + '\"')

            # umount tmpsquashfs
            print _("Unmounting tmpsquash...")
            os.popen('umount --force \"' + os.path.join(self.customDir, "tmpsquash") + '\"')
            # umount cdrom
            print _("Unmounting cdrom...")
            os.popen("umount --force " + self.mountDir)
            # remove tmpsquash
            print _("Removing tmpsquash...")
            os.popen('rm -Rf \"' + os.path.join(self.customDir, "tmpsquash") + '\"')
            # set proper permissions - MUST DO WITH UBUNTU
            print _("Setting proper permissions...")
            os.popen('chmod 6755 \"' + os.path.join(self.customDir, "root/usr/bin/sudo") + '\"')
            os.popen('chmod 0440 \"' + os.path.join(self.customDir, "root/etc/sudoers") + '\"')
            print _("Finished extracting squashfs root...")
        # initrd dir
        if self.createInitrdRoot == True:
            if os.path.exists(os.path.join(self.customDir, "initrd")):
                print _("INFO: Removing existing Initrd directory...")
                os.popen('rm -Rf \"' + os.path.join(self.customDir, "initrd/") + '\"')
            print _("INFO: Creating Initrd directory...")
            os.makedirs(os.path.join(self.customDir, "initrd"))
            # check for iso
            if self.isoFilename == "":
                mntDlg = gtk.Dialog(title=self.appName, parent=None, flags=0, buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OK, gtk.RESPONSE_OK))
                mntDlg.set_icon_from_file(self.iconFile)
                mntDlg.vbox.set_spacing(10)
                labelSpc = gtk.Label(" ")
                mntDlg.vbox.pack_start(labelSpc)
                labelSpc.show()
                lblText = _("  <b>Please insert Ubuntu Live CD and click OK</b>  ")
                label = gtk.Label(lblText)
                label.set_use_markup(True)
                mntDlg.vbox.pack_start(label)
                label.show()
                response = mntDlg.run()
                if response == gtk.RESPONSE_OK:
                    print _("Using Live CD for initrd...")
                    mntDlg.destroy()
                    os.popen("mount " + self.mountDir)
                else:
                    mntDlg.destroy()
                    self.setDefaultCursor()
                    return
            else:
                print _("Using ISO for initrd...")
                os.popen('mount -o loop \"' + self.isoFilename + '\" ' + self.mountDir)

            # extract initrd
            print _("Extracting Initial Ram Disk (initrd)...")
            os.popen('cd \"' + os.path.join(self.customDir, "initrd/") + '\"; cat ' + self.mountDir + '/casper/initrd.gz | gzip -d | cpio -i')

            # umount cdrom
            os.popen("umount " + self.mountDir)

        # get ubuntu version
        self.loadCdVersion()
        # get current boot options menu text color
        self.loadBootMenuColor()
        # get current gdm background color
        self.loadGdmBackgroundColor()
        # load comboboxes for customization
        self.loadGdmThemes()
        self.loadGnomeThemes()
        #self.hideWorking()
        self.setDefaultCursor()
        self.setPage(self.pageLiveCustomize)
        print _("Finished setting up working directory...")
        print " "
        return False

    def setupAltWorkingDirectory(self):
        print _("INFO: Setting up alternate working directory...")
        # remaster dir
        if self.createAltRemasterDir == True:
            # check for existing directories and remove if necessary
            #if os.path.exists(os.path.join(self.customDir, self.altRemasterDir)):
            #    print _("INFO: Removing existing Alternate Remaster directory...")
            #    os.popen('rm -Rf \"' + os.path.join(self.customDir, self.altRemasterDir) + '\"')
            #    os.makedirs(os.path.join(self.customDir, self.altRemasterDir))
            if os.path.exists(os.path.join(self.customDir, self.altRemasterDir)) == False:
                # create remaster dir
                os.makedirs(os.path.join(self.customDir, self.altRemasterDir))

            # only create if doesn't exists -- keep existing and use rsync for speed
            # check for tmp package dir
            #if os.path.exists(os.path.join(self.customDir, self.tmpPackageDir)) == False:
                # create tmp package dir
            #    os.makedirs(os.path.join(self.customDir, self.tmpPackageDir))

            # create tmp dir
            if os.path.exists(os.path.join(self.customDir, self.tmpDir)) == False:
                # create tmp dir
                os.makedirs(os.path.join(self.customDir, self.tmpDir))
            else:
                # clean tmp dir
                print _("Cleaning alternate temporary directory...")
                os.popen('cd \"' + os.path.join(self.customDir, self.tmpDir) + '\" ; rm -Rf ./*')
            # create archives/partial dir
            #if os.path.exists(os.path.join(os.path.join(self.customDir, self.tmpPackageDir), "archives/partial")) == False:
            #    os.makedirs(os.path.join(os.path.join(self.customDir, self.tmpPackageDir), "archives/partial"))
            # create alt remaster repo
            if os.path.exists(os.path.join(self.customDir, self.altRemasterRepo)) == False:
                # create alternate remaster repo
                os.makedirs(os.path.join(self.customDir, self.altRemasterRepo))
            #print "INFO: Creating Remaster directory..."
            # check for iso
            if self.isoFilename == "":
                mntDlg = gtk.Dialog(title=self.appName, parent=None, flags=0, buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OK, gtk.RESPONSE_OK))
                mntDlg.set_icon_from_file(self.iconFile)
                mntDlg.vbox.set_spacing(10)
                labelSpc = gtk.Label(" ")
                mntDlg.vbox.pack_start(labelSpc)
                labelSpc.show()
                lblText = _("  <b>Please insert Ubuntu Alternate CD and click OK</b>  ")
                label = gtk.Label(lblText)
                label.set_use_markup(True)
                mntDlg.vbox.pack_start(label)
                label.show()
                #warnDlg.show()
                response = mntDlg.run()
                if response == gtk.RESPONSE_OK:
                    print _("Using Alternate CD for remastering...")
                    mntDlg.destroy()
                    os.popen("mount " + self.mountDir)
                else:
                    mntDlg.destroy()
                    self.setDefaultCursor()
                    return False
            else:
                print _("Using ISO for remastering...")
                os.popen('mount -o loop \"' + self.isoFilename + '\" ' + self.mountDir)

            # copy remaster files
            print _("Copying alternate remaster directory...")
            #os.popen('rsync -at --del --exclude=\"pool/main/**/*.deb\" --exclude=\"pool/restricted/**/*.deb\" ' + self.mountDir + '/ \"' + os.path.join(self.customDir, self.altRemasterDir) + '\"')
            os.popen('rsync -at --del ' + self.mountDir + '/ \"' + os.path.join(self.customDir, self.altRemasterDir) + '\"')

            # ----- Removed due to poor ubuntu dependency packaging -----
            # copy alternate base
            #baseType = self.wTree.get_widget("comboboxAltBase").get_active()
            #print _("Copying files...")
            #typeTxt = _("Using Alternate Base:")
            ## HACK: use rsync to find packages and copy
            #if baseType == self.altBaseTypeStandard:
            #    print typeTxt,"Standard"
            #    pHelper.copyPackages(pHelper.ubuntuMinimalPackages, self.mountDir + '/', os.path.join(self.customDir, self.altRemasterDir))
            #elif baseType == self.altBaseTypeServer:
            #    print typeTxt, " Server"
            #    pHelper.copyPackages(pHelper.ubuntuServerPackages, self.mountDir + '/', os.path.join(self.customDir, self.altRemasterDir))
            #elif baseType == self.altBaseTypeDesktop:
            #    print typeTxt, " Desktop"
            #    pHelper.copyPackages(pHelper.ubuntuDesktopPackages, self.mountDir + '/', os.path.join(self.customDir, self.altRemasterDir))
            #else:
            #    print _("ERROR: Unknown Alternate Base Type...")

            print _("Finished copying files...")

            # unmount iso/cd-rom
            os.popen("umount " + self.mountDir)
        # initrd dir
        if self.createAltInitrdRoot == True:
            if os.path.exists(os.path.join(self.customDir, self.altInitrdRoot)):
                print _("INFO: Removing existing Alternate Initrd directory...")
                os.popen('rm -Rf \"' + os.path.join(self.customDir, self.altInitrdRoot) + '\"')
            print _("INFO: Creating Alternate Initrd directory...")
            os.makedirs(os.path.join(self.customDir, self.altInitrdRoot))
            # check for iso
            if self.isoFilename == "":
                mntDlg = gtk.Dialog(title=self.appName, parent=None, flags=0, buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OK, gtk.RESPONSE_OK))
                mntDlg.set_icon_from_file(self.iconFile)
                mntDlg.vbox.set_spacing(10)
                labelSpc = gtk.Label(" ")
                mntDlg.vbox.pack_start(labelSpc)
                labelSpc.show()
                lblText = _("  <b>Please insert Ubuntu Alternate CD and click OK</b>  ")
                label = gtk.Label(lblText)
                label.set_use_markup(True)
                mntDlg.vbox.pack_start(label)
                label.show()
                response = mntDlg.run()
                if response == gtk.RESPONSE_OK:
                    print _("Using Alternate CD for initrd...")
                    mntDlg.destroy()
                    os.popen("mount " + self.mountDir)
                else:
                    mntDlg.destroy()
                    self.setDefaultCursor()
                    return
            else:
                print _("Using ISO for initrd...")
                os.popen('mount -o loop \"' + self.isoFilename + '\" ' + self.mountDir)

            # extract initrd
            print _("Extracting Alternate Initial Ram Disk (initrd)...")
            os.popen('cd \"' + os.path.join(self.customDir, self.altInitrdRoot) + '\"; cat ' + self.mountDir + '/install/initrd.gz | gzip -d | cpio -i')

            # umount cdrom
            os.popen("umount " + self.mountDir)


        self.setDefaultCursor()
        # calculate iso size in the background
        gobject.idle_add(self.calculateAltIsoSize)
        print _("Finished setting up alternate working directory...")
        print " "
        return False


# ---------- Customize Live ---------- #
    def customize(self):
        print _("INFO: Customizing...")
        # check user entered password first, so user doesn't have to wait
        if self.checkUserPassword() == False:
            print _('User passwords do not match.')
            # show warning dlg
            warnDlg = gtk.Dialog(title=self.appName, parent=None, flags=0, buttons=(gtk.STOCK_OK, gtk.RESPONSE_OK))
            warnDlg.set_icon_from_file(self.iconFile)
            warnDlg.vbox.set_spacing(10)
            labelSpc = gtk.Label(" ")
            warnDlg.vbox.pack_start(labelSpc)
            labelSpc.show()
            lblBuildText = _("  <b>Passwords do not match</b>  ")
            lblBuildInfo = _("     Please make sure passwords match and try again...     ")
            label = gtk.Label(lblBuildText)
            lblInfo = gtk.Label(lblBuildInfo)
            label.set_use_markup(True)
            warnDlg.vbox.pack_start(label)
            warnDlg.vbox.pack_start(lblInfo)
            lblInfo.show()
            label.show()
            response = warnDlg.run()
            # destroy dialog no matter what...
            if response == gtk.RESPONSE_OK:
                warnDlg.destroy()
            else:
                warnDlg.destroy()
            # show live cd customization page
            self.wTree.get_widget("notebookCustomize").set_current_page(-1)
            # return - don't continue until error fixed
            return
        else:
            # set user info
            user = self.wTree.get_widget("entryLiveCdUsername").get_text()
            userFull = self.wTree.get_widget("entryLiveCdUserFullname").get_text()
            password = self.wTree.get_widget("entryLiveCdUserPassword").get_text()
            host = self.wTree.get_widget("entryLiveCdHostname").get_text()
            # set live cd info
            self.setLiveCdInfo(username=user, userFullname=userFull, userPassword=password, hostname=host)

        # boot customization
        # live cd splash
        if self.wTree.get_widget("entryLiveCdSplashImage").get_text() != "":
            print _("Customizing Live CD Splash Image...")
            os.popen('cp -f \"' + self.wTree.get_widget("entryLiveCdSplashImage").get_text() + '\" \"' + os.path.join(self.customDir, "remaster/isolinux/splash.pcx") + '\"')
        # live cd text color
        if os.path.exists(os.path.join(self.customDir, "remaster/isolinux/isolinux.cfg")):
            print _("Setting Live CD Text color...")
            color = self.wTree.get_widget("colorbuttonBrowseLiveCdTextColor").get_color()
            rgbColor = color.red/255, color.green/255, color.blue/255
            hexColor = '%02x%02x%02x' % rgbColor
            # replace config line in isolinux.cfg
            f = file(os.path.join(self.customDir, "remaster/isolinux/isolinux.cfg"), 'r')
            lines = []
            r = re.compile('GFXBOOT-BACKGROUND*', re.IGNORECASE)
            # find config string
            for line in f:
                if r.search(line) != None:
                    # replace
                    line = 'GFXBOOT-BACKGROUND 0x' + str(hexColor) + '\n'
                lines.append(line)

            f.close()
            # re-write config file
            f = file(os.path.join(self.customDir, "remaster/isolinux/isolinux.cfg"), 'w')
            f.writelines(lines)
            f.close()

        # usplash image
        if self.wTree.get_widget("entryUsplashFilename").get_text() != "":
            print _("Customizing boot usplash...")
            os.popen('cp -f \"' + self.wTree.get_widget("entryUsplashFilename").get_text() + '\" \"' + os.path.join(self.customDir, "root/usr/lib/usplash/usplash-default.so") + '\"')
            os.popen('cp -f \"' + self.wTree.get_widget("entryUsplashFilename").get_text() + '\" \"' + os.path.join(self.customDir, "initrd/usr/lib/usplash/usplash-artwork.so") + '\"')
            # regenerate initrd for root
            #print ('chroot \"' + os.path.join(self.customDir, "root/") + '\"' + ' update-initramfs -u ')
            os.popen('chroot \"' + os.path.join(self.customDir, "root/") + '\"' + ' update-initramfs -u ')
        # wallpaper
        if self.wTree.get_widget("entryGnomeDesktopWallpaperFilename").get_text() != "":
            print _("Customizing Gnome wallpaper...")
            path, filename = os.path.split(self.wTree.get_widget("entryGnomeDesktopWallpaperFilename").get_text())
            os.popen('cp -f \"' + self.wTree.get_widget("entryGnomeDesktopWallpaperFilename").get_text() + '\" \"' + os.path.join(self.customDir, "root/usr/share/backgrounds/") + filename + '\"')
            os.popen('chmod 777 \"' + os.path.join(self.customDir, "root/usr/share/backgrounds/") + filename + '\"')
            # set wallpaper in gconf
            os.popen('chroot \"' + os.path.join(self.customDir, "root/") + '\"' + ' gconftool-2 --direct --config-source xml:readwrite:/etc/gconf/gconf.xml.defaults --type string --set /desktop/gnome/background/picture_filename \"/usr/share/backgrounds/' + filename + '\"')
        # set fonts in gconf
        if self.wTree.get_widget("labelGnomeDesktopApplicationFontValue").get_text() != "":
            print _("Setting Gnome application font...")
            os.popen('chroot \"' + os.path.join(self.customDir, "root/") + '\"' + ' gconftool-2 --direct --config-source xml:readwrite:/etc/gconf/gconf.xml.defaults --type string --set /desktop/gnome/interface/font_name \"' + self.wTree.get_widget("labelGnomeDesktopApplicationFontValue").get_text() + '\"')
        if self.wTree.get_widget("labelGnomeDesktopDocumentFontValue").get_text() != "":
            print _("Setting Gnome document font...")
            os.popen('chroot \"' + os.path.join(self.customDir, "root/") + '\"' + ' gconftool-2 --direct --config-source xml:readwrite:/etc/gconf/gconf.xml.defaults --type string --set /desktop/gnome/interface/document_font_name \"' + self.wTree.get_widget("labelGnomeDesktopDocumentFontValue").get_text() + '\"')
        if self.wTree.get_widget("labelGnomeDesktopFontValue").get_text() != "":
            print _("Setting Gnome desktop font...")
            os.popen('chroot \"' + os.path.join(self.customDir, "root/") + '\"' + ' gconftool-2 --direct --config-source xml:readwrite:/etc/gconf/gconf.xml.defaults --type string --set /apps/nautilus/preferences/desktop_font \"' + self.wTree.get_widget("labelGnomeDesktopFontValue").get_text() + '\"')
        if self.wTree.get_widget("labelGnomeDesktopTitleBarFontValue").get_text() != "":
            print _("Setting Gnome title bar font...")
            os.popen('chroot \"' + os.path.join(self.customDir, "root/") + '\"' + ' gconftool-2 --direct --config-source xml:readwrite:/etc/gconf/gconf.xml.defaults --type string --set /apps/metacity/general/titlebar_font \"' + self.wTree.get_widget("labelGnomeDesktopTitleBarFontValue").get_text() + '\"')
        if self.wTree.get_widget("labelGnomeDesktopFixedFontValue").get_text() != "":
            print _("Setting Gnome fixed font...")
            os.popen('chroot \"' + os.path.join(self.customDir, "root/") + '\"' + ' gconftool-2 --direct --config-source xml:readwrite:/etc/gconf/gconf.xml.defaults --type string --set /desktop/gnome/interface/monospace_font_name \"' + self.wTree.get_widget("labelGnomeDesktopFixedFontValue").get_text() + '\"')

        # set theme options in gconf
        # theme
        if self.wTree.get_widget("comboboxentryGnomeTheme").get_active_text() != "":
            print _("Setting Gnome theme...")
            os.popen('chroot \"' + os.path.join(self.customDir, "root/") + '\"' + ' gconftool-2 --direct --config-source xml:readwrite:/etc/gconf/gconf.xml.defaults --type string --set /desktop/gnome/interface/gtk_theme \"' + self.wTree.get_widget("comboboxentryGnomeTheme").get_active_text() + '\"')
        # window borders
        if self.wTree.get_widget("comboboxentryGnomeThemeWindowBorders").get_active_text() != "":
            print _("Setting Gnome window borders...")
            os.popen('chroot \"' + os.path.join(self.customDir, "root/") + '\"' + ' gconftool-2 --direct --config-source xml:readwrite:/etc/gconf/gconf.xml.defaults --type string --set /apps/metacity/general/theme \"' + self.wTree.get_widget("comboboxentryGnomeThemeWindowBorders").get_active_text() + '\"')
        # icons
        if self.wTree.get_widget("comboboxentryGnomeThemeIcons").get_active_text() != "":
            print _("Setting Gnome icons...")
            os.popen('chroot \"' + os.path.join(self.customDir, "root/") + '\"' + ' gconftool-2 --direct --config-source xml:readwrite:/etc/gconf/gconf.xml.defaults --type string --set /desktop/gnome/interface/icon_theme \"' + self.wTree.get_widget("comboboxentryGnomeThemeIcons").get_active_text() + '\"')

        # gdm configuration
        if self.checkCustomGdm() == True:
            print _("Configuring GDM...")
            conf = "[daemon]\nRemoteGreeter=/usr/lib/gdm/gdmgreeter\n\n"
            # security
            print _("Setting GDM Security...")
            if self.wTree.get_widget("checkbuttonGdmRootLogin").get_active() == True:
                conf = conf + "[security]\nAllowRoot=true\n\n"
            else:
                conf = conf + "[security]\nAllowRoot=false\n\n"
            # xdmcp
            print _("Setting GDM XDMCP...")
            if self.wTree.get_widget("checkbuttonGdmXdmcp").get_active() == True:
                conf = conf + "[xdmcp]\nEnable=true\n\n"
            else:
                conf = conf + "[xdmcp]\nEnable=false\n\n"
            conf = conf + "[gui]\n\n"
            conf = conf + "[greeter]\n"
            # gdm color
            color = self.wTree.get_widget("colorbuttonBrowseGdmBackgroundColor").get_color()
            rgbColor = color.red/255, color.green/255, color.blue/255
            hexColor = '%02x%02x%02x' % rgbColor
            conf += 'GraphicalThemedColor=#' + str(hexColor) + '\n'
            if self.wTree.get_widget("comboboxentryGnomeGdmTheme").get_active_text() != "":
                print _("Setting GDM Theme...")
                conf = conf + "GraphicalTheme=" + self.wTree.get_widget("comboboxentryGnomeGdmTheme").get_active_text() + "\n"
            print _("Setting GDM Sounds...")
            if self.wTree.get_widget("checkbuttonGdmSounds").get_active() == True:
                conf = conf + "SoundOnLogin=true\n\n"
            else:
                conf = conf + "SoundOnLogin=false\n\n"

            print _("Backing up GDM configuration...")
            os.popen('mv -f \"' + os.path.join(self.customDir, "root/etc/gdm/gdm.conf-custom") + '\" \"' + os.path.join(self.customDir, "root/etc/gdm/gdm.conf-custom.orig") + '\"')

            print _("Saving GDM configuration...")
            f=open(os.path.join(self.customDir, "root/etc/gdm/gdm.conf-custom"), 'w')
            f.write(conf)
            f.close()


        # splash screen
        if self.wTree.get_widget("entryGnomeSplashScreenFilename").get_text() != "":
            print _("Customizing Gnome Splash Screen...")
            path, filename = os.path.split(self.wTree.get_widget("entryGnomeSplashScreenFilename").get_text())
            os.popen('cp -f \"' + self.wTree.get_widget("entryGnomeSplashScreenFilename").get_text() + '\" \"' + os.path.join(self.customDir, "root/usr/share/pixmaps/splash/") + filename + '\"')
            os.popen('chmod 777 \"' + os.path.join(self.customDir, "root/usr/share/pixmaps/splash/") + filename + '\"')
            # set splash screen in gconf
            os.popen('chroot \"' + os.path.join(self.customDir, "root/") + '\"' + ' gconftool-2 --direct --config-source xml:readwrite:/etc/gconf/gconf.xml.defaults --type string --set /apps/gnome-session/options/splash_image \"splash/' + filename + '\"')


        # set up apt repos
        if self.checkCustomRepos() == True:
            # move old sources.list apt file
            print _("Backing up old apt config...")
            os.popen('mv -f \"' + os.path.join(self.customDir, "root/etc/apt/sources.list") + '\" \"' + os.path.join(self.customDir, "root/etc/apt/sources.list.orig") + '\"')
            #os.popen('rm -f \"' + os.path.join(self.customDir, "root/etc/apt/sources.list") + '\"')
            # load ubuntu codename for apt
            ubuntuCodename = ''
            if self.cdUbuntuVersion == self.dapperVersion:
                ubuntuCodename = 'dapper'
            elif self.cdUbuntuVersion == self.edgyVersion:
                ubuntuCodename = 'edgy'
            elif self.cdUbuntuVersion == self.feistyVersion:
                ubuntuCodename = 'feisty'
            else:
                print _("Unable to detect codename for Ubuntu CD Version - APT Repositories will NOT be modified...")

            if ubuntuCodename != '':
                # ubuntu official
                if self.wTree.get_widget("checkbuttonAptRepoUbuntuOfficial").get_active() == True:
                    print _("Adding Official Apt Repository...")
                    os.popen('echo \"deb http://archive.ubuntu.com/ubuntu/ ' + ubuntuCodename + ' main\" >> \"' + os.path.join(self.customDir, "root/etc/apt/sources.list") + '\"')
                    print _('Adding Ubuntu Official Security Repository...')
                    os.popen('echo \"deb http://security.ubuntu.com/ubuntu ' + ubuntuCodename +'-security main restricted\" >> \"' + os.path.join(self.customDir, "root/etc/apt/sources.list") + '\"')
                    os.popen('echo \"deb-src http://security.ubuntu.com/ubuntu ' + ubuntuCodename + '-security main restricted\" >> \"' + os.path.join(self.customDir, "root/etc/apt/sources.list") + '\"')

                # ubuntu restricted
                if self.wTree.get_widget("checkbuttonAptRepoUbuntuRestricted").get_active() == True:
                    print _("Adding Ubuntu Restricted Apt Repository...")
                    os.popen('echo \"deb http://archive.ubuntu.com/ubuntu/ ' + ubuntuCodename + ' restricted\" >> \"' + os.path.join(self.customDir, "root/etc/apt/sources.list") + '\"')

                # ubuntu universe
                if self.wTree.get_widget("checkbuttonAptRepoUbuntuUniverse").get_active() == True:
                    print _("Adding Ubuntu Universe Apt Repository...")
                    os.popen('echo \"deb http://archive.ubuntu.com/ubuntu/ ' + ubuntuCodename + ' universe\" >> \"' + os.path.join(self.customDir, "root/etc/apt/sources.list") + '\"')
                    print _('Adding Ubuntu Universe Security Repository...')
                    os.popen('echo \"deb http://security.ubuntu.com/ubuntu ' + ubuntuCodename + '-security universe\" >> \"' + os.path.join(self.customDir, "root/etc/apt/sources.list") + '\"')
                    os.popen('echo \"deb-src http://security.ubuntu.com/ubuntu ' + ubuntuCodename + '-security universe\" >> \"' + os.path.join(self.customDir, "root/etc/apt/sources.list") + '\"')

                # ubuntu multiverse
                if self.wTree.get_widget("checkbuttonAptRepoUbuntuMultiverse").get_active() == True:
                    print _("Adding Ubuntu Multiverse Apt Repository...")
                    os.popen('echo \"deb http://archive.ubuntu.com/ubuntu/ ' + ubuntuCodename + ' multiverse\" >> \"' + os.path.join(self.customDir, "root/etc/apt/sources.list") + '\"')

                # ubuntu official updates
                print _("Adding Ubuntu Official Updates Apt Repository...")
                os.popen('echo \"deb http://us.archive.ubuntu.com/ubuntu/ ' + ubuntuCodename + '-updates main restricted\" >> \"' + os.path.join(self.customDir, "root/etc/apt/sources.list") + '\"')

                # custom archives
                buf = self.wTree.get_widget("textviewAptCustomArchives").get_buffer()
                if buf.get_text(buf.get_start_iter(),buf.get_end_iter()) != '':
                    print _("Adding Custom Apt Repositories...")
                    os.popen('echo \"' + buf.get_text(buf.get_start_iter(),buf.get_end_iter()) + '\" >> \"' + os.path.join(self.customDir, "root/etc/apt/sources.list") + '\"')

        # interactive editing
        if self.interactiveEdit == True:
            # copy template user config to /etc/skel in root dir
            try:
                print _('Removing existing template...')
                os.popen('rm -Rf \"' + os.path.join(self.customDir, "root/etc/skel/*") + '\"')
                print _('Copying User Template...')
                os.popen('cp -Rf /home/reconstructor ' + os.path.join(self.customDir, "root/etc/skel") )
                os.popen('cp -Rf ' + os.path.join(self.customDir, "root/etc/skel/reconstructor/*") + ' ' + os.path.join(self.customDir, "root/etc/skel/"))
                os.popen('rm -Rf ' + os.path.join(self.customDir, "root/etc/skel/reconstructor"))
            except Exception, detail:
                errCopy = _('Error copying template: ')
                print errCopy, detail
                pass
        # startup optimization
        if self.wTree.get_widget("checkbuttonOptimizationStartupEnable").get_active() == True:
            self.optimizeStartup()

        # shutdown optimization
        if self.wTree.get_widget("checkbuttonOptimizationShutdown").get_active() == True:
            self.optimizeShutdown()

        # run modules
        # HACK: check for run on boot scripts and clear previous if new ones selected
        self.execModulesEnabled = False;
        self.treeModel.foreach(self.checkExecModuleEnabled)
        if self.execModulesEnabled == True:
            print _('Running modules...')
            modExecScrChroot = '#!/bin/sh\n\ncd /tmp ;\n'
            # copy all "execute" enabled scripts proper location (chroot or customdir)
            self.treeModel.foreach(self.copyExecuteModule)
            # find all modules in chroot and chain together and run
            for execModRoot, execModexecModDirs, execModFiles in os.walk(os.path.join(self.customDir, "root/tmp/")):
                for execMod in execModFiles:
                    r, ext = os.path.splitext(execMod)
                    if ext == '.rmod':
                        modExecScrChroot += 'echo Running Module: ' + os.path.basename(execMod) + '\n'
                        modExecScrChroot += 'bash \"/tmp/' + os.path.basename(execMod) + '\"' + ' ;\n '
            modExecScrChroot += '\necho \'--------------------\'\necho \'Modules Finished...\'\n'
            modExecScrChroot += 'sleep 10'
            #modExecScrChroot += 'echo \'Press [Enter] to continue...\'\nread \n'
            #print modExecScrChroot
            fModExecChroot=open(os.path.join(self.customDir, "root/tmp/module-exec.sh"), 'w')
            fModExecChroot.write(modExecScrChroot)
            fModExecChroot.close()
            os.popen('chmod a+x ' + os.path.join(self.customDir, "root/tmp/module-exec.sh"))
            #os.popen('xterm -title \'Reconstructor Module Exec\' -e chroot \"' + os.path.join(self.customDir, "root/") + '\" /tmp/module-exec.sh')
            # copy dns info
            print _("Copying DNS info...")
            os.popen('cp -f /etc/resolv.conf ' + os.path.join(self.customDir, "root/etc/resolv.conf"))
            # mount /proc
            print _("Mounting /proc filesystem...")
            os.popen('mount --bind /proc \"' + os.path.join(self.customDir, "root/proc") + '\"')
            # copy apt.conf
            print _("Copying apt.conf configuration...")
            os.popen('cp -f /etc/apt/apt.conf ' + os.path.join(self.customDir, "root/etc/apt/apt.conf"))
            # copy wgetrc
            print _("Copying wgetrc configuration...")
            # backup
            os.popen('mv -f \"' + os.path.join(self.customDir, "root/etc/wgetrc") + '\" \"' + os.path.join(self.customDir, "root/etc/wgetrc.orig") + '\"')
            os.popen('cp -f /etc/wgetrc ' + os.path.join(self.customDir, "root/etc/wgetrc"))
            # run module script
            os.popen('gnome-terminal --hide-menubar -t \"Reconstructor Modules\" -x chroot \"' + os.path.join(self.customDir, "root/") + '\" /tmp/module-exec.sh')
            # cleanup
            os.popen('cd \"' + os.path.join(self.customDir, "root/tmp/") + '\" ; ' + 'rm -Rf *.rmod 1>&2 2>/dev/null')
            os.popen('rm -Rf \"' + os.path.join(self.customDir, "root/tmp/module-exec.sh") + '\" 1>&2 2>/dev/null')
            # restore wgetrc
            print _("Restoring wgetrc configuration...")
            os.popen('mv -f \"' + os.path.join(self.customDir, "root/etc/wgetrc.orig") + '\" \"' + os.path.join(self.customDir, "root/etc/wgetrc") + '\"')
            # remove apt.conf
            print _("Removing apt.conf configuration...")
            os.popen('rm -Rf \"' + os.path.join(self.customDir, "root/etc/apt/apt.conf") + '\"')
            # remove dns info
            print _("Removing DNS info...")
            os.popen('rm -Rf \"' + os.path.join(self.customDir, "root/etc/resolv.conf") + '\"')
            # umount /proc
            print _("Umounting /proc...")
            os.popen('umount \"' + os.path.join(self.customDir, "root/proc/") + '\"')

        # HACK: check for run on boot scripts and clear previous if new ones selected
        self.bootModulesEnabled = False;
        self.treeModel.foreach(self.checkBootModuleEnabled)
        if self.bootModulesEnabled == True:
            # create module script to add to live cd for modules that run on boot
            print _('Copying modules that run on boot...')
            modScrRunOnBoot = '#/bin/sh\n\nsleep 5\n'
            # clear previous
            os.popen('rm -Rf \"' + os.path.join(self.customDir, "root/usr/share/reconstructor/scripts/") + '\"')
            # copy all "run on boot" enabled scripts
            self.treeModel.foreach(self.copyRunOnBootModule)
            for bootModRoot, bootModDirs, bootModFiles in os.walk(os.path.join(self.customDir, "root/usr/share/reconstructor/scripts/")):
                for bootMod in bootModFiles:
                    r, ext = os.path.splitext(bootMod)
                    if ext == '.rmod':
                        modScrRunOnBoot += '\necho Running Module: ' + os.path.basename(bootMod) + '\n'
                        modScrRunOnBoot += '\"/usr/share/reconstructor/scripts/' + os.path.basename(bootMod) + '\"' + ' ; '

            modScrRunOnBoot += '\nsudo rm -Rf /etc/skel/.gnomerc\nsudo rm -Rf /usr/share/reconstructor/\necho \'Modules Finished...\'\n\nsleep 5'
            # create boot mod script
            print _('Generating boot module script...')
            # remove existing
            if os.path.exists(os.path.join(self.customDir, "root/etc/skel/.gnomerc")):
                os.popen('rm -Rf \"' + os.path.join(self.customDir, "root/etc/skel/.gnomerc") + '\"')
            fGnomerc = open(os.path.join(self.customDir, "root/etc/skel/.gnomerc"), 'w')
            fGnomerc.write("bash /usr/share/reconstructor/scripts/boot-scripts-exec.sh &")
            fGnomerc.close()
            os.popen('chmod -R 777 \"' + os.path.join(self.customDir, "root/etc/skel/.gnomerc") + '\"')
            fbootModScript = open(os.path.join(self.customDir, "root/usr/share/reconstructor/scripts/boot-scripts-exec.sh"), 'w')
            fbootModScript.write(modScrRunOnBoot)
            fbootModScript.close()
            os.popen('chmod a+x \"' + os.path.join(self.customDir, "root/usr/share/reconstructor/scripts/boot-scripts-exec.sh") + '\"')
            # chmod all scripts
            os.popen('chmod -R 775 \"' + os.path.join(self.customDir, "root/usr/share/reconstructor/") + '\"')

        # manual software
        # check for manual install
        if self.manualInstall == True:
            print _("Manually installing all existing .deb archives in /var/cache/apt/archives...")
            os.popen('chroot \"' + os.path.join(self.customDir, "root/") + '\"' + ' dpkg -i -R /var/cache/apt/archives/ 1>&2 2>/dev/null')
            os.popen('chroot \"' + os.path.join(self.customDir, "root/") + '\"' + ' apt-get clean')
            os.popen('chroot \"' + os.path.join(self.customDir, "root/") + '\"' + ' apt-get autoclean')

        # DEPRECATED - replacing with module framework
        # install software

        # install regular software
        if self.checkSoftware() == True:
            # copy dns info
            print _("Copying DNS info...")
            os.popen('cp -f /etc/resolv.conf ' + os.path.join(self.customDir, "root/etc/resolv.conf"))
            # mount /proc
            print _("Mounting /proc filesystem...")
            os.popen('mount --bind /proc \"' + os.path.join(self.customDir, "root/proc") + '\"')
            # copy apt.conf
            print _("Copying apt.conf configuration...")
            os.popen('cp -f /etc/apt/apt.conf ' + os.path.join(self.customDir, "root/etc/apt/apt.conf"))
            # copy wgetrc
            print _("Copying wgetrc configuration...")
            # backup
            os.popen('mv -f \"' + os.path.join(self.customDir, "root/etc/wgetrc") + '\" \"' + os.path.join(self.customDir, "root/etc/wgetrc.orig") + '\"')
            os.popen('cp -f /etc/wgetrc ' + os.path.join(self.customDir, "root/etc/wgetrc"))
            # update ONLY if repositories are selected
            if self.checkCustomRepos() == True:
                print _("Updating APT Information...")
                # update apt
                os.popen('chroot \"' + os.path.join(self.customDir, "root/") + '\"' + ' apt-get update ')
            # clean cache
            os.popen('chroot \"' + os.path.join(self.customDir, "root/") + '\"' + ' apt-get clean')
            os.popen('chroot \"' + os.path.join(self.customDir, "root/") + '\"' + ' apt-get autoclean')

            # custom apt-get
            if self.wTree.get_widget("entryCustomAptInstall").get_text() != "":
                print _("Installing Custom Software...")
                os.popen('chroot \"' + os.path.join(self.customDir, "root/") + '\"' + ' apt-get install --assume-yes --force-yes -d ' + self.wTree.get_widget("entryCustomAptInstall").get_text())
                os.popen('chroot \"' + os.path.join(self.customDir, "root/") + '\"' + ' dpkg -i -R /var/cache/apt/archives/ 1>&2 2>/dev/null')
                os.popen('chroot \"' + os.path.join(self.customDir, "root/") + '\"' + ' apt-get clean')
                os.popen('chroot \"' + os.path.join(self.customDir, "root/") + '\"' + ' apt-get autoclean')

            # custom software removal
            if self.wTree.get_widget("entryCustomAptRemove").get_text() != "":
                print _("Removing Custom Software...")
                os.popen('chroot \"' + os.path.join(self.customDir, "root/") + '\"' + ' dpkg -P ' + self.wTree.get_widget("entryCustomAptRemove").get_text() + ' 1>&2 2>/dev/null')
                os.popen('chroot \"' + os.path.join(self.customDir, "root/") + '\"' + ' dpkg --configure -a')
                os.popen('chroot \"' + os.path.join(self.customDir, "root/") + '\"' + ' apt-get clean')
                os.popen('chroot \"' + os.path.join(self.customDir, "root/") + '\"' + ' apt-get autoclean')


            # restore wgetrc
            print _("Restoring wgetrc configuration...")
            os.popen('mv -f \"' + os.path.join(self.customDir, "root/etc/wgetrc.orig") + '\" \"' + os.path.join(self.customDir, "root/etc/wgetrc") + '\"')
            # remove apt.conf
            print _("Removing apt.conf configuration...")
            os.popen('rm -Rf \"' + os.path.join(self.customDir, "root/etc/apt/apt.conf") + '\"')
            # remove dns info
            print _("Removing DNS info...")
            os.popen('rm -Rf \"' + os.path.join(self.customDir, "root/etc/resolv.conf") + '\"')
            # umount /proc
            print _("Umounting /proc...")
            os.popen('umount \"' + os.path.join(self.customDir, "root/proc/") + '\"')
            self.setDefaultCursor()
            self.setPage(self.pageLiveBuild)




# ---------- Customize Alternate ----- #
    def customizeAlt(self):
        # get alternate cd info
        self.altCdUbuntuDist = 'unknown'
        self.altCdUbuntuVersion = 'unknown'
        self.altCdUbuntuArch = 'unknown'
        # build regex for info
        r = re.compile(self.regexUbuntuAltCdInfo, re.IGNORECASE)
        f = file(os.path.join(self.customDir, "remaster_alt/.disk/info"), 'r')
        for l in f:
            if r.match(l) != None:
                self.altCdUbuntuDist = r.match(l).group(1)
                self.altCdUbuntuVersion = r.match(l).group(2)
                self.altCdUbuntuArch = r.match(l).group(3)
        f.close()
        distText = _('Distribution:')
        verText = _('Version:')
        archText = _('Architecture:')
        print distText + ' ' + self.altCdUbuntuDist
        print verText + ' ' + self.altCdUbuntuVersion
        print archText + ' ' + self.altCdUbuntuArch

        # load ubuntu codename for apt
        self.ubuntuCodename = ''
        if self.altCdUbuntuVersion == self.dapperVersion:
            self.ubuntuCodename = 'dapper'
        elif self.altCdUbuntuVersion == self.edgyVersion:
            self.ubuntuCodename = 'edgy'
        else:
            print _("Unable to detect codename for Ubuntu CD Version - APT Repositories will NOT be modified...")


        # set up apt repos
        if self.checkAltCustomRepos() == True:
            # move old sources.list apt file
            print _("Backing up old apt config...")
            os.popen('mv -f /etc/apt/sources.list /etc/apt/sources.list.orig')
            os.popen('cp -Rf /var/cache/apt /var/cache/apt.orig')
            # check for directories and create if necessary
            if os.path.exists(os.path.join(self.customDir, self.altRemasterRepo)) == False:
                os.popen('mkdir -p \"' + os.path.join(self.customDir, self.altRemasterRepo) + '\"')
            if os.path.exists(os.path.join(self.customDir, self.altRemasterRepo + "/archives")) == False:
                os.popen('mkdir -p \"' + os.path.join(self.customDir, self.altRemasterRepo + "/archives/partial") + '\"')
            os.popen('chmod -R 775 \"' + os.path.join(self.customDir, self.altRemasterRepo) + '\"')

            if self.ubuntuCodename != '':
                # ubuntu official
                if self.wTree.get_widget("checkbuttonAltUbuntuOfficialRepo").get_active() == True:
                    print _("Adding Ubuntu Official Apt Repository...")
                    os.popen('echo \"deb http://archive.ubuntu.com/ubuntu/ ' + self.ubuntuCodename + ' main\" >> /etc/apt/sources.list')
                    print _('Adding Ubuntu Official Security Repository...')
                    os.popen('echo \"deb http://security.ubuntu.com/ubuntu ' + self.ubuntuCodename +'-security main restricted\" >> /etc/apt/sources.list')
                    os.popen('echo \"deb-src http://security.ubuntu.com/ubuntu ' + self.ubuntuCodename + '-security main restricted\" >> /etc/apt/sources.list')

                # ubuntu restricted
                if self.wTree.get_widget("checkbuttonAltUbuntuRestrictedRepo").get_active() == True:
                    print _("Adding Ubuntu Restricted Apt Repository...")
                    os.popen('echo \"deb http://archive.ubuntu.com/ubuntu/ ' + self.ubuntuCodename + ' restricted\" >> /etc/apt/sources.list')

                # ubuntu universe
                if self.wTree.get_widget("checkbuttonAltUbuntuUniverseRepo").get_active() == True:
                    print _("Adding Ubuntu Universe Apt Repository...")
                    os.popen('echo \"deb http://archive.ubuntu.com/ubuntu/ ' + self.ubuntuCodename + ' universe\" >> /etc/apt/sources.list')
                    print _('Adding Ubuntu Universe Security Repository...')
                    os.popen('echo \"deb http://security.ubuntu.com/ubuntu ' + self.ubuntuCodename + '-security universe\" >> /etc/apt/sources.list')
                    os.popen('echo \"deb-src http://security.ubuntu.com/ubuntu ' + self.ubuntuCodename + '-security universe\" >> /etc/apt/sources.list')

                # ubuntu multiverse
                if self.wTree.get_widget("checkbuttonAltUbuntuMultiverseRepo").get_active() == True:
                    print _("Adding Ubuntu Multiverse Apt Repository...")
                    os.popen('echo \"deb http://archive.ubuntu.com/ubuntu/ ' + self.ubuntuCodename + ' multiverse\" >> /etc/apt/sources.list')

                # ubuntu official updates
                print _("Adding Ubuntu Official Updates Apt Repository...")
                os.popen('echo \"deb http://us.archive.ubuntu.com/ubuntu/ ' + self.ubuntuCodename + '-updates main restricted\" >> /etc/apt/sources.list')

                # custom archives
                buf = self.wTree.get_widget("textviewAltAptCustomRepos").get_buffer()
                if buf.get_text(buf.get_start_iter(),buf.get_end_iter()) != '':
                    print _("Adding Custom Apt Repositories...")
                    os.popen('echo \"' + buf.get_text(buf.get_start_iter(),buf.get_end_iter()) + '\" >> /etc/apt/sources.list')

                # download packages
                buf = self.wTree.get_widget("textviewAltPackages").get_buffer()
                if buf.get_text(buf.get_start_iter(),buf.get_end_iter()) != '':
                    print _("Updating apt (apt-get update)...")
                    os.popen('apt-get update')
                    print _("Downloading extra packages...")
                    print(commands.getoutput('apt-get install -d -y -m --reinstall --allow-unauthenticated -o Dir::Cache=\"' + os.path.join(self.customDir, self.altRemasterRepo) + '/\" ' + buf.get_text(buf.get_start_iter(),buf.get_end_iter())))


                # copy .debs to remaster dir
                # check for extras dir
                if os.path.exists(os.path.join(self.customDir, self.altRemasterDir) + "/dists/" + self.ubuntuCodename + "/extras") == False:
                    os.popen('cd \"' + os.path.join(self.customDir, self.altRemasterDir) + '\" ; mkdir -p dists/' + self.ubuntuCodename + '/extras/binary-' + self.altCdUbuntuArch)
                # pool dir
                if os.path.exists(os.path.join(self.customDir, self.altRemasterDir) + "/pool/extras") == False:
                    os.popen('cd \"' + os.path.join(self.customDir, self.altRemasterDir) + '\" ; mkdir -p pool/extras')
                # check and copy
                if commands.getoutput('ls \"' + os.path.join(self.customDir, self.altRemasterRepo) + '/archives\"' + ' | grep .deb') != '':
                    print _("Copying downloaded archives into pool...")
                    os.popen('cd \"' + os.path.join(self.customDir, self.altRemasterRepo) + '/archives\" ; cp -R *.deb \"' + os.path.join(self.customDir, self.altRemasterDir) + '/pool/extras/\"')
                    #print _("Cleaning temporary apt cache...")
                    os.popen('apt-get clean -o Dir::Cache=\"' + os.path.join(self.customDir, self.altRemasterRepo) + '/\" ')

                # check dependencies for extras
                p = PackageHelper(customDirectory=self.customDir, remasterDirectory=self.altRemasterDir, remasterRepoDirectory=self.altRemasterRepo, remasterTempDirectory=self.tmpDir, distribution=self.ubuntuCodename)
                print _("Checking and downloading dependencies for extra packages...")
                p.resolveDependencies()

                #print _("Cleaning temporary apt cache...")
                os.popen('apt-get clean -o Dir::Cache=\"' + os.path.join(self.customDir, self.altRemasterRepo) + '/\" ')

                print _("Restoring original apt configuration...")
                os.popen('mv -f /etc/apt/sources.list.orig /etc/apt/sources.list')
                os.popen('rm -Rf /var/cache/apt')
                os.popen('mv -f /var/cache/apt.orig /var/cache/apt')
                os.popen('rm -Rf /var/cache/apt.orig')


        # check for pool dir
        if os.path.exists(os.path.join(self.customDir, self.altRemasterDir) + '/pool/extras' ) == True:
            # check for debs
            if commands.getoutput('ls \"' + os.path.join(self.customDir, self.altRemasterDir) + '/pool/extras/\"' + ' | grep .deb') != '':
                # create Release file
                print _("Creating Release file...")
                # check for extras directory
                if os.path.exists(os.path.join(self.customDir, self.altRemasterDir) + '/dists/' + self.ubuntuCodename + '/extras/binary-' + self.altCdUbuntuArch) == False:
                    os.popen('mkdir -p \"' + os.path.join(self.customDir, self.altRemasterDir) + '/dists/' + self.ubuntuCodename + '/extras/binary-' + self.altCdUbuntuArch + '\"')
                f=open(os.path.join(self.customDir, self.altRemasterDir) + '/dists/' + self.ubuntuCodename + '/extras/binary-' + self.altCdUbuntuArch + '/Release', 'w')
                f.write('Archive: ' + self.ubuntuCodename + '\nVersion: ' + self.altCdUbuntuVersion + '\nComponent: extras\nOrigin: Ubuntu\nLabel: Ubuntu\nArchitecture: ' + self.altCdUbuntuArch + '\n')
                f.close()
                # check for GPG key and create if necessary
                status, output = commands.getstatusoutput('gpg --list-keys | grep \"' + self.altGpgKeyName +'\" > /dev/null')
                if status == 0:
                    # key found
                    print "GPG Key Found..."
                else:
                    # not found; create
                    print _("No GPG Key found... Creating...")
                    try:
                        # get key information
                        gpgKeyEmail, gpgKeyPhrase = None, None
                        try:
                            gpgKeyEmail, gpgKeyPhrase = self.getGpgKeyInfo()
                        except:
                            pass
                        if gpgKeyEmail != None and gpgKeyPhrase != None:
                            #print gpgKeyEmail, gpgKeyPhrase
                            # create key
                            key = "Key-Type: DSA\nKey-Length: 1024\nSubkey-Type: ELG-E\nSubkey-Length: 2048\nName-Real: " + self.altGpgKeyName + "\nName-Comment: " + self.altGpgKeyComment + "\nName-Email: " + gpgKeyEmail + "\nExpire-Date: 0\nPassphrase: " + gpgKeyPhrase
                            #print key
                            f = open(os.path.join(self.customDir, self.tmpDir) + '/gpg.key', 'w')
                            f.write(key)
                            f.close()
                            # create the key from the gpg.key file
                            os.popen('gpg --gen-key --batch --gen-key \"' + os.path.join(self.customDir, self.tmpDir) + '/gpg.key\" > /dev/null')
                            # reset permissions for user
                            os.popen('chown -R ' + os.getlogin() + ' \"' + os.environ['HOME'] + '/.gnupg/\"')
                            print _("GPG Key Generation Finished...")
                            # remove key generation file
                            os.popen('rm -Rf \"' + os.path.join(self.customDir, self.tmpDir) + '/gpg.key\"')

                        else:
                            raise Exception, _("Email and passphrase must not be empty and must match...")
                            self.setDefaultCursor()
                            return False
                    except Exception, detail:
                        errText = _("Error Creating GPG Key:")
                        print errText, detail
                        self.setDefaultCursor()
                        return False

                # create apt.conf
                if os.path.exists(os.path.join(self.customDir, self.tmpDir) + '/apt.conf') == False:
                    print _("Creating apt.conf...")
                    os.popen('cd \"' + os.path.join(self.customDir, self.altRemasterDir) + '\" ; cat dists/' + self.ubuntuCodename + '/Release | egrep -v \"^ \" | egrep -v \"^(Date|MD5Sum|SHA1)\" | sed \'s/: / \"/\' | sed \'s/^/APT::FTPArchive::Release::/\' | sed \'s/$/\";/\' > \"' + os.path.join(self.customDir, self.tmpDir) + '/apt.conf\"')

                # build paths for conf files (so sed can understand them...)
                archDir = os.path.join(self.customDir, self.altRemasterDir)
                archDir = archDir.replace('/', '\\/')
                indexDir = os.path.join(self.customDir, self.tmpDir)
                indexDir = indexDir.replace('/', '\\/')
                #check for apt-ftparchive-deb.conf
                if os.path.exists(os.path.join(self.customDir, self.tmpDir) + '/apt-ftparchive-deb.conf') == False:
                    # create apt-ftparchive-deb.conf
                    print _("Creating apt-ftparchive-deb.conf...")
                    # add archive dir path
                    os.popen('cat \"' + os.getcwd() + '/lib/apt-ftparchive-deb.conf\" | sed \'s/ARCHIVEDIR/' + archDir + '/\' > \"' + os.path.join(self.customDir, self.tmpDir) + '/apt-ftparchive-deb.conf\"')
                    # add dist
                    os.popen('cat \"' + os.path.join(self.customDir, self.tmpDir) + '/apt-ftparchive-deb.conf\" | sed \'s/DIST/' + self.ubuntuCodename + '/\' > \"' + os.path.join(self.customDir, self.tmpDir) + '/apt-ftparchive-deb.conf.tmp\"')
                    os.popen('cd \"' + os.path.join(self.customDir, self.tmpDir) + '\" ; mv apt-ftparchive-deb.conf.tmp apt-ftparchive-deb.conf ; rm -f apt-ftparchive-deb.conf.tmp')
                    # add architecture
                    os.popen('cat \"' + os.path.join(self.customDir, self.tmpDir) + '/apt-ftparchive-deb.conf\" | sed \'s/ARCH/' + self.altCdUbuntuArch + '/\' > \"' + os.path.join(self.customDir, self.tmpDir) + '/apt-ftparchive-deb.conf.tmp\"')
                    os.popen('cd \"' + os.path.join(self.customDir, self.tmpDir) + '\" ; mv apt-ftparchive-deb.conf.tmp apt-ftparchive-deb.conf ; rm -f apt-ftparchive-deb.conf.tmp')
                    # add index path
                    os.popen('cat \"' + os.path.join(self.customDir, self.tmpDir) + '/apt-ftparchive-deb.conf\" | sed \'s/INDEXDIR/' + indexDir + '/\' > \"' + os.path.join(self.customDir, self.tmpDir) + '/apt-ftparchive-deb.conf.tmp\"')
                    os.popen('cd \"' + os.path.join(self.customDir, self.tmpDir) + '\" ; mv apt-ftparchive-deb.conf.tmp apt-ftparchive-deb.conf ; rm -f apt-ftparchive-deb.conf.tmp')

                # check for apt-ftparchive-udeb.conf
                if os.path.exists(os.path.join(self.customDir, self.tmpDir) + '/apt-ftparchive-udeb.conf') == False:
                    print _("Creating apt-ftparchive-udeb.conf...")
                    # add archive dir path
                    os.popen('cat \"' + os.getcwd() + '/lib/apt-ftparchive-udeb.conf\" | sed \'s/ARCHIVEDIR/' + archDir + '/\' > \"' + os.path.join(self.customDir, self.tmpDir) + '/apt-ftparchive-udeb.conf\"')
                    # add dist
                    os.popen('cat \"' + os.path.join(self.customDir, self.tmpDir) + '/apt-ftparchive-udeb.conf\" | sed \'s/DIST/' + self.ubuntuCodename + '/\' > \"' + os.path.join(self.customDir, self.tmpDir) + '/apt-ftparchive-udeb.conf.tmp\"')
                    os.popen('cd \"' + os.path.join(self.customDir, self.tmpDir) + '\" ; mv apt-ftparchive-udeb.conf.tmp apt-ftparchive-udeb.conf ; rm -f apt-ftparchive-udeb.conf.tmp')
                    # add architecture
                    os.popen('cat \"' + os.path.join(self.customDir, self.tmpDir) + '/apt-ftparchive-udeb.conf\" | sed \'s/ARCH/' + self.altCdUbuntuArch + '/\' > \"' + os.path.join(self.customDir, self.tmpDir) + '/apt-ftparchive-udeb.conf.tmp\"')
                    os.popen('cd \"' + os.path.join(self.customDir, self.tmpDir) + '\" ; mv apt-ftparchive-udeb.conf.tmp apt-ftparchive-udeb.conf ; rm -f apt-ftparchive-udeb.conf.tmp')
                    # add index path
                    os.popen('cat \"' + os.path.join(self.customDir, self.tmpDir) + '/apt-ftparchive-udeb.conf\" | sed \'s/INDEXDIR/' + indexDir + '/\' > \"' + os.path.join(self.customDir, self.tmpDir) + '/apt-ftparchive-udeb.conf.tmp\"')
                    os.popen('cd \"' + os.path.join(self.customDir, self.tmpDir) + '\" ; mv apt-ftparchive-udeb.conf.tmp apt-ftparchive-udeb.conf ; rm -f apt-ftparchive-udeb.conf.tmp')

                # check for apt-ftparchive-extras.conf
                if os.path.exists(os.path.join(self.customDir, self.tmpDir) + '/apt-ftparchive-extras.conf') == False:
                    print _("Creating apt-ftparchive-extras.conf...")
                    # add archive dir path
                    os.popen('cat \"' + os.getcwd() + '/lib/apt-ftparchive-extras.conf\" | sed \'s/ARCHIVEDIR/' + archDir + '/\' > \"' + os.path.join(self.customDir, self.tmpDir) + '/apt-ftparchive-extras.conf\"')
                    # add dist
                    os.popen('cat \"' + os.path.join(self.customDir, self.tmpDir) + '/apt-ftparchive-extras.conf\" | sed \'s/DIST/' + self.ubuntuCodename + '/\' > \"' + os.path.join(self.customDir, self.tmpDir) + '/apt-ftparchive-extras.conf.tmp\"')
                    os.popen('cd \"' + os.path.join(self.customDir, self.tmpDir) + '\" ; mv apt-ftparchive-extras.conf.tmp apt-ftparchive-extras.conf ; rm -f apt-ftparchive-extras.conf.tmp')
                    # add architecture
                    os.popen('cat \"' + os.path.join(self.customDir, self.tmpDir) + '/apt-ftparchive-extras.conf\" | sed \'s/ARCH/' + self.altCdUbuntuArch + '/\' > \"' + os.path.join(self.customDir, self.tmpDir) + '/apt-ftparchive-extras.conf.tmp\"')
                    os.popen('cd \"' + os.path.join(self.customDir, self.tmpDir) + '\" ; mv apt-ftparchive-extras.conf.tmp apt-ftparchive-extras.conf ; rm -f apt-ftparchive-extras.conf.tmp')

                print _("Checking Indices...")
                if os.path.exists (os.path.join(self.customDir, self.tmpDir) + '/override.' + self.ubuntuCodename + '.main') == False:
                    print "Getting index: override." + self.ubuntuCodename + ".main ..."
                    os.popen('cd \"' + os.path.join(self.customDir, self.tmpDir) + '\" ; wget -nv http://archive.ubuntu.com/ubuntu/indices/override.' + self.ubuntuCodename + '.main')
                if os.path.exists (os.path.join(self.customDir, self.tmpDir) + '/override.' + self.ubuntuCodename + '.extra.main') == False:
                    print "Getting index: override." + self.ubuntuCodename + ".extra.main ..."
                    os.popen('cd \"' + os.path.join(self.customDir, self.tmpDir) + '\" ; wget -nv http://archive.ubuntu.com/ubuntu/indices/override.' + self.ubuntuCodename + '.extra.main')
                if os.path.exists (os.path.join(self.customDir, self.tmpDir) + '/override.' + self.ubuntuCodename + '.main.debian-installer') == False:
                    print "Getting index: override." + self.ubuntuCodename + ".main.debian-installer ..."
                    os.popen('cd \"' + os.path.join(self.customDir, self.tmpDir) + '\" ; wget -nv http://archive.ubuntu.com/ubuntu/indices/override.' + self.ubuntuCodename + '.main.debian-installer')

                # check for extra2.main override
                if os.path.exists(os.path.join(self.customDir, self.tmpDir) + '/override.' + self.ubuntuCodename + '.extra2.main') == False:
                    # create a 'fixed' version of extra.main override
                    print "Fixing index: override." + self.ubuntuCodename + ".extra.main ..."
                    os.popen('cd \"' + os.path.join(self.customDir, self.tmpDir) + '\" ; cat override.'+ self.ubuntuCodename + '.extra.main | egrep -v \' Task \' > override.' + self.ubuntuCodename + '.extra2.main')
                    os.popen('cd \"' + os.path.join(self.customDir, self.altRemasterDir) + '\" ; cat dists/' + self.ubuntuCodename + '/main/binary-' + self.altCdUbuntuArch + '/Packages | perl -e \'while (<>) { chomp; if(/^Package\:\s*(.+)$/) { $pkg=$1; } elsif(/^Task\:\s(.+)$/) { print \"$pkg\tTask\t$1\n\"; } }\' >> ' + os.path.join(self.customDir, self.tmpDir) + '/override.' + self.ubuntuCodename + '.extra2.main')

                # download ubuntu keyring
                # move old sources.list apt file
                print _("Backing up old apt config...")
                os.popen('mv -f /etc/apt/sources.list /etc/apt/sources.list.orig')
                os.popen('cp -Rf /var/cache/apt /var/cache/apt.orig')

                # remove old ubuntu-keyring
                print _("Removing existing ubuntu-keyring source...")
                os.popen('cd \"' + os.path.join(self.customDir, self.tmpDir) + '\" ; rm -Rf ubuntu-keyring*')

                # add deb-src to apt sources
                os.popen('echo deb-src http://us.archive.ubuntu.com/ubuntu ' + self.ubuntuCodename + ' main restricted > /etc/apt/sources.list')
                print _("Updating apt (apt-get update)...")
                os.popen('apt-get update')
                # download ubuntu-keyring for keyring generation
                print _("Getting Ubuntu Keyring source...")
                print(commands.getoutput('cd \"' + os.path.join(self.customDir, self.tmpDir) + '\" ; apt-get source ubuntu-keyring'))

                print _("Restoring original apt configuration...")
                os.popen('mv -f /etc/apt/sources.list.orig /etc/apt/sources.list')
                os.popen('rm -Rf /var/cache/apt')
                os.popen('mv -f /var/cache/apt.orig /var/cache/apt')
                os.popen('rm -Rf /var/cache/apt.orig')
                # update local system apt so user doesn't have to later
                os.popen('apt-get update')

                keyringDir = commands.getoutput('cd \"' + os.path.join(self.customDir, self.tmpDir) + '\" ; find * -maxdepth 1 -name "ubuntu-keyring*" -type d -print')
                # import ubuntu keyring
                print _("Importing Ubuntu Key...")
                os.popen('cd \"' + os.path.join(self.customDir, self.tmpDir) + '/' + keyringDir + '/keyrings\" ; gpg --import < ubuntu-archive-keyring.gpg > /dev/null ; rm -Rf ubuntu-archive-keyring.gpg > /dev/null')
                # reset permissions for user
                os.popen('chown -R ' + os.getlogin() + ' \"' + os.environ['HOME'] + '/.gnupg/\"')
                print _("Exporting new key...")
                os.popen('cd \"' + os.path.join(self.customDir, self.tmpDir) + '/' + keyringDir + '/keyrings\" ; gpg --output=ubuntu-archive-keyring.gpg --export \"Ubuntu CD Image Automatic Signing Key\" \"Ubuntu Archive Automatic Signing Key\" \"' + self.altGpgKeyName + '\" > /dev/null' )
                print _("Building new key package...")
                # TODO: somehow pass the gpg passphrase so it doesn't prompt...
                os.popen('cd \"' + os.path.join(self.customDir, self.tmpDir) + '/' + keyringDir + '\" ; dpkg-buildpackage -rfakeroot -m\"' + self.altGpgKeyName + '\" -k\"' + self.altGpgKeyName + '\" > /dev/null')
                # remove old ubuntu-keyring package
                print _("Removing old ubuntu keyring package...")
                os.popen('cd \"' + os.path.join(self.customDir, self.altRemasterDir) + '\" ; rm -Rf pool/main/u/ubuntu-keyring/*')
                # copy new keyring package
                print _("Copying new ubuntu keyring package...")
                os.popen('cd \"' + os.path.join(self.customDir, self.tmpDir) + '\" ; cp -Rf ubuntu-keyring*deb \"' + os.path.join(self.customDir, self.altRemasterDir) + '/pool/main/u/ubuntu-keyring/\"')

                # create apt package list
                print _("Generating package lists...")
                print("  deb...")
                os.popen('cd \"' + os.path.join(self.customDir, self.altRemasterDir) + '\" ; apt-ftparchive -c \"' + os.path.join(self.customDir, self.tmpDir) + '/apt.conf\" generate \"' + os.path.join(self.customDir, self.tmpDir) + '/apt-ftparchive-deb.conf\"')
                print("  udeb...")
                os.popen('cd \"' + os.path.join(self.customDir, self.altRemasterDir) + '\" ; apt-ftparchive -c \"' + os.path.join(self.customDir, self.tmpDir) + '/apt.conf\" generate \"' + os.path.join(self.customDir, self.tmpDir) + '/apt-ftparchive-udeb.conf\"')
                os.popen('cd \"' + os.path.join(self.customDir, self.altRemasterDir) + '\" ; cat dists/' + self.ubuntuCodename + '/main/binary-' + self.altCdUbuntuArch + '/Release | sed \'s/Component: main/Component: extras/\' > dists/' + self.ubuntuCodename + '/extras/binary-' + self.altCdUbuntuArch + '/Release')
                print("  extras...")
                os.popen('cd \"' + os.path.join(self.customDir, self.altRemasterDir) + '\" ; apt-ftparchive -c \"' + os.path.join(self.customDir, self.tmpDir) + '/apt.conf\" generate \"' + os.path.join(self.customDir, self.tmpDir) + '/apt-ftparchive-extras.conf\"')

                # remove existing release file
                print _("Removing current Release file...")
                os.popen('cd \"' + os.path.join(self.customDir, self.altRemasterDir) + '/dists/' + self.ubuntuCodename + '\" ; rm -Rf Release*')
                print _("Generating new Release file...")
                os.popen('cd \"' + os.path.join(self.customDir, self.altRemasterDir) + '\" ; apt-ftparchive -c \"' + os.path.join(self.customDir, self.tmpDir) + '/apt.conf\" release dists/' + self.ubuntuCodename + '/ > \"' + os.path.join(self.customDir, self.altRemasterDir) + '/dists/' + self.ubuntuCodename + '/Release\"')
                print _("GPG signing new Release file...")
                #os.popen('echo \"' + self.altGpgKeyPhrase + '\" | gpg --default-key \"' + self.altGpgKeyName + '\" --passphrase-fd 0 --output \"' + os.path.join(self.customDir, self.altRemasterDir) + '/dists/' + self.ubuntuCodename + '/Release.gpg\" -ba \"' + os.path.join(self.customDir, self.altRemasterDir) + '/dists/' + self.ubuntuCodename + '/Release\"')
                os.popen('gpg --default-key \"' + self.altGpgKeyName + '\" --output \"' + os.path.join(self.customDir, self.altRemasterDir) + '/dists/' + self.ubuntuCodename + '/Release.gpg\" -ba \"' + os.path.join(self.customDir, self.altRemasterDir) + '/dists/' + self.ubuntuCodename + '/Release\"')

                # build list for preseed
                # build regex
                r = re.compile(self.regexUbuntuAltPackages, re.IGNORECASE)
                # package list
                pkgs = ''
                fp = open(os.path.join(self.customDir, self.altRemasterDir) + '/dists/' + self.ubuntuCodename + '/extras/binary-' + self.altCdUbuntuArch + '/Packages', 'r')
                for l in fp:
                    if r.match(l) != None:
                        pkgs += r.match(l).group(1) + ' '
                fp.close()

                # find distribution, correct preseed file (for isolinux.cfg), and write preseed
                preseedMain = ''
                seedfile = ''
                if self.altCdUbuntuDist == 'Ubuntu':
                    print _("Creating preseed for Ubuntu...")
                    preseedMain = 'tasksel    tasksel/first    multiselect ubuntu-desktop\n'
                    seedfile = 'ubuntu.seed'
                elif self.altCdUbuntuDist == 'Kubuntu':
                    print _("Creating preseed for Kubuntu...")
                    preseedMain = 'tasksel    tasksel/first    multiselect kubuntu-desktop\n'
                    seedfile = 'kubuntu.seed'
                elif self.altCdUbuntuDist == 'Xubuntu':
                    print _("Creating preseed for Xubuntu...")
                    preseedMain = 'tasksel    tasksel/first    multiselect xubuntu-desktop\n'
                    seedfile = 'xubuntu.seed'
                elif self.altCdUbuntuDist == 'Ubuntu-Server':
                    print _("Creating preseed for Ubuntu-Server...")
                    preseedMain = 'd-i    base-installer/kernel/override-image    string linux-server\nd-i    pkgsel/language-pack-patterns    string\nd-i    pkgsel/install-language-support    boolean false\n'
                    seedfile = 'ubuntu-server.seed'
                else:
                    print _("Error: Unknown distribution. Skipping preseed creation...")
                # write preseed
                if preseedMain != '':
                    if os.path.exists(os.path.join(self.customDir, self.altRemasterDir) + '/preseed/custom.seed'):
                        # remove preseed
                        os.popen('rm -Rf \"' + os.path.join(self.customDir, self.altRemasterDir) + '/preseed/custom.seed\"')
                    fs = open(os.path.join(self.customDir, self.altRemasterDir) + '/preseed/custom.seed', 'w')
                    preseedMain += 'd-i pkgsel/include string ' + pkgs
                    fs.write(preseedMain)
                    fs.close
                # write custom isolinux.cfg
                if seedfile != '':
                    print _("Creating isolinux.cfg...")
                    os.popen('cd \"' + os.path.join(self.customDir, self.altRemasterDir) + '/isolinux/\" ; cat isolinux.cfg | sed \'s/' + seedfile + '/custom.seed/\' > isolinux.cfg.tmp ; mv isolinux.cfg.tmp isolinux.cfg')

        # no packages
        else:
            # no extra packages found
            print _("No extra packages found...")

        self.setDefaultCursor()
        print _("Finished customizing alternate install...")
        print " "
        # calculate iso size in the background
        gobject.idle_add(self.calculateAltIsoSize)
        #return False

# ---------- Build ---------- #
    def build(self):
        # check for custom mksquashfs (for multi-threading, new features, etc.)
        mksquashfs = ''
        if commands.getoutput('echo $MKSQUASHFS') != '':
            mksquashfs = commands.getoutput('echo $MKSQUASHFS')
            print 'Using alternative mksquashfs: ' + ' Version: ' + commands.getoutput(mksquashfs + ' -version')
        # setup build vars
        self.buildInitrd = self.wTree.get_widget("checkbuttonBuildInitrd").get_active()
        self.buildSquashRoot = self.wTree.get_widget("checkbuttonBuildSquashRoot").get_active()
        self.buildIso = self.wTree.get_widget("checkbuttonBuildIso").get_active()
        self.buildLiveCdFilename = self.wTree.get_widget("entryLiveIsoFilename").get_text()
        self.LiveCdDescription = "ubuntu-custom"
        self.LiveCdRemovePrograms = self.wTree.get_widget("checkbuttonLiveCdRemoveWin32Programs").get_active()
        self.LiveCdArch = self.wTree.get_widget("comboboxLiveCdArch").get_active_text()
        self.hfsMap = os.getcwd() + "/lib/hfs.map"

        print " "
        print _("INFO: Starting Build...")
        print " "
        # build initrd
        if self.buildInitrd == True:
            # create initrd
            if os.path.exists(os.path.join(self.customDir, "initrd")):
                print _("Creating Initrd...")
                os.popen('cd \"' + os.path.join(self.customDir, "initrd/") + '\"; find | cpio -H newc -o | gzip > ../initrd.gz' + '; mv -f ../initrd.gz \"' + os.path.join(self.customDir, "remaster/casper/initrd.gz") + '\"')

        # build squash root
        if self.buildSquashRoot == True:
            # create squashfs root
            if os.path.exists(os.path.join(self.customDir, "root")):
                print _("Creating SquashFS root...")
                print _("Updating File lists...")
                q = ' dpkg-query -W --showformat=\'${Package} ${Version}\n\' '
                os.popen('chroot \"' + os.path.join(self.customDir, "root/") + '\"' + q + ' > \"' + os.path.join(self.customDir, "remaster/casper/filesystem.manifest") + '\"' )
                os.popen('cp -f \"' + os.path.join(self.customDir, "remaster/casper/filesystem.manifest") + '\" \"' + os.path.join(self.customDir, "remaster/casper/filesystem.manifest-desktop") + '\"')
                # check for existing squashfs root
                if os.path.exists(os.path.join(self.customDir, "remaster/casper/filesystem.squashfs")):
                    print _("Removing existing SquashFS root...")
                    os.popen('rm -Rf \"' + os.path.join(self.customDir, "remaster/casper/filesystem.squashfs") + '\"')
                print _("Building SquashFS root...")
                # check for alternate mksquashfs
                if mksquashfs == '':
                    os.popen(self.timeCmd + ' mksquashfs \"' + os.path.join(self.customDir, "root/") + '\"' + ' \"' + os.path.join(self.customDir, "remaster/casper/filesystem.squashfs") + '\"')
                else:
                    os.popen(self.timeCmd + ' ' + mksquashfs + ' \"' + os.path.join(self.customDir, "root/") + '\"' + ' \"' + os.path.join(self.customDir, "remaster/casper/filesystem.squashfs") + '\"')

        # remove windows programs
        if self.LiveCdRemovePrograms == True:
            print _('Removing Win32 versions of Firefox, Thunderbird, etc. ...')
            os.popen('rm -Rf \"' + os.path.join(self.customDir, "remaster/bin") + '\"')
            os.popen('rm -Rf \"' + os.path.join(self.customDir, "remaster/programs") + '\"')
            os.popen('rm -Rf \"' + os.path.join(self.customDir, "remaster/autorun.inf") + '\"')
            os.popen('rm -Rf \"' + os.path.join(self.customDir, "remaster/start.ini") + '\"')
            os.popen('rm -Rf \"' + os.path.join(self.customDir, "remaster/start.exe") + '\"')
            os.popen('rm -Rf \"' + os.path.join(self.customDir, "remaster/start.bmp") + '\"')

        # build iso
        if self.buildIso == True:
            # create iso
            if os.path.exists(os.path.join(self.customDir, "remaster")):
                print _("Creating ISO...")
                # add disc id
                os.popen('echo \"Built by Reconstructor ' + self.appVersion + ' - Rev ' + self.updateId + ' (c) Reconstructor Team, 2006 - http://reconstructor.aperantis.com\" > \"' + os.path.join(self.customDir, "remaster/.disc_id") + '\"')
                # update md5
                print _("Updating md5 sums...")
                os.popen('cd \"' + os.path.join(self.customDir, "remaster/") + '\"; ' + 'find . -type f -print0 | xargs -0 md5sum > md5sum.txt')
                # remove existing iso
                if os.path.exists(self.buildLiveCdFilename):
                    print _("Removing existing ISO...")
                    os.popen('rm -Rf \"' + self.buildLiveCdFilename + '\"')
                # build
                # check for description - replace if necessary
                if self.wTree.get_widget("entryLiveCdDescription").get_text() != "":
                    self.LiveCdDescription = self.wTree.get_widget("entryLiveCdDescription").get_text()

                # build iso according to architecture
                if self.LiveCdArch == "x86":
                    print _("Building x86 ISO...")
                    os.popen(self.timeCmd + ' mkisofs -o \"' + self.buildLiveCdFilename + '\" -b \"isolinux/isolinux.bin\" -c \"isolinux/boot.cat\" -no-emul-boot -boot-load-size 4 -boot-info-table -V \"' + self.LiveCdDescription + '\" -cache-inodes -r -J -l \"' + os.path.join(self.customDir, "remaster") + '\"')
                elif self.LiveCdArch == "PowerPC":
                    print _("Building PowerPC ISO...")
                    os.popen(self.timeCmd + ' mkisofs  -r -V \"' + self.LiveCdDescription + '\" --netatalk -hfs -probe -map \"' + self.hfsMap + '\" -chrp-boot -iso-level 2 -part -no-desktop -hfs-bless ' + '\"' + os.path.join(self.customDir, "remaster/install") + '\" -o \"' + self.buildLiveCdFilename + '\" \"' + os.path.join(self.customDir, "remaster") + '\"')
                elif self.LiveCdArch == "x86_64":
                    print _("Building x86_64 ISO...")
                    os.popen(self.timeCmd + ' mkisofs -r -o \"' + self.buildLiveCdFilename + '\" -b \"isolinux/isolinux.bin\" -c \"isolinux/boot.cat\" -no-emul-boot -V \"' + self.LiveCdDescription + '\" -J -l \"' + os.path.join(self.customDir, "remaster") + '\"')

        self.setDefaultCursor()
        self.setPage(self.pageFinish)
        # print status message
        statusMsgFinish = _('     <b>Finished.</b>     ')
        statusMsgISO = _('      <b>Finished.</b> ISO located at: ')
        if os.path.exists(self.buildLiveCdFilename):
            print "ISO Located: " + self.buildLiveCdFilename
            self.wTree.get_widget("labelBuildComplete").set_text(statusMsgISO + self.buildLiveCdFilename + '     ')
            self.wTree.get_widget("labelBuildComplete").set_use_markup(True)
        else:
            self.wTree.get_widget("labelBuildComplete").set_text(statusMsgFinish)
            self.wTree.get_widget("labelBuildComplete").set_use_markup(True)
        # enable/disable iso burn
        self.checkEnableBurnIso()

        print "Build Complete..."

#---------- Build alternate disc ----------#
    def buildAlternate(self):
        # setup build vars
        self.buildAltInitrd = self.wTree.get_widget("checkbuttonAltBuildInitrd").get_active()
        self.buildAltIso = self.wTree.get_widget("checkbuttonAltBuildIso").get_active()
        self.buildAltCdFilename = self.wTree.get_widget("entryAltBuildIsoFilename").get_text()
        self.altCdDescription = "ubuntu-custom-alt"
        self.altCdArch = self.wTree.get_widget("comboboxAltBuildArch").get_active_text()
        self.hfsMap = os.getcwd() + "/lib/hfs.map"

        print " "
        print _("INFO: Starting Build...")
        print " "
        # build initrd
        if self.buildAltInitrd == True:
            # create initrd
            if os.path.exists(os.path.join(self.customDir, "initrd_alt")):
                print _("Creating Initrd...")
                os.popen('cd \"' + os.path.join(self.customDir, "initrd_alt/") + '\"; find | cpio -H newc -o | gzip > ../initrd.gz' + '; mv -f ../initrd.gz \"' + os.path.join(self.customDir, "remaster_alt/install/initrd.gz") + '\"')

        # build iso
        if self.buildAltIso == True:
            # create iso
            if os.path.exists(os.path.join(self.customDir, "remaster_alt")):
                print _("Creating ISO...")
                # add disc id
                os.popen('echo \"Built by Reconstructor ' + self.appVersion + ' - Rev ' + self.updateId + ' (c) Reconstructor Team, 2006 - http://reconstructor.aperantis.com\" > \"' + os.path.join(self.customDir, "remaster/.disc_id") + '\"')
                # update md5
                print _("Updating md5 sums...")
                os.popen('cd \"' + os.path.join(self.customDir, "remaster_alt/") + '\"; ' + 'find . -type f -print0 | xargs -0 md5sum > md5sum.txt')
                # remove existing iso
                if os.path.exists(self.buildAltCdFilename):
                    print _("Removing existing ISO...")
                    os.popen('rm -Rf \"' + self.buildAltCdFilename + '\"')
                # build
                # check for description - replace if necessary
                if self.wTree.get_widget("entryBuildAltCdDescription").get_text() != "":
                    self.altCdDescription = self.wTree.get_widget("entryBuildAltCdDescription").get_text()

                # build iso according to architecture
                if self.altCdArch == "x86":
                    print _("Building x86 ISO...")
                    os.popen(self.timeCmd + ' mkisofs -o \"' + self.buildAltCdFilename + '\" -b \"isolinux/isolinux.bin\" -c \"isolinux/boot.cat\" -no-emul-boot -boot-load-size 4 -boot-info-table -V \"' + self.altCdDescription + '\" -cache-inodes -r -J -l \"' + os.path.join(self.customDir, "remaster_alt") + '\"')
                elif self.altCdArch == "PowerPC":
                    print _("Building PowerPC ISO...")
                    os.popen(self.timeCmd + ' mkisofs  -r -V \"' + self.altCdDescription + '\" --netatalk -hfs -probe -map \"' + self.hfsMap + '\" -chrp-boot -iso-level 2 -part -no-desktop -hfs-bless ' + '\"' + os.path.join(self.customDir, "remaster_alt/install") + '\" -o \"' + self.buildAltCdFilename + '\" \"' + os.path.join(self.customDir, "remaster_alt") + '\"')
                elif self.altCdArch == "x86_64":
                    print _("Building x86_64 ISO...")
                    os.popen(self.timeCmd + ' mkisofs -r -o \"' + self.buildAltCdFilename + '\" -b \"isolinux/isolinux.bin\" -c \"isolinux/boot.cat\" -no-emul-boot -V \"' + self.altCdDescription + '\" -J -l \"' + os.path.join(self.customDir, "remaster_alt") + '\"')

        self.setDefaultCursor()
        self.setPage(self.pageFinish)
        # print status message
        statusMsgFinish = _('     <b>Finished.</b>     ')
        statusMsgISO = _('      <b>Finished.</b> ISO located at: ')
        if os.path.exists(self.buildAltCdFilename):
            print "ISO Located: " + self.buildAltCdFilename
            self.wTree.get_widget("labelBuildComplete").set_text(statusMsgISO + self.buildAltCdFilename + '     ')
            self.wTree.get_widget("labelBuildComplete").set_use_markup(True)
        else:
            self.wTree.get_widget("labelBuildComplete").set_text(statusMsgFinish)
            self.wTree.get_widget("labelBuildComplete").set_use_markup(True)
        # enable/disable iso burn
        self.checkEnableBurnAltIso()

        print "Build Complete..."


class AltPackageHelper:
    """AltPackageHelper - .deb package helper..."""
    def __init__(self):
        # package lists
        # ubuntu Minimal Packages - base system
        self.ubuntuMinimalPackages = ('adduser', 'alsa-base', 'alsa-utils', 'apt', 'apt-utils', 'aptitude',
                                    'base-files', 'base-passwd', 'bash', 'bsdutils', 'bzip2', 'console-setup',
                                    'console-tools', 'coreutils', 'dash', 'debconf', 'debianutils',
                                    'dhcp3-client', 'diff', 'dpkg', 'e2fsprogs', 'eject', 'ethtool',
                                    'findutils', 'gettext-base', 'gnupg', 'grep', 'gzip', 'hostname',
                                    'ifupdown', 'initramfs-tools', 'iproute', 'iputils-ping', 'less',
                                    'libc6-i686', 'libfribidi0', 'locales', 'login', 'lsb-release', 'makedev',
                                    'mawk', 'mii-diag', 'mktemp', 'module-init-tools', 'mount', 'ncurses-base',
                                    'ncurses-bin', 'net-tools', 'netbase', 'netcat', 'ntpdate', 'passwd',
                                    'pciutils', 'pcmciautils', 'perl-base', 'procps', 'python',
                                    'python-minimal', 'sed', 'startup-tasks', 'sudo', 'sysklogd',
                                    'system-services', 'tar', 'tasksel', 'zdata', 'ubuntu-keyring', 'udev',
                                    'upstart', 'upstart-compat-sysv', 'upstart-logd', 'usbutils', 'til-linux',
                                    'util-linux-locales', 'vim-tiny', 'wireless-tools', 'wpasupplicant')

        # ubuntu Standard Packages - comfortable cli system
        self.ubuntuStandardPackages = ('at', 'cpio', 'cron', 'dmidecode', 'dnsutils', 'dosfstools', 'dselect',
                                     'ed', 'fdutils', 'file', 'ftp', 'hdparm', 'info', 'inputattach',
                                     'iptables', 'iputils-arping', 'iputils-tracepath', 'logrotate', 'lshw',
                                     'lsof', 'ltrace', 'man-db', 'manpages', 'memtest86+', 'mime-support',
                                     'nano', 'parted', 'popularity-contest', 'ppp', 'pppconfig', 'pppoeconf',
                                     'psmisc', 'reiserfsprogs', 'rsync', 'strace', 'tcpdump', 'telnet', 'time',
                                     'w3m', 'wget')

        # ubuntu Server Packages - LAMP server
        self.ubuntuServerPackages = ('')
        # ubuntu Desktop Packages - default desktop system
        self.ubuntuDesktopPackages = ('acpi', 'acpi-support', 'acpid', 'alacarte', 'anacron', 'apmd',
                                    'apport-gtk', 'avahi-daemon', 'bc', 'bug-buddy', 'cdparanoia', 'cdrecord',
                                    'contact-lookup-applet', 'cupsys', 'cupsys-bsd', 'cupsys-client',
                                    'cupsys-driver-gutenprint', 'dc', 'deskbar-applet', 'desktop-file-utils',
                                    'diveintopython', 'doc-base', 'dvd+rw-tools', 'ekiga', 'eog', 'esound',
                                    'evince', 'evolution', 'evolution-exchange', 'evolution-plugins',
                                    'evolution-webcal', 'f-spot', 'file-roller', 'firefox',
                                    'firefox-gnome-support', 'foo2zjs', 'foomatic-db', 'foomatic-db-engine',
                                    'foomatic-db-hpijs', 'foomatic-filters', 'fortune-mod', 'gaim',
                                    'gcalctool', 'gconf-editor', 'gdebi', 'gdm', 'gedit', 'gimp', 'gimp-print',
                                    'gimp-python', 'gnome-about', 'gnome-app-install', 'gnome-applets',
                                    'gnome-btdownload', 'gnome-control-center', 'gnome-cups-manager',
                                    'gnome-icon-theme', 'gnome-keyring-manager', 'gnome-media', 'gnome-menus',
                                    'gnome-netstatus-applet', 'gnome-nettool', 'gnome-panel',
                                    'gnome-pilot-conduits', 'gnome-power-manager', 'gnome-session',
                                    'gnome-spell', 'gnome-system-monitor', 'gnome-system-tools',
                                    'gnome-terminal', 'gnome-themes', 'gnome-utils', 'gnome-volume-manager',
                                    'gnome2-user-guide', 'gs-esp', 'gstreamer0.10-alsa', 'gstreamer0.10-esd',
                                    'gstreamer0.10-plugins-base-apps', 'gthumb', 'gtk2-engines', 'gucharmap',
                                    'hal', 'hal-device-manager', 'hotkey-setup', 'hwdb-client-gnome',
                                    'landscape-client', 'language-selector', 'lftp', 'libgl1-mesa-glx',
                                    'libglut3', 'libgnome2-perl', 'libgnomevfs2-bin', 'libgnomevfs2-extra',
                                    'libpam-foreground', 'libpt-plugins-v4l', 'libpt-plugins-v4l2',
                                    'libsasl2-modules', 'libstdc++5', 'libxp6', 'metacity', 'min12xxw',
                                    'mkisofs', 'nautilus', 'nautilus-cd-burner', 'nautilus-sendto',
                                    'notification-daemon', 'openoffice.org', 'openoffice.org-evolution',
                                    'openoffice.org-gnome', 'pnm2ppa', 'powermanagement-interface',
                                    'readahead', 'rhythmbox', 'rss-glx', 'screen', 'screensaver-default-images',
                                    'scrollkeeper', 'serpentine', 'slocate', 'smbclient', 'sound-juicer',
                                    'ssh-askpass-gnome', 'synaptic', 'tangerine-icon-theme', 'tango-icon-theme',
                                    'tango-icon-theme-common', 'tomboy', 'totem', 'totem-mozilla', 'tsclient',
                                    'ttf-bitstream-vera', 'ttf-dejavu', 'ttf-freefont', 'ubuntu-artwork',
                                    'ubuntu-docs', 'ubuntu-sounds', 'unzip', 'update-notifier', 'usplash',
                                    'usplash-theme-ubuntu', 'vino', 'wvdial', 'x-ttcidfont-conf',
                                    'xkeyboard-config', 'xorg', 'xsane', 'xscreensaver-data', 'xscreensaver-gl',
                                    'xterm', 'xvncviewer', 'yelp', 'zenity', 'zip')



    def copyPackages(self, packageList, sourcePath, destinationPath):
        for package in packageList:
            print "Copying " + package + "..."
            os.popen("rsync -a --del --prune-empty-dirs --filter=\"+ */\" --filter=\"+ /**/" + package + "_*.deb\" --filter=\"- *\" " + sourcePath + " " + destinationPath)

# ---------- MAIN ----------

if __name__ == "__main__":
    APPDOMAIN='reconstructor'
    LANGDIR='lang'
    # locale
    locale.setlocale(locale.LC_ALL, '')
    gettext.bindtextdomain(APPDOMAIN, LANGDIR)
    gtk.glade.bindtextdomain(APPDOMAIN, LANGDIR)
    gtk.glade.textdomain(APPDOMAIN)
    gettext.textdomain(APPDOMAIN)
    gettext.install(APPDOMAIN, LANGDIR, unicode=1)

    # check credentials
    if os.getuid() != 0 :
        ## show non-root privledge error
        warnDlg = gtk.Dialog(title="Reconstructor", parent=None, flags=0, buttons=(gtk.STOCK_OK, gtk.RESPONSE_OK))
        warnDlg.set_icon_from_file('glade/app.png')
        warnDlg.vbox.set_spacing(10)
        labelSpc = gtk.Label(" ")
        warnDlg.vbox.pack_start(labelSpc)
        labelSpc.show()
        warnText = _("  <b>You must run with root privledges.</b>")
        infoText = _("Open a Terminal, change to the directory with reconstructor, \nand type <b>sudo python reconstructor.py</b>  ")
        label = gtk.Label(warnText)
        lblInfo = gtk.Label(infoText)
        label.set_use_markup(True)
        lblInfo.set_use_markup(True)
        warnDlg.vbox.pack_start(label)
        warnDlg.vbox.pack_start(lblInfo)
        label.show()
        lblInfo.show()
        response = warnDlg.run()
        if response == gtk.RESPONSE_OK :
            warnDlg.destroy()
            #gtk.main_quit()
            sys.exit(0)
        # use gksu to open -- HIDES TERMINAL
        #os.popen('gksu ' + os.getcwd() + '/reconstructor.py')
        #gtk.main_quit()
        #sys.exit(0)
    else :
        rec = Reconstructor()
        # run gui
        gtk.main()
