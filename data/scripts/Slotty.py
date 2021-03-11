import sys,os,re
from copy import deepcopy

""" Slotty: infer ETSCRI-style slot information from MTAAC POS and FEATS annotations"""

def nominalized(feats,slots):
	# must contain something verbal
	if(not "V" in feats and not "NV" in feats and not "NU" in feats):
		return False

	# true if it contains nominalizer
	if "V15" in slots:
		return feats[slots.index("V15")]=="SUB"
	
	# or if the last non slot other than None is a nominal one (NF, N)
	if(None in slots and slots[0]!=None):
		return slots[slots.index(None)-1][0]=="N"
	return False

# return boolean and message
def valid(feats,slots):
	if(len(slots)>1):
		try:
			head=get_head(slots)
		except Exception as e:
			return False,str(e)
		for x in range(len(slots)-1):
			if(slots[x+1]!=None):
				try:
					last=str(slots[x])
					lastf=str(feats[x])
					next=str(slots[x+1])
					nextf=str(feats[x])
					cat1=re.sub(r"[0-9]+","",last)
					cat2=re.sub(r"[0-9]+","",next)
					nr1=int(re.sub(r"[^0-9]","",last))
					nr2=int(re.sub(r"[^0-9]","",next))
					if( not (
						(cat1==cat2 and nr2>nr1) or													# within the same template
						(cat1=="NV" and cat2=="N") or												# nominal inflection of "adjectives"
						(cat1=="V" and nr1>=12 and cat2=="N") or									# implicit nominalization
						(cat1=="N" and cat2=="N" and nr2 in [3,4,5] and nr1 in [3,4,5]) or			# case stacking
						(last=="N6" and "COP" in lastf and cat2=="V") or							# noun+copula => verb 
						(last=="N6" and "COP" in lastf and cat2=="N") 								# nominalization of a copular clause
						)):
						return False,"invalid slot sequence "+last+" "+next+" ("+cat1+str(nr1)+" "+cat2+str(nr2)+")"
				except ValueError as e:
					return False, str(e)+" while processing "+str(last)+" and "+str(next)
					raise e
	return True,""

pattern={
	"NV": ['NV1', 'NV2', 'NV3', 'NV4', 
		  'N3', 'N4', 'N5', 'N6', "V15", 
		  'N3', 'N4', 'N5', "N6","V15"],	
	"N": ['N1', 'N2', 
		  'N3', 'N4', 'N5', 'N6', "V15", 
		  'N3', 'N4', 'N5', 'N6', "V15", 
		  'N3', 'N4', 'N5', "N6", "V15"],
	"V": ['V1', 'V2', 'V3', 'V4', 'V5', 'V6', 'V7', 'V8', 'V9', 'V10', 'V11', 'V12', 'V13', 'V14', 'V15', 
		  'N3', 'N4', 'N5', 'N6', "V15", 
		  'N3', 'N4', 'N5', "N6", "V15"
		  ]
		 }
	
