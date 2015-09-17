#!/bin/bash

cd /var/www/virtual/ddumke/html/scrmblog.com/
echo "RM everything but sites, .htacces, temp, robots.txt, humans.txt, ok?"
ls | grep -v '(sites|human.txt|robots.txt|.htaccess)'

read

ls | grep -v '(sites|human.txt|robots.txt|.htaccess)' | xargs rm

echo "Move .htaccess to htaccess.old.txt"
mv .htaccess htaccess.old.txt

cd /var/www/virtual/ddumke/html

wget http://drupal.org/files/projects/drupal-7.34.tar.gz
tar -zxvf drupal-7.34.tar.gz



cp -R drupal-7.34/* drupal-7.34/.htaccess scrmblog.com/

echo "Copy new .htaccess to htaccess.new.txt"
cd /var/www/virtual/ddumke/html/scrmblog.com/
cp .htaccess htaccess.new.txt

echo "Please go to http://scrmblog.com/update.php, to finalize the update"
