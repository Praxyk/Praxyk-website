#!/bin/bash

rm -rf app/templates/praxyk-wiki-html
cp -R praxyk_wiki_html app/templates/praxyk-wiki-html
cp app/templates/praxyk-wiki-html/assets/css/* app/static/assets/css
cd app/templates/praxyk-wiki-html
sed 's/assets/\/static\/assets/' Praxyk-API.html > Praxyk-API2.html
mv Praxyk-API2.html Praxyk-API.html
rm app/static/assets/style.css

