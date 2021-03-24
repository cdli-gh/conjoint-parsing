import sys,os,re,timeit

""" Deppy.py: expand MTAAC dependency syntax to morphosyntactic dependencies

MTAAC dependency syntax:
	one word per line, HEAD: syntactic head, DEP: syntactic dependency

MTAAC morphosyntactic dependencies:
	one slot per line,
	- morphological head: standard dependency syntax
	- other slots: HEAD: morphological head, POS: slot, DEP: morphological gloss, FORM: entire word
	
compact MTAAC morphosyntactic dependencies: (for human consumption)
	- MTAAC morphosyntactic dependencies for all slots with an annotation
	
full MTAAC morphosyntactic dependencies: (for parsing)
	- MTAAC morphosyntactic dependencies for all possible slots for the given POS """
	
from Slotty import get_slots, get_head, pattern, pos2pattern, enforce_pattern				

# given an array of row arrays, eliminate crossing edges
def make_projective(sentence,id=0,head=5):
	changed=True
	iterations=0
	start = timeit.default_timer()
    
	# terminate by 20 sec timeout
	while(changed and iterations < len(sentence)*2 and timeit.default_timer()-start<20):
		changed=False
		for x in range(len(sentence)-1):
			for y in range(x,len(sentence)):	# x<y => x[id] < y[id]
				y2xid=False
				y2xhead=False
				if ((sentence[y][head] < sentence[x][id] and sentence[y][id] < sentence[x][head] ) or
				    (sentence[x][head] < sentence[y][head] and sentence[y][head] < sentence[x][id])):
					sentence[y][head] = sentence[x][id]					
					print(sentence[y][id],"=>",sentence[y][head])
					y2xid=True
					changed=True
				elif (
					(sentence[x][id] < sentence[y][head] and sentence[y][head]<sentence[x][head] and sentence[x][head]<sentence[y][id]) or
					(sentence[y][id] < sentence[x][head] and sentence[x][head]<sentence[y][head])):
					sentence[y][head] = sentence[x][head]
					print(sentence[y][id],"=>",sentence[y][head])
					changed=True
					y2xhead=True
		iterations+=1
	return sentence
	

def get_feats(morph,pos):
	feats=get_slots(morph,pos).split(".")
	slots=[ re.sub(r"=.*","",f) for f in feats ]
	feats=[ re.sub(r".*=","",f) for f in feats ]
	
	if pos in pos2pattern:
		feats,slots=enforce_pattern(feats,slots,pos,validate=True)
		# this works in principle, but it is a bit lossy
		head=get_head(slots)
		if(head!=None):
			if(len(pos)==0 or pos=="_"):
				pos=feats[head]
			if not (
				pos in feats[head] or							# we keep NV for verbs and named entity tags for nouns
				(feats[head]=="COP" and pos=="V") or			# we keep COP for verbs
				(feats[head] in ["DN", "MN" ,"ON","PN","TN" ])	# we keep proper names (full-gloss)

				# corrections in royal subcorpus:
				# N => CC
				# _ => CC
				# IP => N
				# N => NU
				# NV => NU
				# _ => NU
				# n => NU
				# STEM => V
				
				# corrections in full auto-glossed subcorpus:
				# note: the POS annotation of the MTAAC-Ur III corpus overgeneralizes numerals
				# COP => N
				# IP => N
				# N => DET
				# N => NU
				# N => V
				# NV => NU
				# V => N
				# V => NU
				
				):
				sys.stderr.write("warning: override head feature "+feats[head]+" with POS "+pos+"\n")
				sys.stderr.flush()
				feats[head]=pos

	return feats,slots

