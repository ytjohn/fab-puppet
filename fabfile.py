from fabric.api import run, env
from fabric.api import cd
from fabric.api import sudo
from fabric.api import settings, hide
import re

settings(hide('warnings', 'running', 'stdout', 'stderr'), warn_only=True)

def addrepo():
   release = getrelease()
   os = release['os']

   if os == 'Ubuntu' or os == 'Debian':
       # need to silence output again
       repo = 'apt.puppetlabs.com'
       deb = 'puppetlabs-release-%s.deb' % release['codename']
       source = 'http://%s/%s' % (repo, deb)
       run('wget %s -O /tmp/%s' % (source, deb))
           
       if run('sudo dpkg -i /tmp/%s' % deb): 
           run('rm /tmp/%s' % deb)
           run('sudo apt-get update')
       else:
           print "install failed"

   elif os == 'CentOS' or os == 'RHEL':
       if release['version'] >= 5:
           pass
       else:
           print "%s version %s unsupported" % (os, release['version'])
   else:
       print "Unsupported OS %s" %releas['os']


def installagent():
    release = getrelease()
    os = release['os']
     
    if os == 'Ubuntu' or os == 'Debian':
        run('sudo apt-get -y install puppet')
    elif os == 'RHEL' or os == 'CentOS':
        # http://docs.puppetlabs.com/guides/puppetlabs_package_repositories.html#for-red-hat-enterprise-linux-and-derivatives
        # http://yum.puppetlabs.com/el/6/products/x86_64/puppetlabs-release-6-1.noarch.rpm
        # http://yum.puppetlabs.com/el/5/products/x86_64/puppetlabs-release-5-6.noarch.rpm
        # http://yum.puppetlabs.com/el/<major>products/<arch>/puppetlabs-release-<major>-<minor>.noarch.rpm
        # need to think about this
        pass         
 
def enableagent():
    release = getrelease()
    os = release['os']

    if os == 'Ubuntu' or os == 'Debian':
        run('sudo sed -i s/START=no/START=yes/ /etc/default/puppet')
        run('sudo /etc/init.d/puppet start')

def disableagent():
    release = getrelease()
    os = release['os']

    if os == 'Ubuntu' or os == 'Debian':
        run('sudo sed -i s/START=yes/START=no/ /etc/default/puppet')
        run('sudo /etc/init.d/puppet stop')

def setserver(server):
    print server
    release = getrelease()
    os = release['os']

    checkserver = 'grep -q server /etc/puppet/puppet.conf'
    modify = 'sed -i s/server=.*/server=test/ puppet.conf'
    checkagent = 'grep -q "[agent]" /etc/puppet/puppet.conf' 

    results = sudo(checkserver)

#        # server line exists, just modify
#        run(modify)
#    else:
#        # line doesn't exist, add it
#        # check for agent section
#        if run(checkagent):
#            print "agent section found"
#        else:
#            print "agent section not found"
# 
    
    
def installmaster():
    release = getrelease()
    os = release['os']

    if os == 'Ubuntu' or os == 'Debian':
        run('sudo apt-get -y install puppetmaster')

def getrelease():
    with settings(
	hide('warnings', 'running', 'stdout', 'stderr'),
	warn_only=True
    ):
        out = run('cat /etc/*-release')
       
    release = {}
 
    if out.find('Ubuntu') != -1:
        #DISTRIB_ID=Ubuntu
        #DISTRIB_RELEASE=12.04
        #DISTRIB_CODENAME=precise
        #DISTRIB_DESCRIPTION="Ubuntu 12.04.1 LTS"
	release['os'] = 'Ubuntu'
        
        for line in out.splitlines():
            (k,s,v) = line.partition('=')
            if k == 'DISTRIB_RELEASE':
                release['version'] = v
            if k == 'DISTRIB_CODENAME':
                release['codename'] = v

    elif out.find('Red Hat Enterprise Linux') != -1:
        # Red Hat Enterprise Linux ES release 3 (Taroon Update 4)
        # Red Hat doesn't use code names, but we'll fake it.
        # Need to get the major (3, 4, 5, 6) and the Update version
        release['os'] = 'RHEL'
        m = re.search(r"release (?P<version>\d+) \((?P<codename>\w+).*(?P<minor>\d+)\)", out)
        release['version'] = m.group('version')
        release['codename'] = m.group('codename')
        release['minor'] = m.group('minor')

    elif out.find('CentOS') != -1:
        # CentOS release 6.2 (Final)
        # CentOS has several files, so you end up with three lines
        # Also, centos doesn't use codenames like Ubuntu does.
        # Need the major (
        release['os'] = 'CentOS'
        for line in out.splitlines():
            m = re.search(r"release (?P<version>\d+).(?P<minor>\d+) \((?P<codename>.*)\)", line)
            release['version'] = m.group('version')
            release['codename'] = m.group('codename') 
            release['minor'] = m.group('minor')

    else:
        release['os']  = 'Unknown %s' % out

    return release
    
    
