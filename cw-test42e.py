# cw-test42d.py:
# \ctxf works, but only for one argument
#
# cw-test42e.py:
# \ctxf works for multiple arguments 

import unicodedata
from fonttable import readn2  # new 

usefont=[]                                   #new 2016_0129   function for searching fonts
usefontname=[]
def searchfont(fname,fontno):  
    fno=fname+'-'+str(fontno)
    try:
        k=usefont.index(fno)        
    except ValueError:
        usefont.append(fno)    
    try:        
        r=usefontname.index(fname)
    except ValueError:    
        usefontname.append(fname)
        
def writefont():                             #new 2016_0129  function for writing cinput.tex 
    for i in range(len(usefont)):
        fn=usefont[i].split('-')
        f=fn[0]
        n=int(fn[1])
        if (n<=25):            # 0-25: a,b,c ,...,z 
            c1=chr(n+97)
        elif (n<=51):          # 26-51: aa,ab,ac ,...,az
            c1='a'+chr(n+71)
        elif (n<=77):          # 52-77: ba,bb,bc ,...,bz
            c1='b'+chr(n+45)
        else :                    # 78-103: ca,cb,cc ,...,cz
            c1='c'+chr(n+19)

        file_cinput.write('\\providecommand{\\%s%sQ}{\\fontfamily{cw%s}\\fontseries{%s}\\selectfont}\n' % (f,c1,f,str(n)))

    for i in range(len(usefontname)):        
        file_cinput.write('\\newcommand{\\ctxf%s}{\\ignorespaces}\n' % (usefontname[i].lower()))    # fontname lower case

import re                                                      
cjk = re.compile(u'[\u4e00-\u9fff]+', re.UNICODE)
cjk_punc = re.compile(u'[\u3001-\u301f]+', re.UNICODE)
ctxf = re.compile(r'\\ctxf(mes|me|ms|m|bbes|bbe|bbs|bb|res|re|rs|r|fes|fe|fs|f|kes|ke|ks|k)')       # to be expanded to incluce all fonts
digit = re.compile('[\d]+')

file_cinput = open('cinput.tex', 'w', newline="\n") 

file_cinput.write('\\providecommand{\\z}{\\hskip 0.0pt plus0.2pt minus0.1pt}\n')
file_cinput.write('\\providecommand{\\Z}{\\hskip 1.2pt plus0.4pt minus0.2pt}\n')
file_cinput.write('\\providecommand{\\zZ}{\\hskip 3.6pt plus1.2pt minus0.8pt}\n') 
file_cinput.write('\\providecommand{\\cH}{\\char}\n')

file_object = open('test3.tex', 'w')
file_object.write('\\input cinput.tex ')

###
# 1. \ctxfdef 須自成一行
# 2. From cwtex4, if \ctxfdef found, then do the following algorithm.
# 
#      For example, \ctxfdef{\section}[\ctxfr]{\ctxfk}{\ctxfbb}
# 
#      seperate (a) \section, (b) \ctxfr (optional), (c) \ctxfk, \ctxfbb
#      for (c), there at most 2 arguments. For part (b) and (c), generate font name: r, k, bb
# 
#        example:                                     
#        \ctxfdef{\section}[\ctxff]{\ctxfk}{ctxfbb} =>
#          \section, 1, 1, 1, m, k, bb                
#        \ctxfdef{\section}{\ctxfk}{ctxfbb} =>        
#          \section, 0, 1, 1, m, k, bb                
#        \ctxfdef{\section}{\ctxfk} =>                
#          \section, 0, 1, 0, m, k, m                 
# 
#      Search for command name from (a) in .ctx file, eg., c_macro[0] (= \section).
#      If found, check if \section*, goto the char position after [ or {, and change font name.
#          Here, we use the same algorithm as the \ctxf portion, but only need to 
#          (a) re-define  curf, and (b) fontlist.append
#          For example,  {\ctxfm ,,. \bfig[.]{.}{.}  ...}  or  ... \st{.} ...
###  

###
# The purpose of n in [["M", n]] is to make sure that we can back to the previous font
# 
#   {\ctxfm ... {\ctxfk ...} ...}
# 
# n = 1 after the second  "{", n = 0 after the next  "}",  and then curf = m
###

char_skip = 0
fontlist = [["M", 0]]
curf = fontlist[len(fontlist)-1][0]

###
# c_macro is a list of group of 7 elements
# 
#   c_macro["\section", 0, 1, 0, "m", "bb", "m", "\bfig", 0, 1, 0, "m", "r", "m"]
#
# the first element of each group is the latex macro 
#
#   curm > 0 means there is ctxf macro
#   curf is current font, default is  \ctxfm
##

c_macro = []  
curm = 0
bgn = []

file = open('test3a.ctx', encoding='utf-8')
while 1:
    lines = file.readlines(1)                      # read by lines
#    print(lines)
    str1 = ''.join(lines)
    i = 0   
    k = 0                                        # ith char in current line
    linelength = len(str1)
    while i != linelength: 
