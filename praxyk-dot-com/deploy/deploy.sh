#!/bin/bash

# @author John Allard, Nick Corgan, others
# @github https://github.com/Praxyk/praxyk

# this script takes the website code and deploys it 
# under an apache server on port 80.

echo "Deploying Praxyk Web Server"

WEB_DEPLOY_DIR=$CWD

xargs sudo apt-get -y install < .ubuntu_install

RETVAL=$?
[ $RETVAL -eq 0 ] && echo "  Web-Deploy : Ubuntu Requirements Install Success"
[ $RETVAL -ne 0 ] && echo "  Web-Deploy : Ubuntu Requirements Install Failure" && exit 1

sudo a2enmod wsgi 

RETVAL=$?
[ $RETVAL -eq 0 ] && echo "  Web-Deploy : Apache WSGI Enabled"
[ $RETVAL -ne 0 ] && echo "  Web-Deploy : Apache WSGI Failure" && exit 1

$SERVER_IP=$(ifconfig eth0 | grep inet | awk '{ print $2 }')

sudo mkdir -p /var/www/praxyk_web_server/
sudo cp web_server.wsgi /var/www/praxyk_web_server/
sudo cp praxyk.com.conf /etc/apache2/sites-available/praxyk.com.conf

cd ~
rm -rf praxyk-website-live
cp -R praxyk-website praxyk-website-live
cd $WEB_DEPLOY_DIR

sudo service apache2 restart

sudo a2dissite 000-default.conf
sudo a2ensite praxyk.com.conf

sudo service apache2 restart

RETVAL=$?
[ $RETVAL -eq 0 ] && echo "  Web-Deploy : Apache Site Started"
[ $RETVAL -ne 0 ] && echo "  Web-Deploy : Apache Site Start Failure" && exit 1


exit 0
