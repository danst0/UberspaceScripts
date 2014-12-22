#!/usr/bin/env python2.7
# -*- coding: utf8 -*- 

import mailbox
import email
import os
import shutil
import datetime
import re
from subprocess import call

now = datetime.datetime.now()


tmp_dir = '/home/ddumke/.tmp/'
blog_dir = '/var/www/virtual/ddumke/html/kirbycms/content/01-schnipsel/'

valid_senders = ['daniel@dumke.me', 'daniel.dumke@eon.com', 'may@dumke.me']

valid_recievers = [('delivered-to', 'ddumke-tumblr@dumke.me'), ('to', 'tumblr@dumke.me') ]

photo_extensions = ['.jpg', '.jpeg', '.png']

video_extensions = ['.mov']

month = ['jan', 'feb', 'mar', 'apr', 'mai', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dez']



def strip_enter(text):
    if text != None:
        for i in range(4):
            text = text.strip('\n')
            text = text.strip('\r')
    return text

def decode_message(message):
    body = None
    html = None
    attachments = []
    for part in message.walk():

        ctype = part.get_content_type()
#         print ctype
        if ctype == "text/plain":
            if body is None:
                body = ''
            encoding = part.get_content_charset()
            if encoding == None:
                encoding = 'ascii'
            body += unicode(part.get_payload(decode=True),
                encoding,'replace').encode('utf8','replace')
        elif ctype == "text/html":
            if html is None:
                html = ''
            encoding = part.get_content_charset()
            if encoding == None:
                encoding = 'ascii'
            html += unicode(part.get_payload(decode=True),
                encoding,'replace').encode('utf8','replace')
        elif ctype in ['image/jpeg', 'image/jpg', 'image/png']:
            filename = part.get_filename()
            if not check_extenstions([filename], photo_extensions):
                if ctype in ['image/jpeg', 'image/jpg']:
                    filename = filename + '.jpg'
                elif ctype in ['image/png']:
                    filename = filename + '.png'
            open(tmp_dir + filename, 'wb').write(part.get_payload(decode=True))
            attachments.append(filename)
        elif ctype in ['video/quicktime', 'application/octet-stream']:
            open(tmp_dir + part.get_filename(), 'wb').write(part.get_payload(decode=True))
            attachments.append(part.get_filename())
        elif ctype in ['multipart/mixed']:
            pass
        else:
            print 'Unrecognized content type:', ctype
    strip_enter(body)
    strip_enter(html)
    if body == None and html != None:
        return html, attachments
    elif body != None and html == None:
        return body, attachments
    elif body == None and html == None:
        return '', attachments
    elif body != None and html != None:
        return '', attachments

def replace_directory(dir):
    dir = dir.lower()
    dir = dir.replace('“', '"')
    dir = dir.replace('”', '"')
    dir = dir.replace('…', '...')
    dir = dir.replace('ä', 'ae')
    dir = dir.replace('ö', 'oe')
    dir = dir.replace('ü', 'ue')
    dir = dir.replace('ß', 'ss')         
    dir = re.sub('[^A-Za-z0-9\-\s]+', '', dir)
    dir = re.sub(' ', '-', dir)
    for i in range(3):
        dir = dir.replace('--', '-')
        dir = dir.strip('-')
    return dir


def check_extenstions(attachments, valid_ext):
    found = False
#     print attachments, valid_ext
    for attach in attachments:
        for ext in valid_ext:
            if attach.lower().find(ext) != -1:
                found = True
                break
    return found

def extract_tags(title):
    tags = []
    pos_hash = title.find('#')
#     print title
    while pos_hash != -1:
        pos_space = title.find(' ', pos_hash)
        if pos_space == -1:
            pos_space = len(title)
#         print pos_hash, pos_space, title[pos_hash + 1:pos_space], ':'
        tags.append(title[pos_hash + 1:pos_space].strip())
        title = title[:pos_hash] + title[pos_space+1:]
        pos_hash = title.find('#')
    return title.strip(), tags    
def make_post(title, text, attachments):
    success = False
    now = datetime.datetime.now()
    new_dir = blog_dir + str(now.year) + str(now.month).zfill(2) + '-' +  month[int(now.month) - 1] + '-' + str(now.year) + '/'
#     print new_dir
    if not os.path.exists(new_dir):
        os.makedirs(new_dir)
    last_blog = 0
    for dir in os.listdir(new_dir):
        if os.path.isdir(new_dir + dir):
            try:
                tmp_last_blog = int(dir[:2])
            except:
                tmp_last_blog = 0
            if tmp_last_blog > last_blog:
                last_blog = tmp_last_blog
    title, tags = extract_tags(title)
    tag_line = ''
    for tag in tags:
        tag_line += ', ' + tag
#     print 'tag_line', tag_line
    new_dir = new_dir + str(last_blog + 1).zfill(2) + '-' + replace_directory(title) + '/'
    

    if attachments != [] and check_extenstions(attachments, photo_extensions):
        print 'Creating', new_dir
        os.makedirs(new_dir)
        for file in attachments:
            call(['/home/ddumke/.toast/armed/bin/jhead', '-autorot', tmp_dir + file])
            shutil.move(tmp_dir + file, new_dir)
        f = open(new_dir + '/article.photo.txt', 'w')
        f.write('Title: ' + title + '\n')
        f.write('----\n')
        f.write('Date: ' + (str(now.day) + '.' + str(now.month) + '.' + str(now.year)).encode('utf8') + '\n')
        f.write('----\n')
        f.write('Text: ' + text.encode('utf8') + '\n')
        f.write('----\n')
        f.write('Tags: photo' + tag_line + '\n')
        f.write('----\n')
        f.close()
        success = True
    elif attachments != [] and check_extenstions(attachments, video_extensions):
        print 'Creating', new_dir
        os.makedirs(new_dir)
        shutil.move(tmp_dir + attachments[0], new_dir)
        fileName, fileExtension = os.path.splitext(attachments[0])
        f = open(new_dir + '/article.video.txt', 'w')
        f.write('Title: ' + title + '\n')
        f.write('----\n')
        f.write('Date: ' + (str(now.day) + '.' + str(now.month) + '.' + str(now.year)).encode('utf8') + '\n')
        f.write('----\n')
        sublime_line = '(sublime: ' + fileName + ' width: 510 height: 288 name: ' + title + ' uid: ' + title + ')'
        f.write('Text: ' + '' + '\n')
        f.write('----\n')
        f.write('Video: ' + sublime_line + '\n')
        f.write('----\n')
        f.write('Tags: video' + tag_line + '\n')
        f.write('----\n')
        f.close()
        success = True
    elif text.find('Link: ') != -1:
        print 'Creating', new_dir
        os.makedirs(new_dir)
        f = open(new_dir + '/article.link.txt', 'w')
        f.write('Title: ' + title + '\n')
        f.write('----\n')
        f.write('Date: ' + (str(now.day) + '.' + str(now.month) + '.' + str(now.year)).encode('utf8') + '\n')
        f.write('----\n')
        f.write(text.encode('utf8') + '\n')
        if text[-8:].find('----') == -1:
            f.write('----\n')
        f.write('Tags: link' + tag_line + '\n')
        f.write('----\n')
        f.close()
        success = True
    # other link
    elif text.find('\n', 1) == -1 and (text.find('http://') != -1 or text.find('https://') != -1):
        print 'Creating', new_dir
        os.makedirs(new_dir)
        f = open(new_dir + '/article.link.txt', 'w')
        f.write('Title: ' + title + '\n')
        f.write('----\n')
        f.write('Date: ' + (str(now.day) + '.' + str(now.month) + '.' + str(now.year)).encode('utf8') + '\n')
        f.write('----\n')
        f.write('Link: ' + text.encode('utf8').strip('/n').strip() +'\n')
        f.write('----\n')
        f.write('LinkTitle: ' + title + '\n')
        f.write('----\n')
        f.write('Tags: link' + tag_line + '\n')
        f.write('----\n')
        f.close()
        success = True
    return success
        
#     link, photo, quote, text

def check_from_mail(addr):
    valid = False
    for sender in valid_senders:
        if addr.find(sender) != -1:
            valid = True
            break
    return valid
        

def check_to_mail(message):
    valid = False
    for field, rec in valid_recievers:
        if field in [x.lower() for x in message.keys()]:
            if message[field].find(rec) != -1:
                valid = True
                break
    return valid

if __name__ == '__main__':
    mb = mailbox.Maildir('~/users/daniel', email.message_from_file)
    if os.path.exists(tmp_dir):
        shutil.rmtree(tmp_dir)
    os.makedirs(tmp_dir)
    to_remove = []
    for key, message in mb.iteritems():
    #     print message.keys()
        from_line = message['from']
        to_line = message['to']
        subject = email.header.decode_header(message['subject'])
#         print subject[0]
        encoding = subject[0][1]
        if subject[0][1] == None:
            encoding = 'ascii'
        print key        
        print "::", subject[0][0],"::"
        title = unicode(subject[0][0], encoding,'replace').encode('utf8','replace')
#         print message.keys()
#         raw_input()
        if  (check_from_mail(from_line) and check_to_mail(message)):
            text, attachments = decode_message(message)
            print 'Subject', title
            print 'Text:', text, '::'
            print 'Attachments:', attachments
            if make_post(title, text, attachments):
                to_remove.append(key)
    for key in to_remove:
        mb.remove(key)
