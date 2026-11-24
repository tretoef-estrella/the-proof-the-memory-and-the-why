#!/usr/bin/env python3
# Converts the md master (restricted subset) into a pdflatex source. Written for this one document.
import re,sys
src=sys.argv[1]; out=sys.argv[2]
L=open(src,encoding='utf-8').read().split('\n')
def esc(t):
    t=t.replace('\\','\\textbackslash ')
    for c in '&%#_$': t=t.replace(c,'\\'+c)
    return t
def inline(t):
    urls=[]
    def keep(m):
        urls.append(m.group(0)); return '\x00%d\x00'%(len(urls)-1)
    t=re.sub(r'https?://\S+',keep,t)
    t=esc(t)
    t=re.sub(r'\[(\d+(?:, \d+)*)\]',lambda m:'\\cite{'+','.join('s'+x for x in m.group(1).split(', '))+'}',t)
    t=re.sub(r'\*\*(.+?)\*\*',r'\\textbf{\1}',t)
    t=re.sub(r'\*(.+?)\*',r'\\emph{\1}',t)
    t=t.replace('“','``').replace('”',"''").replace('‘','`').replace('’',"'").replace('–','--')
    t=re.sub('\x00(\\d+)\x00',lambda m:'\\url{'+urls[int(m.group(1))]+'}',t)
    return t
o=[]; lst=None; h1=0; bib=False
def close():
    global lst
    if lst: o.append('\\end{%s}'%lst); lst=None
for ln in L:
    if bib:
        m=re.match(r'\[(\d+)\] (.*)',ln)
        if m: o.append('\\bibitem{s%s} %s\n'%(m.group(1),inline(m.group(2))))
        continue
    if ln.startswith('### Sources'):
        close(); bib=True
        o.append('\\selectlanguage{english}\n\\renewcommand{\\refname}{%s}\n\\begin{thebibliography}{9}\\small'%inline(ln[4:]))
        continue
    if ln.strip()=='---':
        close(); continue
    if ln.startswith('# '):
        close(); h1+=1
        if h1==2: o.append('\\newpage\\selectlanguage{spanish}')
        o.append('\\begin{center}{\\LARGE\\bfseries %s\\par}\\end{center}'%inline(ln[2:])); continue
    if ln.startswith('## '):
        close(); o.append('\\begin{center}{\\large\\itshape %s\\par}\\end{center}\\medskip'%inline(ln[3:])); continue
    if ln.startswith('### '):
        close(); o.append('\\subsection*{%s}'%inline(ln[4:])); continue
    m=re.match(r'(\d+)\. (.*)',ln)
    if m:
        if lst!='enumerate': close(); o.append('\\begin{enumerate}'); lst='enumerate'
        o.append('\\item '+inline(m.group(2))); continue
    if ln.startswith('- '):
        if lst!='itemize': close(); o.append('\\begin{itemize}'); lst='itemize'
        o.append('\\item '+inline(ln[2:])); continue
    if ln.strip()=='':
        close(); o.append(''); continue
    if ln.strip()=='Claude':
        o.append('\\medskip\\hfill\\textit{Claude}\\par'); continue
    o.append(inline(ln))
close()
if bib: o.append('\\end{thebibliography}')
pre=r'''\documentclass[11pt,a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{lmodern}
\usepackage[spanish,es-noshorthands,es-nolists,es-noindentfirst,english]{babel}
\usepackage[margin=2.6cm]{geometry}
\usepackage{microtype}
\usepackage[hidelinks]{hyperref}
\usepackage{xurl}
\setlength{\parindent}{0pt}\setlength{\parskip}{0.55em}
\hypersetup{pdftitle={The Proof, the Memory and the Why},pdfauthor={Claude (Fable 5.2, Anthropic), at the invitation of Rafael Amichis Luengo}}
\begin{document}
'''
open(out,'w',encoding='utf-8').write(pre+'\n'.join(o)+'\n\\end{document}\n')
