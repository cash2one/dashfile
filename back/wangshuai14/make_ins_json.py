#!/usr/bin/python

import json
import random
import operator
import os

def jstree(json):
    result=[]
    if isinstance(json, dict):
        for k,v in json.iteritems():
            a=random.uniform(0,10)
            if not isinstance(v,dict) and not isinstance(v,list):
                if len(v) > 60 and r'://' in v:
                    temp=v
                    pos=temp.index(r'://')
                    content=temp[0:pos+3]+"..."+temp[-57:]
                    result.append({"id":k+str(a),"text":str(k)+":"+content}) 
                else:
                    result.append({"id":k+str(a),"text":str(k)+":"+str(v)}) 
            else:
                chstr = jstree(v)
                result.append({"id":k+str(a),"text":k,"children":chstr})    
    elif isinstance(json, list):
        for v in json:
            a=random.uniform(0,10)
            if not isinstance(v,dict) and not isinstance(v,list):
                result.append({"id":v+str(a),"text":v}) 
            else:
                chstr = jstree(v)
                result.append({"id":str(a),"text":"--","children":chstr})  
    result_sorted=sorted(result,key=operator.itemgetter('text'))
    return result_sorted
def main():
    infile="/home/work/data_search/result.txt"
    outfile="/home/work/data_search/result.json"
    fout=open(outfile,'w')
    if os.path.getsize(infile) != 0:
        fin=open(infile)
        s=json.load(fin)
        result_raw=jstree(s)
        for x in range(0,len(result_raw)):
            result_raw[x]['state']={"opened":"true"}
        result=json.dumps(result_raw)
    else:
        result_raw = [{"id":1,"text":"empty"}] 
        result=json.dumps(result_raw)
    print >> fout, result

    infile="/home/work/data_search/result_no_status.txt"
    outfile="/home/work/data_search/result_no_status.json"
    fout=open(outfile,'w')
    if os.path.getsize(infile) != 0:
        fin=open(infile)
        s=json.load(fin)
        result_raw=jstree(s)
        for x in range(0,len(result_raw)):
            result_raw[x]['state']={"opened":"true"}
        result=json.dumps(result_raw)
    else:
        result_raw = [{"id":1,"text":"empty"}] 
        result=json.dumps(result_raw)
    print >> fout, result

    infile="/home/work/data_search/machine.txt"
    outfile="/home/work/data_search/machine.json"
    fout=open(outfile,'w')
    if os.path.getsize(infile) != 0:
        fin=open(infile)
        s=json.load(fin)
        result_raw=jstree(s)
        for x in range(0,len(result_raw)):
            result_raw[x]['state']={"opened":"true"}
        result=json.dumps(result_raw)
    else:
        result_raw = [{"id":1,"text":"empty"}] 
        result=json.dumps(result_raw)
    print >> fout, result

    infile="/home/work/data_search/machine_child.txt"
    outfile="/home/work/data_search/machine_child.json"
    fout=open(outfile,'w')
    if os.path.getsize(infile) != 0:
        fin=open(infile)
        result=[]
        count=0
        for x in fin.readlines():
            map={}
            map['id']=count
            map['text']=x.strip('\n')
            count += 1
            result.append(map)    
    else:
        result_raw = [{"id":1,"text":"empty"}] 
        result=json.dumps(result_raw)
    print >> fout, result

    infile="/home/work/data_search/machine_child.json"
    outfile="/home/work/data_search/machine_child_better.json"
    fin = open(infile)
    fout = open(outfile,'w')
    for x in fin.readlines():
        x = x.replace("'",'"') 
        print >> fout, x


if __name__ == '__main__':
    main()        
        
