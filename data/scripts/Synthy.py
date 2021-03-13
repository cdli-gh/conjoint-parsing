import sys,io,re,argparse,random

""" synthesize training data from a training corpus in CDLI-CoNLL format
	words with complex MORPH: replace randomly with words with the same POS+MORPH
	*nouns* with simple MORPH: replace randomly with words that have the same parent word and the same first dependent	
	
	(complex MORPH: contain at least one .)
 """
 
args=argparse.ArgumentParser(description="synthesize additional training data from a CDLI-CoNLL corpus")
args.add_argument("size", type=int, help="minimum token size of target corpus")
args.add_argument("corpus", nargs="+", type=str, action="extend", help="input corpus")
args.add_argument("-support", "--support", nargs="*", type=str, action="extend", help="support corpora, used to determine possible substitutes")

args=args.parse_args()
if args.support==None:
	args.support=[]

""" sentence must be an array of string arrays"""
def update_syntactic_replacement_rules(pos2morph2edge2hword2cpos2cedge2form2freq,sentence):
	try:
		# ID WORD SEGM POS MORPH HEAD EDGE MISC	
		for x in range(len(sentence)):
			sentence[x][0]=int(sentence[x][0])
			sentence[x][5]=int(sentence[x][5])
		for x in range(len(sentence)):
			word=sentence[x][1]
			pos=sentence[x][3]
			morph=sentence[x][4]
			edge=sentence[x][6]
			hword="_"
			if sentence[x][5]>0:
				hword=sentence[sentence[x][5]-1][1]
			cpos="_"
			cedge="_"
			for y in range(len(sentence)):
				if cpos=="_" or cedge=="_":
					if sentence[y][5]==sentence[x][0]:
						cpos=sentence[y][3]
						cedge=sentence[y][6]
			if pos not in pos2morph2edge2hword2cpos2cedge2form2freq:
				pos2morph2edge2hword2cpos2cedge2form2freq[pos] = { morph : { edge : { hword : { cpos : { cedge : { word : 1 }}}}}}
			elif morph not in pos2morph2edge2hword2cpos2cedge2form2freq[pos]:
				pos2morph2edge2hword2cpos2cedge2form2freq[pos][morph] = { edge : { hword : { cpos : { cedge : { word : 1 }}}}}
			elif edge not in pos2morph2edge2hword2cpos2cedge2form2freq[pos][morph]:
				pos2morph2edge2hword2cpos2cedge2form2freq[pos][morph][edge]= { hword : { cpos : { cedge : { word : 1 }}}}
			elif hword not in pos2morph2edge2hword2cpos2cedge2form2freq[pos][morph][edge]:
				pos2morph2edge2hword2cpos2cedge2form2freq[pos][morph][edge][hword]= { cpos : { cedge : { word : 1 }}}
			elif cpos not in pos2morph2edge2hword2cpos2cedge2form2freq[pos][morph][edge][hword]:
				pos2morph2edge2hword2cpos2cedge2form2freq[pos][morph][edge][hword][cpos]= { cedge : { word : 1 }}
			elif cedge not in pos2morph2edge2hword2cpos2cedge2form2freq[pos][morph][edge][hword][cpos]:
				pos2morph2edge2hword2cpos2cedge2form2freq[pos][morph][edge][hword][cpos][cedge] = { word : 1 }
			elif word not in pos2morph2edge2hword2cpos2cedge2form2freq[pos][morph][edge][hword][cpos][cedge]:
				pos2morph2edge2hword2cpos2cedge2form2freq[pos][morph][edge][hword][cpos][cedge][word] = 1
			else:
				pos2morph2edge2hword2cpos2cedge2form2freq[pos][morph][edge][hword][cpos][cedge][word]+= 1
		
	except:	# number format exception etc.
		pass
	return pos2morph2edge2hword2cpos2cedge2form2freq
	