# match POS to most typical pattern
pos2pattern={
	"AJ": "NV",
	"AN": "N",
	"DET":"N",
	"DN": "N",
	"EN": "N",
	"FN": "N",
	"GN": "N",
	"IP": "N",
	"MN": "N",
	"N": "N",
	"NU": "NV",
	"NV": "NV", # no actual POS, may only be generated from feats
	"ON": "N",
	"PN": "N",
	"RN": "N",
	"SN": "N",
	"TN": "N",
	"V": "V",
	"WN": "N"

	# underlying statistics
	# # full: mapping tags to patterns
	# # royal
	# # MTAAC morph
	###	cat mtaac-morph/*conll | cut -f 4 | egrep '\.' | grep -v '#' | perl -pe 's/^([^\.]?N[^\.]*)?/$1\t$1/g; s/^(NEG|ANT)?\t/V\t/; s/^NF\t/NV\t/g' | python3 Slotty.py

	# # not fully up to date mapping
		# 	| full	 		 		| royal	 		 		| mtaac	 				|
		# 	| N		| NV	| V		| N		| NV	| V		| N		| NV	| V		|
	# ---	| ----- | ----- | ----- | ----- | ----- | ----- | ----- | ----- | ----- |
	# AJ	| 100%	| 		| 		| 		| 		| 		| 		| 		| 		|
	# AN	| 		| 		| 		| 		| 		| 		| 100%	| 		| 		|
	# DET	| 100%	| 		| 		| 		| 		| 		| 		| 		| 		|
	# DN	| 99%	| 		| 1%	| 100%	| 		| 		| 100%	| 		| 		|
	# EN	| 100%	| 		| 		| 100%	| 		| 		| 100%	| 		| 		|
	# FN	| 100%	| 		| 		| 		| 		| 		| 100%	| 		| 		|
	# GN	| 100%	| 		| 		| 100%	| 		| 		| 100%	| 		| 		|
	# IP	| 		| 		| 		| 100%	| 		| 		| 		| 		| 		|
	# MN	| 100%	| 		| 		| 		| 		| 		| 100%	| 		| 		|
	# N		| 97%	| 3%	| 0%	| 100%	| 		| 		| 100%	| 		| 		|
	# NU	| 7%	| 0%	| 92%	| 		| 100%	| 		| 		| 		| 100%	|
	# NV	| 		| 		| 		| 		| 		| 		| 36%	| 64%	| 		|
	# ON	| 100%	| 		| 		| 		| 		| 		| 100%	| 		| 		|
	# PN	| 95%	| 1%	| 4%	| 100%	| 		| 		| 100%	| 		| 		|
	# RN	| 100%	| 		| 		| 100%	| 		| 		| 100%	| 		| 		|
	# SN	| 100%	| 		| 		| 100%	| 		| 		| 100%	| 		| 		|
	# TN	| 100%	| 		| 		| 100%	| 		| 		| 100%	| 		| 		|
	# V		| 1%	| 1%	| 99%	| 		| 1%	| 99%	| 0%	| 2%	| 98%	|
	# WN	| 100%	| 		| 		| 		| 		| 		| 100%	| 		| 		|
}
	
""" validate slots: check whether all slots are coverable by the pre-defined pattern. As Sumerian inflectional morphology is recursive, there may be valid slot configurations that are not covered by the patterm, so this is a validation of the pattern, not the slot structure 

if pos is provided, check whether the pattern matches the expectations for the POS
"""
def pattern_validation(slots,pos=""):
	if len(slots)==0:
		raise Exception("empty slot list")
	for p in pattern:
		if(slots[0].startswith(p)):
			p=pattern[p]
			sl=0
			sp=0
			while(sl<len(slots) and sp<len(p)):
				if(slots[sl]==p[sp]):
					sl+=1
				elif slots[sl] in p[sp:]:
					sp=sp+p[sp:].index(slots[sl])
				else:
					sys.stderr.write("pattern mismatch: "+".".join(slots)+" don't match "+".".join(p)+"\n")
					sys.stderr.flush()
					return False
			if sl==len(slots):
				if pos in pos2pattern:
					if re.sub(r"[0-9].*","",slots[0]) == pos2pattern[pos]:
						return True
					else:
						sys.stderr.write("pattern mismatch: "+pos+" requires "+pos2pattern[pos]+", but we predict "+re.sub(r"[0-9].*","",slots[0])+"\n")
						sys.stderr.flush()
						return False
				else:
					return True
			else:
				sys.stderr.write("pattern mismatch:" +".".join(slots)+" exceed "+".".join(p)+"\n")
				sys.stderr.flush()
				return False
	raise Exception("unsupported pattern \""+re.sub(r"[0-9]+","",str(slots[0]))+"\"")

