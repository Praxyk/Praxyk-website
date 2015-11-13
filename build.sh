#!/bin/bash

# @author John Allard, Nick Corgan, others
# @github https://github.com/Praxyk/praxyk

# this script simply compiles any documentation needed by the project,
# right now that just means compiling the wiki markdown to html

sudo npm install -g markdown-styles
xargs sudo apt-get -y install < .ubuntu_install

RETVAL=$?
[ $RETVAL -eq 0 ] && echo "  Docs : Ubuntu Requirements Install Success"
[ $RETVAL -ne 0 ] && echo "  Docs : Ubuntu Requirements Install Failure" && exit 1


sudo pip install -r .pip_install

RETVAL=$?
[ $RETVAL -eq 0 ] && echo "  Docs : Pip Requirements Install Success"
[ $RETVAL -ne 0 ] && echo "  Docs : Pip  Requirements Install Failure" && exit 1

cd praxyk-dot-com
./update_wiki.sh
./compile_wiki.sh

RETVAL=$?
[ $RETVAL -eq 0 ] && echo "  Docs : Wiki Compile to HTML Success"
[ $RETVAL -ne 0 ] && echo "  Docs : Wiki Compile to HTML Failure" && exit 1

rm -rf app/templates/praxyk-wiki-html
cp -R praxyk_wiki_html app/templates/praxyk-wiki-html
cp app/templates/praxyk-wiki-html/assets/css/* app/static/assets/css
cd app/templates/praxyk-wiki-html
sed 's/assets/\/static\/assets/' Praxyk-API.html > Praxyk-API2.html
mv Praxyk-API2.html Praxyk-API.html

exit 0



