#!/usr/bin/env python
# encoding: utf-8

import sys
from PIL import Image
numdic={189:'7',274:'3',33:'-',146:'1',242:'2',220:'4',116:'+',320:'9',317:'9',315:'0',190:'7',319:'6',273:'3',281:'5',280:'5',318:'9',145:'1',}
def attrcode(im):
    """calculate attribute code of character

    :im: image of single character
    :returns: attribute code

    """
    i_w , i_h = im.size
    count = 0
    for w in xrange(i_w):
        for h in xrange(i_h):
            if im.getpixel((w,h)) == 0:
                count += 1
    return count
def splitimg(img):
    """split img to single character

    :img: image
    :returns: string of result,renturn False when failed

    """
    res = ""
    img_w ,img_h = img.size
    flag = False
    numimg = []
    splitlist = [[],[]]
    for x in xrange(img_w):
        flag_line = False
        for  y in xrange(img_h):
            if img.getpixel((x,y))!= 255:
                flag_line=True
                if flag == False:
                    flag = True
                    splitlist[0].append(x)
            elif y==img_h-1 and flag_line==False and flag:
                splitlist[1].append(x)
                flag = True
                flag = False
    for index in xrange(len(splitlist[0])):
        numimg.append(img.crop((splitlist[0][index],0,splitlist[1][index],img_h)))
        code = attrcode(numimg[index])
        if code in numdic:
            res+=numdic[code]
        else:
            return False
    return res

def procimg(img):
    """process image

    :img: path to image file
    :returns: result in string
              return False when failed

    """
    im = Image.open(img).convert("1")
    res = splitimg(im)
    im.close();
    return res

def main(argv):
    if len(argv)!=2 :
        print len(argv),argv
        print "Usage:python2",argv[0],"<image file>"
        print "or:",argv[0],"<image file>"
        exit()
    res =  procimg(argv[-1])
    if res:
        print res
    else:
        print "failed"

if __name__ == "__main__":
    main(sys.argv)