# sentence must be an array of 8-col arrays, with first and 6th column integers
# this does expansion, but it does not do try to attach morphemes to the nominal heads
# if not return_empty_slots, only write slots with features, for training, write all
# if perlocate, move to attach nominal morphemes to the head of the phrase they apply to
def expand_cdli_conll(sentence, return_empty_slots=True, perlocate=True):
	
	sentence=sentence.split("\n")
	sentence = [ line.split("\t") for line in sentence ]
	for x in range(len(sentence)):
		try:
			sentence[x][0]=int(sentence[x][0])
			sentence[x][5]=int(sentence[x][5])
		except:
			sentence.pop(x)
			x=x-1

	idold2new={}
	new=[]
	for line in sentence:
		id=line[0]
		word=line[1]
		seg=line[2]
		pos=line[3]
		morph=line[4]
		head=line[5]
		edge=line[6]
		misc=line[7]
		
		feats,slots=get_feats(morph,pos)
		mhead=get_head(slots)
		p = pattern["N"]
		if pos in pos2pattern:
			p=pattern[pos2pattern[pos]]
		phead=get_head(p)

		p_nr=0
		s_nr=0
		for p_nr in range(len(p)):
			slot=p[p_nr]
			newid=len(new)+1
			if(slot in p[0:p_nr]):
				slot=slot+"."+str(p[0:p_nr].count(slot))
			if s_nr<len(slots) and p[p_nr]==slots[s_nr]:
				if s_nr==mhead:
					idold2new[id]=newid
					new.append([newid,word,seg,pos,morph,head,edge,misc])
				else:
					new.append([newid,word,"_",slot,"_",id,feats[s_nr],"_"])
				s_nr+=1
			else:
				if return_empty_slots:
					new.append([newid,word,"_",slot,"_",id,"_","_"])
	
	sentence=new
	for x in range(len(sentence)):
		try:
			sentence[x][5]=idold2new[sentence[x][5]]
		except:
			pass
			
	# try to attach to the respective parent node
	# partially and heuristic only
	if(perlocate):
		for x in range(len(sentence)):
			steps_up=0
			if re.match(r"^N[3-6]\.[0-9].*", sentence[x][3]):
				steps_up+=int(re.sub(r".*\.","",sentence[x][3]))
			y=sentence[x][5]-1
			if y>=0 and sentence[y][6]=="appos" and re.match(r"^N[5-6].*",sentence[x][3]):
				steps_up+=1
			#print("perlocate",x,steps_up,y,sentence[y][3],pos2pattern[sentence[y][3]])				
			if(steps_up>0):
				lastY=y
				#print("perlocate",x,steps_up,y,sentence[y][3],pos2pattern[sentence[y][3]])				
				while steps_up >= 0 and y >= 0 and sentence[y][3] in pos2pattern and pos2pattern[sentence[y][3]].startswith("N") and sentence[y][5]>0:
					#print("perlocate",x,steps_up,y,sentence[y][3],pos2pattern[sentence[y][3]])				
					if(not sentence[y][6]=="appos"):
						steps_up = steps_up-1
					lastY=y
					y=sentence[y][5]-1					
				sentence[x][5]=sentence[lastY][0]
				if(not return_empty_slots):
					sentence[x][3]=re.sub(r"\..*","",sentence[x][3])	# skip suffixes		
				
		# TODO
		sentence=make_projective(sentence,id=0,head=5)			
		
	sentence = "\n".join([ "\t".join( [ str(f) for f in row ]) for row in sentence ] )
	return sentence		
			
# read CDLI-CoNLL (8 cols,  ID WORD SEGM POS MORPH HEAD EDGE MISC)
sentence=""

for line in sys.stdin:
	line=line.rstrip()
	if(line.strip().startswith("#")):
		print(line)
	elif len(line.strip())==0:
		if(len(sentence)>0):
			print(expand_cdli_conll(sentence))
		sentence=""
		print(line)
	else:
		line=re.sub(r"[^\\]#.*","",line)	# skip inline comments
		sentence=sentence+line+"\n"
	
if(len(sentence)>0):
	print(expand_cdli_conll(sentence))
	

# post-process get_slots: replace head feature with main pos

