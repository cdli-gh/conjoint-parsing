import sys,os,re,timeit

""" Heady.py: reduce expanded MTAAC dependency syntax to syntactic dependencies

MTAAC dependency syntax:
	one word per line, HEAD: syntactic head, DEP: syntactic dependency

MTAAC morphosyntactic dependencies:
	one slot per line,
	- morphological head: standard dependency syntax
	- other slots: HEAD: morphological head, POS: slot, DEP: morphological gloss, FORM: entire word
	
delete slots, remove their deps
	"""
	
# sentence must be an array of 8-col arrays, with first and 6th column integers
# eliminate empty slots
# note that we do not keep slots with annotations in a DEPS columns (cf.https://universaldependencies.org/format.html)
# because the tags could be confused with case labels
def reduce_cdli_conll(sentence):
	
	sentence=sentence.split("\n")
	sentence = [ line.split("\t") for line in sentence ]
	for x in range(len(sentence)):
		try:
			sentence[x][0]=int(sentence[x][0])
		except:
			sentence.pop(x)
			x=x-1

	oldids=[]
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
		slot=re.match(r".*[0-9]$",pos)
		if not slot:
			newid=len(oldids)+1
			oldids=oldids+[id]
			new.append([newid,word,seg,pos,morph,head,edge,misc])
	
	for x in range(len(new)):		
		head=new[x][5]
		if head!=0:
			try:
				head=oldids.index(int(head))+1
				new[x][5]=head
			except ValueError as e:
				sys.stderr.write(str(type(head))+":"+str(head)+"\n"+str(oldids)+"\n")
				sys.stderr.write(str(e)+"\n")
				sys.stderr.flush()
				new[x][5]=0
				misc=new[x][7]
				if misc in ["_",""]:
					misc=head+":n/a"
				else:
					misc=misc+"|"+head+":n/a"
				new[x][7]=misc
	
	sentence = "\n".join([ "\t".join( [ str(f) for f in row ]) for row in new ] )
		
	return sentence		
			
# read CDLI-CoNLL (8 cols,  ID WORD SEGM POS MORPH HEAD EDGE MISC)
sentence=""

for line in sys.stdin:
	line=line.rstrip()
	if(line.strip().startswith("#")):
		print(line)
	elif len(line.strip())==0:
		if(len(sentence)>0):
			print(reduce_cdli_conll(sentence))
		sentence=""
		print(line)
	else:
		line=re.sub(r"[^\\]#.*","",line)	# skip inline comments
		sentence=sentence+line+"\n"
	
if(len(sentence)>0):
	print(reduce_cdli_conll(sentence))