#!/usr/bin/env python
# encoding: utf-8

from __future__ import division
import sys
from PIL import Image
numdic={0.32:'4',0.52:'1',0.09:'-',0.44:'5',0.5:'9/6/8',0.17:'+',0.38:'2',0.3:'7',0.49:'0',0.43:'3'}
def attrcode(im):
    """calculate attribute code of character

    :im: image of single character
    :returns: attribute code

    """
    i_w , i_h = im.size
    count = 0
    for w in range(i_w):
        for h in range(i_h):
            if im.getpixel((w,h)) == 0:
                count += 1
    return round(count/(i_w*i_h), 2)
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
    for x in range(img_w):
        flag_line = False
        for  y in range(img_h):
            if img.getpixel((x,y))!= 255:
                flag_line=True
                if flag == False:
                    flag = True
                    splitlist[0].append(x)
            elif y==img_h-1 and flag_line==False and flag:
                splitlist[1].append(x)
                flag = True
                flag = False
    for index in range(len(splitlist[0])):
        numimg.append(img.crop((splitlist[0][index],0,splitlist[1][index],img_h)))
        code = attrcode(numimg[index])
        if code in numdic:
            if numdic[code] == '9/6/8':
                if numimg[index].getpixel((1,26))!=0 and numimg[index].getpixel((2,26))!=0 and numimg[index].getpixel((3,26))!=0:
                    res += '9'
                elif numimg[index].getpixel((15,16))!=0 and numimg[index].getpixel((14,16))!=0 and numimg[index].getpixel((13,16))!=0:
                    res += '6'
                else:
                    res += '8'
            else:
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
    im.close()
    return res

def main(argv):
    if len(argv)!=2 :
        print("Usage:python2",argv[0],"<image file>")
        print("or:",argv[0],"<image file>")
        exit()
    res =  procimg(argv[-1])
    if res:
        print(res)
    else:
        print("failed")

if __name__ == "__main__":
    main(sys.argv)