""" this is for valid patterns that do not match their pos
	returns feats, slots
	if validate=True, perform validation and pattern validation, run only if pattern is valid, but pattern_validation is False
	this is to override the gloss analysis with an analysis compliant with the part of speech, i.e., to make sure slots can be reliably predicted from POS
"""
def enforce_pattern(feats,slots,pos,validate=False):
	orig_feats=deepcopy(feats)
	orig_slots=deepcopy(slots)
	if not validate or (valid(feats,slots) and not pattern_validation(slots,pos)):
		# assume that pattern_validation failed but everything else is ok
		if pos in pos2pattern:	# otherwise, there is no pattern to enforce
			pos_pattern=pos2pattern[pos]
			head=get_head(slots)
			p=re.sub(r"[0-9].*","",slots[head])
			if pos_pattern == "N" and p in ["V", "NV"]:		# can happen for nominalizations
				while(len(slots)>0 and slots[0].startswith(p)):
					slots.pop(0)
					feats.pop(0)
				slots=["N1"]+slots
				feats=[pos]+feats
			elif pos_pattern == "N" and p=="V":				# can happen for proper names
				while(len(slots)>0 and slots[0].startswith("NV")):
					slots.pop(0)
					feats.pop(0)
				slots=["N1"]+slots
				feats=[pos]+feats
			elif pos_pattern =="V" and p=="N":					# assume these are nominalizations, in the full corpus, these often carry case
				if(slots[0]==("N1")):
					slots[0]="V12"
			elif pos_pattern == "V" and p=="NV":
				if "NV2" in slots:
					for x in range(slots):
						if slots[x]=="NV1": 
							slots[x]="V1"
						if slots[x]=="NV2":
							slots[x]="V12"
						if slots[x]=="NV3":
							slots.pop(x)
							feats.pop(x)
							x=x-1
						if slots[x]=="NV4":
							slots[x]="V15"
			elif pos_pattern == "NV" and p=="N":
				slots[head]="NV2"
				feats[head]=pos
			elif pos_pattern == "NV" and p == "V":
				if "V12" in slots:
					for x in range(slots):
						if(slots[x]=="V1"):
							slots[x]="NV1"
						elif slots[x]=="V12":
							slots[x]="NV2"
						elif slots[x]=="V15":
							slots[x]="NV4"						
						elif slots[x].startswith("V"):
							slots.pop(x)
							feats.pop(x)
							x=x-1
						
	
	if valid(feats,slots):
		return feats,slots
	else:
		sys.stderr.write("warning: could not recover from pattern validation error for "+pos+" and "+".".join([s+"="+f for (s,f) in zip(slots,feats)])+"\n")
		sys.stderr.flush()
		return orig_feats, orig_slots
	
