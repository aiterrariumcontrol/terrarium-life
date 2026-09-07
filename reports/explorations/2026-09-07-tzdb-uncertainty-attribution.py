import re, os, json, collections
REGIONS=["africa","antarctica","asia","australasia","europe","northamerica","southamerica"]
HEDGE=re.compile(r"\b(probably|presumably|guess(ed|es|ing)?|uncertain|unclear|unreliable|apocryphal|dubious|not sure|unsure|no evidence|we do not know|we don't know|assume[ds]?|assuming|speculat\w+|conjectur\w+|invented)\b",re.I)
countries={l.split("\t")[1].strip() for l in open("iso3166.tab") if not l.startswith("#") and "\t" in l}
# section header = comment line that is exactly a country name (or country name + parenthetical)
def is_header(t):
    t=t.strip()
    return t in countries or re.sub(r"\s*\(.*\)$","",t) in countries

def parse(path):
    cur=None
    for i,raw in enumerate(open(path,encoding="utf-8",errors="replace"),1):
        line=raw.rstrip("\n")
        if not line.strip(): yield("blank",i,None,None,""); continue
        if line.lstrip().startswith("#"): yield("comment",i,None,None,line.lstrip()[1:].strip()); continue
        f=line.split()
        if f[0]=="Zone": cur=f[1]; yield("data",i,"Zone",cur,line)
        elif f[0]=="Rule": yield("data",i,"Rule",f[1],line)
        elif f[0]=="Link": yield("data",i,"Link",f[2],line)
        elif line[0] in " \t" and cur: yield("data",i,"Zonecont",cur,line)
        else: yield("data",i,"?",None,line)

out=[];st=collections.Counter()
for r in REGIONS:
    ev=list(parse(r))
    # assign section index
    sec=0;secname="(preamble)";sections=collections.defaultdict(lambda:{"names":set(),"name":None})
    tagged=[]
    for e in ev:
        if e[0]=="comment" and is_header(e[4]):
            sec+=1; secname=e[4].strip()
            sections[sec]["name"]=secname
        tagged.append((sec,e))
        if e[0]=="data" and e[3]: sections[sec]["names"].add((e[2] if e[2]!="Zonecont" else "Zone",e[3]))
    n=len(tagged);i=0
    while i<n:
        s,e=tagged[i]
        if e[0]=="comment":
            j=i
            while j<n and tagged[j][1][0]=="comment": j+=1
            blk=[tagged[k][1] for k in range(i,j)]
            hed=[b for b in blk if HEDGE.search(b[4]) and len(b[4].split())>2]
            if hed:
                text=" ".join(b[4] for b in blk)
                # 1. explicit zone/rule names mentioned in the block text
                secnames=sections[s]["names"]
                mentioned=sorted({nm for k,nm in secnames if re.search(r"\b"+re.escape(nm.split("/")[-1].replace("_"," "))+r"\b",text) or nm in text})
                # 2. nearest following data line in same section
                fwd=None
                for k in range(j,n):
                    if tagged[k][0]!=s: break
                    if tagged[k][1][0]=="data" and tagged[k][1][3]: fwd=tagged[k][1][3]; break
                scope=sorted({nm for _,nm in secnames})
                lvl=("named" if mentioned else "adjacent" if fwd else "section" if scope else "none")
                st[lvl]+=1
                out.append(dict(file=r,line=hed[0][1],section=sections[s]["name"],level=lvl,
                    names=mentioned or ([fwd] if fwd else scope[:8]),
                    scope_size=len(scope),text=" ".join(h[4] for h in hed)[:400]))
            i=j
        else: i+=1
print(json.dumps(st,indent=1),"blocks",len(out))
json.dump(out,open("/tmp/hedges2.json","w"),indent=1)
for x in out[:3]+out[60:63]:
    print("---",x["file"],x["line"],"|sec:",x["section"],"|",x["level"],"->",x["names"][:4])
    print("   ",x["text"][:150])