""" syntactic rewriting (note that gloss-based rephrasal is done elsewhere, no return value, just write """
def rephrase_sentence(pos2morph2edge2hword2cpos2cedge2form2freq,sentence):
	if len(sentence)>0:
		try:
			# ID WORD SEGM POS MORPH HEAD EDGE MISC	
			for x in range(len(sentence)):
				sentence[x][0]=int(sentence[x][0])
				sentence[x][5]=int(sentence[x][5])
			for x in range(len(sentence)):
				word=sentence[x][1]
				pos=sentence[x][3]
				morph=sentence[x][4]
				edge=sentence[x][6]
				misc=sentence[x][7]
				if misc=="_":
					hword="_"
					if sentence[x][5]>0:
						hword=sentence[sentence[x][5]-1][1]
					cpos="_"
					cedge="_"
					for y in range(len(sentence)):
						if cpos=="_" or cedge=="_":
							if sentence[y][5]==sentence[x][0]:
								cpos=sentence[y][3]
								cedge=sentence[y][6]				
					if pos in pos2morph2edge2hword2cpos2cedge2form2freq:
						if morph in pos2morph2edge2hword2cpos2cedge2form2freq[pos]:
							if edge in pos2morph2edge2hword2cpos2cedge2form2freq[pos][morph]:
								if hword in pos2morph2edge2hword2cpos2cedge2form2freq[pos][morph][edge]:
									if cpos in pos2morph2edge2hword2cpos2cedge2form2freq[pos][morph][edge][hword]:
										if cedge in pos2morph2edge2hword2cpos2cedge2form2freq[pos][morph][edge][hword][cpos]:
											new_word=random.choice(list(pos2morph2edge2hword2cpos2cedge2form2freq[pos][morph][edge][hword][cpos][cedge].keys()))
											sentence[x][1]=new_word
											if word!=new_word:
												sentence[x][7]="synt-randomized"
		except:
			pass
		for line in sentence:
			print("\t".join( [ str(f) for f in line ]))
		print()

dictsize=0
pos2morph2form2freq={}
pos2morph2edge2hword2cpos2cedge2form2freq={}
for file in args.corpus+args.support:
	with open(file,"r") as corpus:
		sentence=[]
		for line in corpus:
			line=line.rstrip()
			if re.match(r"^[0-9]",line):
				# ID WORD SEGM POS MORPH HEAD EDGE MISC	
				line=line.split("\t")
				id=line[0]
				if(id=="1") and len(sentence)>0:
					pos2morph2edge2hword2cpos2cedge2form2freq=update_syntactic_replacement_rules(pos2morph2edge2hword2cpos2cedge2form2freq,sentence)
					sentence=[]
				sentence.append(line)
				word=line[1]
				pos=line[3]
				morph=line[4]
				if not pos in pos2morph2form2freq:
					pos2morph2form2freq[pos]={morph : { word : 1 } }
					dictsize+=1
				elif not morph in pos2morph2form2freq[pos]:
					pos2morph2form2freq[pos][morph] = { word : 1 }
					dictsize+=1
				elif not word in pos2morph2form2freq[pos][morph]:
					pos2morph2form2freq[pos][morph][word] = 1
					dictsize+=1
				else:
					pos2morph2form2freq[pos][morph][word]+=1
		if(len(sentence)>0):
			pos2morph2edge2hword2cpos2cedge2form2freq=update_syntactic_replacement_rules(pos2morph2edge2hword2cpos2cedge2form2freq,sentence)
			sentence=[]
		sys.stderr.write("adding "+file+": "+str(dictsize)+"\r")
		sys.stderr.flush()
	sys.stderr.write("\n")
	sys.stderr.flush()
					
outsize=0
while(outsize<args.size):
	for file in args.corpus:
		if outsize<args.size:
			with open(file,"r") as corpus:
				sentence=[]
				for line in corpus:
					line=line.rstrip()
					if re.match(r"^[0-9]",line):						
						line=line.split("\t")
						if line[1]=="1":
							rephrase_sentence(pos2morph2edge2hword2cpos2cedge2form2freq,sentence)
							outsize+=len(sentence)
							sentence=[]
						word=line[1]
						pos=line[3]
						morph=line[4]
						if "." in morph:
							if pos in pos2morph2form2freq:
								if morph in pos2morph2form2freq[pos]:
									new_word=random.choice(list(pos2morph2form2freq[pos][morph].keys()))
									line[1]=new_word
									if new_word!=word:
										line[7]="gloss-randomized"
						sentence.append(line)
					else:
						print(line)
				rephrase_sentence(pos2morph2edge2hword2cpos2cedge2form2freq,sentence)
				outsize+=len(sentence)
				sentence=[]
						