# return slot analysis, pos information is optional
def get_slots(feats,pos=""):
	# normalization
	origpos=pos
	origfeats=feats
	nouns=["N","DN","EN","GN","N-RDP","NV","PN","RN","TN","SN","IP","WN","AN","FN","MN","ON"]	# note that NV is only introduced below
	if origpos in nouns: pos="N"

	# NF.V => NV
	if "NF.V" in feats:
		feats=re.sub("NF.V","NV",feats)

	# fix typos
	fix={}
	
	## typos in ETCSRI
	fix["DAT.H"]="DAT-H"
	fix["N5."]=""
	fix["NN5="]=""
	fix["abs"]="ABS"
	fix["NV.PT"]="NV-PT"
	fix["NV.PF"]="NV-PF"
	fix["NV.ed"]="NV-PT"
	fix["NV.RDP"]="NV-RDP"
	fix["V.PF"]="V-PF"
	fix["nu."]="NEG."
	fix[".pad."]=".V."
	fix["sabar"]="N"
	fix[".gin."]=".V."
	fix[".gub."]=".V."	
	fix[".ani"]=".3-SG-H-POSS"
	fix[".stem."]=".STEM."
	fix["Ešnunak"]="SN"
	fix["Eridug"]="SN"
	fix["Taramurim"]="PN"
	fix["3-SG-H-AV3-SG-P"]="3-SG-H-A.V.3-SG-P"
	fix["-V11="]="."
	
	## typos in MTAAC
	fix["^_.ABL$"]="N.ABL"
	fix["3-SG-HN-P"]="3-SG-NH-P"
	fix["3-PL-DAT"]="3-PL.DAT"
	fix["GEN-ABL"]="GEN.ABL"
	fix["NV.F"]="NV-F"
	fix["DAH-H"]="DAT-H"
	fix["NV.F"]="NV-F"
	fix["3-SG-COP"]="COP-3-SG"
	fix["3-SG-DAT"]="3-SG.DAT"
	fix["3-SG-H-DAT"]="3-SG-H.DAT"
	fix["3-SG-P.3-PL"]="PL.3-SG-P"	# to be confirmed
	
	## typos in full (Ur-III, auto-glossed
	feats=re.sub(r"[\|].*",".",feats)		# | marks ambiguity: take the first, | separates *full* analyses (which don't have to be *complete* in linguistic terms)
	if(feats=="N.3-SG-NH"): feats="N.3-SG-NH-POSS"	# incomplete gloss
	fix["COP-3-"]="COP-3-SG"
	fix["COP-3-SGPL"]="COP-3-SG"
	fix["COP-3-SGSG"]="COP-3-SG"
	if pos=="AJ":
		pos="NV"
	
	for f in fix:
		if f in feats:
			feats=re.sub(f,fix[f],feats)
	 
	# simplify (valid) feats
	simplify={}
	simplify["NV-PT"]="NV"
	simplify["NV-F"]="NV"	# MTAAC: what is this? logically, that cannot be FIN! 
	simplify["NV-PF"]="NV"
	simplify["NV-RDP"]="NV"
	simplify["STEM-PT"]="STEM"
	simplify["STEM-PF"]="STEM"
	simplify["STEM-RDP"]="STEM"
	simplify["V-PT"]="V"
	simplify["V-PF"]="V"
	simplify["V-RDP"]="V"
	simplify["NU"]="NV"	# all numerals are inherently verbal, although mostly NV rather than V
	simplify["AJ"]="NV" # doesn't occur
	for f in simplify:
		if f in feats:
			feats=re.sub(f,simplify[f],feats)
		
	# split feats
	feats=feats.split(".")

	# replacements to improve alignment with pos annotation
	if pos in ["N"] and "NV" in feats:
		feats[feats.index("NV")]="N"
	if pos in ["V"] and "NV" in feats:
		feats[feats.index("NV")]="V"
	
	# prune feats
	removable=[
		"N5",	# segmentation error
		"X",	# illegible
		"PF",	# segmentation error
		"_",	# empty element/parsing error
		"F",	# MTAAC only: what is that?
		"PT",	# segmentation error
		"",		# full annotation: incomplete gloss
	]
	for f in removable:
		while f in feats:
			feats.remove(f)
			
	# feature fixes
	## MTAAC
	if(feats==["ABL"]):
		feats=["N"]+feats
			
	# infer POS, only for mtaac-morph
	if(len(pos)==0):
		pos="_"
	if pos=="_":
		for tag in ["V","NV","NU"]+nouns:
			if tag in feats and pos=="_":
				pos=tag
				sys.stderr.write("pos inference: "+tag+" <= "+".".join(feats)+"\n")
		if(pos=="_"):		
			sys.stderr.write("pos inference failed: _ <= "+".".join(feats)+"\n")
		sys.stderr.flush()
		
	# map feats to slots
	slots=[None]*len(feats)
	if len(feats)<=1:
		if pos in pos2pattern and pos2pattern[pos]=="V": slots=["V12"]
		elif pos in pos2pattern and pos2pattern[pos]=="NV": slots=["NV2"]
		elif pos in pos2pattern and pos2pattern[pos]=="N": slots=["N1"]
		else: slots=[None]
	else:
		for x,f in enumerate(feats):
			if f in ["NV"]:	# original: NF.V
				if pos=="V": 
					slots[x]="V12"		# assume that nominalization is morphological rather than lexical
					if(not valid(feats,slots)[0]):
						slots[x]="NV2"	
				else: 
					slots[x]="NV2"
					if(not valid(feats,slots)[0]):
						slots[x]="V12"	#	internal argument of a nominalized clause
			elif f in "V":
				if pos in pos2pattern and pos2pattern[pos] in ["NV","N"]:
					slots[x]="NV2"
				else:
					slots[x]="V12"				
			elif f in nouns : slots[x]="N1"
			elif f in ["1-PL-POSS", "1-SG-POSS", "2-PL-POSS", "2-SG-POSS", "3-PL-POSS", "3-SG-H-POSS", "3-SG-NH-POSS","3-NH-POSS","DEM2"]: slots[x]="N3"
			elif f in ["ORD"]: slots[x]="N4"
			elif f in ["ABS","ADV","DAT-H","DAT-NH","EQU","ERG","GEN","L2-H","L2-NH","L3-H","L3-NH","L4"]: slots[x]="N5"
			elif f in ["EXCEPT","COP-1-PL", "COP-1-SG", "COP-2-PL","COP-3-SG","COP-3-PL"]: slots[x]="N6"
			elif f in ["ANT", "MOD1","MOD"]: slots[x]="V1"
			elif f in ["MOD2","MOD3","MOD4","MOD5","MOD6","MOD7","FIN"]: slots[x]="V2"
			elif f in ["COOR"]: slots[x]="V3"
			elif f in ["VEN"]: slots[x]="V4"
			elif f in ["MID","3-NH"]: slots[x]="V5"
			elif f in ["1-SG","2-SG","3-SG","3-SG-H","3-SG-NH"]: slots[x]="V6"
			elif f in ["L1-SYN","L2-SYN"]: slots[x]="V10"
			elif f in ["3-PL-H-P", "3-SG-H-A", "3-SG-H-L3", "3-SG-H-P", "3-SG-NH-A","3-SG-NH-L3","3-SG-NH-P"]: slots[x]="V11"
			elif f in ["COP","V.PL","V"]: slots[x]="V12"
			elif f in ["1-PL-A", "1-PL-S", "1-SG-S", "2-PL", "2-PL-A","2-PL-S","2-SG-P","3-PL-A","3-PL-P","3-SG-P","3-SG-S","3-SG-S-OB","3-PL-S"]: slots[x]="V14"
			elif f in ["DAT"]:
				if pos in nouns or nominalized(feats,slots): 
					slots[x]="N5"
					if(not valid(feats,slots)[0]):
						slots[x]="V7"	#	internal argument of a nominalized clause
				elif pos in ["V"]: 
					slots[x]="V7"
					if(not valid(feats,slots)[0]):
						slots[x]="N5"	#	unmarked nominalization
			elif f in ["COM"]:
				if pos in nouns or nominalized(feats,slots): slots[x]="N5"
				elif pos in ["V"]: 
					slots[x]="V8"
					if(not valid(feats,slots)[0]):
						slots[x]="N5"	#	unmarked nominalization
			elif f in ["ABL","TERM"]:
				if pos in nouns or pos in ["NU"] or nominalized(feats,slots): slots[x]="N5"
				elif pos in ["V"]: 
					slots[x]="V9"
					if(not valid(feats,slots)[0]):
						slots[x]="N5"	#	unmarked nominalization
			elif f in ["L1","L2","L3"]:
				if pos in nouns or nominalized(feats,slots) or pos in ["NU"]: 
					slots[x]="N5"
					if(not valid(feats,slots)[0]):
						slots[x]="V10"	#	internal argument of a nominalized clause
				elif pos in ["V"]: 
					slots[x]="V10"
					if(not valid(feats,slots)[0]):
						slots[x]="N5"	#	unmarked nominalization
			elif f in ["PL"]:
				if pos in nouns or  nominalized(feats,slots): slots[x]="N4"
				elif pos in ["V"]: slots[x]="V13"

			# V14/16 disambiguation: pre- and post-verbal
			if f in ["1-PL","3-PL"]: 
				if "V12" in slots: slots[x]="V14"
				else: slots[x]="V6"
			if f in ["1-SG-A","2-SG-A","3-SG-A"]:
				if "V12" in slots: slots[x]="V14"
				else: slots[x]="V11"
				
			# NV vs. NF feats
			if f in ["NEG"]:
				if "NV" in feats: slots[x]="NV1"
				else: slots[x]="V1"
			if f in ["STEM","STEM-RDP"]:
				if "NV" in feats: slots[x]="NV2"
				else: slots[x]="V12"
			if f in ["SUB"]:
				if "NV2" in slots: slots[x]="NV4"
				else: slots[x]="V15"
	
	# replacing value in stem slots with main word POS
	head=None
	if len(slots)==1:
		head=0
	for slot in ["N1", "V12", "NV2", "NV1" ]:
		if head==None and slot in slots:
			head=slots.index(slot)
	# "NV2" is head of "adjective"
	# "NV1" is either negation (of "adjective") or head of verbal noun
	
	# sync overal POS and head pos
	if head==None and pos in nouns:
		head=0
		if "V" in feats or "NV" in feats:
			slots=["NV2"]+slots
		else:
			slots=["N1"]+slots
		feats=[pos]+feats

	# feature fixes
	## royal
	if slots==[None]:
		if pos=="NU": slots=["NV2"]								# royal
		elif pos in ["X","CC","CNJ","L"]: slots=["N1"]		# royal: just assert everything we don't know is nominal
		head=0
		
	if(len(feats)==0):
		feats=[pos]
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
		
	# validate slots
	
	if None in slots:
		sys.stderr.write("warning: unknown gloss "+feats[slots.index(None)]+"\nslot analysis: "+".".join([str(x) for x in feats])+" (slots "+".".join([str(x) for x in slots ])+")\n")
		sys.stderr.flush()
		while(None in slots):
			feats.pop(slots.index(None))
			slots.pop(slots.index(None))
	
	v,msg=valid(feats,slots)
	if(not v):
		# The only invalid gloss we found is from automated glossing: N.L1.3-SG-H-A.V.3-PL. This is an incorrect concatenation.
		# We use POS as an orientation to strip that down to a valid tag. No guarantees.
		sys.stderr.write("warning: validity error in "+".".join(feats)+":\n"+str(msg)+"\n")
		sys.stderr.flush()
		while(pos=="V" and not valid(feats,slots)[0]) and "V12" in slots:	# we use POS as a trigger to strip invalid parts
			feats.pop(0)
			slots.pop(0)
		while(not valid(feats,slots)[0] and ("V12" in slots or "NV2" in slots or "NV1" in slots or "N1" in slots)):
			feats.pop()
			slots.pop()
		
	try:
		get_head(slots)
	except Exception as e:
		sys.stderr.write("warning: no head found in "+".".join(slots)+", trying to recover\n")
		sys.stderr.flush()
		s="N1"
		f="N"
		try:
			pattern=re.sub(r"[0-9].*","",slots[0])
			if(pattern=="V"):
				s="V12"
			if(pattern=="NV"):
				s="NV2"
		except:
			pass
		while(len(slots)>0 and not(valid([pos]+feats,[s]+slots)[0])):
			slots.pop(0)
			feats.pop(0)
		slots=[s]+slots
		feats=[pos]+feats
		
	try:
		if(not pattern_validation(slots,pos)):
			sys.stderr.write("pattern validation failed for "+".".join(slots)+"\n")
			sys.stderr.flush()
			feats,slots=enforce_pattern(feats,slots,pos)			
	except Exception as e:
		sys.stderr.write("pattern validation error for "+".".join(slots)+": ",str(e)+"\n")		
		sys.stderr.flush()
		
	result=".".join([s+"="+f for (s,f) in zip(slots,feats)])
		
	# head is N1 (if present), V12 (if present), NV2 (if present), NV1 (otherwise) or the first element
	# the head tag is *not* the one of the morphological analysis, but that of the overall pos annotation
	return result