####         
#    Check \ctxfdef. command  
#
        if re.findall(r'\\ctxfdef', str1):
            str2 = '% '.join(lines)              ### if two lines together, the second line 
            file_object.write(str2)              ### is not processed correctly             

            cm_a = re.findall(r'\{\\[-a-zA-Z]+\}', str1[i:])                        
            option = re.findall(r'\[\\[-a-zA-Z]+\]', str1[i:])                      
            c_macro.append(cm_a[0].strip("{").strip("}"))         # getting  \section 
            if not option:                                                          
                c_macro.append(0)                # if option, 1; else  0
            else:
                c_macro.append(1)                # no. of commands include \section and option                                                  
            c_macro.append(1)                
            if len(cm_a) == 3:                   # if no option, there is at lease one font command
                c_macro.append(1)                # cm_a does not count option
            elif len(cm_a) == 2:
                c_macro.append(0)
            n = ctxf.findall(str1[i:])           # next find cw-font in ctxfdef
            if not option:                                                          
                c_macro.append("m")              # if no option, \ctxfm
            for j in range(0,len(n)):                                                                  
                c_macro.append(n[j]) 
            if not option and len(n) == 1:
                c_macro.append("m")              # if no option, \ctxfm
            elif len(n) == 2:
                c_macro.append("m")              # if no option, \ctxfm
            i = linelength - 1                        
####     
        elif cjk.match(str1[i]):
            fontchar, kfno=readn2(str1[i])                   # new, kfno_2016_0129
            searchfont(curf,kfno)                            # new 2016_0129
            y = "{\\" + curf + fontchar                      #fontdic.get(str1[i], None)  changed
            if digit.match(str1[i+1]):
                y = y + "\\Z"
            if cjk.match(str1[i+1]):
                y = y + "\\z"
            file_object.write(y)
        elif cjk_punc.match(str1[i]):
            fontchar, kfno=readn2(str1[i])                   # new, kfno_2016_0129
            searchfont(curf,kfno)                            # new 2016_0129
            y = "{\\" + curf + fontchar                      # fontdic.get(str1[i], None)   changed    
            if str1[i] == "。":
                y = y + "\\zZ" 
            file_object.write(y)            
        elif digit.match(str1[i]):
            y = str1[i]    
            if cjk.match(str1[i+1]):
                y = y + "\\Z"
            file_object.write(y)

        elif str1[i] == "{":
            file_object.write("{")
            bgn.append("{")
            fontlist[len(fontlist)-1][1] = fontlist[len(fontlist)-1][1] + 1 
            if curm > 0:
                fontlist.append([c_macro[7 * (curm - 1) + 5].upper(), 0])    
                print(fontlist)                                  
                curf = fontlist[len(fontlist)-1][0] 

        elif str1[i] == "}":                                                # Check if  "}"  matches with  "{"
            if not bgn:
                print("brackets does not match for {.}")
            else:
                del (bgn[len(bgn)-1])
            fontlist[len(fontlist)-1][1] = fontlist[len(fontlist)-1][1] - 1
            if fontlist[len(fontlist)-1][1] < 0:                            # number of } is more than {
                del fontlist[-1]
                curf = fontlist[len(fontlist)-1][0]
            if curm > 0:
                curm = 0                            ### to be revised, need to handle 3 arguments
            file_object.write("}")   
###
# Since checking macro starts with checking "\\", we have to check \\ctxf first.
###             
        elif str1[i] == "\\" and str1[i+1] == "c" and str1[i+2] == "t" and str1[i+3] == "x" and str1[i+4] == "f" and str1[i+5] != "d" and str1[i+6] != "e":
            n = ctxf.findall(str1[i:])  
            if n:                                         
                fontlist.append([n[0].upper(), 0])                                      
                curf = fontlist[len(fontlist)-1][0] 
                print(curf)
            file_object.write("\\")                     
### 
#   We have to checked if c_macro is empty  
#   c_macro != []  means \ctxfdef exists, so  c_macro[i]  exists, 
#     c_macro[0]  is the first command, eg., \section
#     c_macro[7]  is the second command, eg., \bfig
###   

        elif str1[i] == "\\":                                                          
            if c_macro != []:      
                for k in range(0,len(c_macro)//7):
                    if re.findall(r'(' + '\\' + str(c_macro[k*7]) + r')', str1[i:]):
                        curm = k + 1                    
#                     if test_curm:
#                    print(test_curm)

#
#                   curm = 0/7 + 1; eg.,  if c_macro[7], then curm = 7/7 + 1 = 2
#                  print("We find it!")                    
            file_object.write("\\") 
###
#             if x:
#                 file_object.write(''.join(x))
#                 i = i + len(x)
#                 if str1[i] == "{":
#                     file_object.write("{")
#                     i = i + 1                    
#                     bgn.append("{")
#                     fontlist[len(fontlist)-1][1] = fontlist[len(fontlist)-1][1] + 1 
#                     curf = c_macro[5]
###
        else:
            y = str1[i]    
            file_object.write(y)
        i += 1
    if not lines: break

writefont()                                                         #new 2016_0129  write cinput.tex

file.close()
file_object.close()    
file_cinput.close()  

from subprocess import call
call(["pdflatex", "test3"])  


    