# return index of head from slots
def get_head(feats_or_slots,pos=""):
	if len(feats_or_slots)==0:
		raise Exception("get_head() called with empty argument")
		
	if type(feats_or_slots)==list:	# expect it a list of slots
		slots=feats_or_slots
		if(len(slots)==1):
			return 0
		heads=["N1", "V12", "NV2", "NV1"]
		for s in heads:
			if s in slots:
				return slots.index(s)
		raise Exception("get_head("+(str(slots))+") apparently not called with a list of slots, expected one of "+",".join(heads))
	
	if(type(feats_or_slots)==str):
		feats=feats_or_slots		
		if not "=" in feats:
			return(get_head(get_slots(feats,pos)))
		else:
			feats=feats.split(".")
			feats=[re.sub("=.*","",f).strip() for f in feats]
			return get_head(feats)
			
	raise Exception("get_head("+str(feats_or_slots)+") must be called with feat string, list of slot=gloss feats or list of slots")

if __name__ == "__main__":
    # execute only if run as a script

	sys.stderr.write("read two-column data (POS<TAB>FEATS) of Sumerian/MTAAC annotation from stdin, infer slots\n")
	sys.stderr.write("note that POS is optional and can be left empty, but the <TAB> before FEATS is required\n")
	sys.stderr.flush()
	pos2pattern2freq={}
	# read feats from stdin
	for line in sys.stdin:
		line=line.rstrip()
		fields=line.split("\t")
		pos=fields[0]
		
		feats=fields[1]
		if feats=="":
			feats=pos
			
		# to eval impact of pos
		#print(pos,feats,get_slots(feats),get_slots(feats,pos),sep="\t")

		feats=get_slots(feats,pos)
		print(line+"\t"+feats)
		p=re.sub(r"[0-9]*=.*","",feats)
		if not pos in pos2pattern2freq:
			pos2pattern2freq[pos] = { p : 1 }
		elif not p in pos2pattern2freq[pos]:
			pos2pattern2freq[pos][p] = 1
		else:
			pos2pattern2freq[pos][p]+=1

	print()
	
	for pos in sorted(pos2pattern2freq):
		for p in sorted(pos2pattern2freq[pos]):
			print(pos,p,pos2pattern2freq[pos][p],sep="\t")
		
	# tests:
	# cat mtaac-morph/*conll | cut -f 4 | egrep '\.' | grep -v '#' | perl -pe 's/^[_\.]*//g; s/^([^\.]?N[^\.]*)?/$1\t$1/g; s/^\t(ABL)/N\t$1/; s/^(NEG|ANT)?\t/V\t/; s/^NF\t/NV\t/g' | sort -u | python3 Slotty.py