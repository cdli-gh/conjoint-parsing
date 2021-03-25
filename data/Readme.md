# Conjoint morphological and syntactic (dependency) parsing for Sumerian

To a large extent, Sumerian clausal syntax is morphologically expressed at the verb, e.g., in polypersonal agreement and dimensional affixes (that indicate semantic roles other than direct arguments). This information, even though incomplete due to idiosyncrasies of the writing system and spelling conventions) is essential for parsing, because it helps to disambiguate the attachment of nominal arguments. Similarly, nominal inflection indicates the grammatical role of the inflected noun, but also that of its parent(s). For successful dependency parsing, it is thus beneficial to perform conjoint parsing for/disambiguation of inflectional morphology and syntactic dependencies.

## Data directories

- `classical/` 
	CDLI-CoNLL data, one word per line, 8 tab-separated columns: ID WORD SEGM POS MORPH HEAD EDGE MISC
	- `classical/royal` (tokens: train 7.500, dev 750, test 1.000)

		royal subcorpus with syntax annotations, mirror of https://github.com/cdli-gh/mtaac_syntax_corpus/tree/master/royal/release
		
		train/dev/test split corresponds to [Ur III corpus](https://github.com/cdli-gh/mtaac_cdli_ur3_corpus/blob/master/ur3_corpus_data/corpus_split_20180418-225438.json)
	- `classical/parallel` (tokens: train 35.000, dev 5.500, test 5.500)
		
		parallel subcorpus with projected annotations, mirror of https://github.com/cdli-gh/mtaac_syntax_corpus/tree/master/parallel/consolidated
		
		train/dev/test split corresponds to [Ur III corpus](https://github.com/cdli-gh/mtaac_cdli_ur3_corpus/blob/master/ur3_corpus_data/corpus_split_20180418-225438.json)
	- `classical/royal-synth` (tokens: train 41.000, dev 8.250, test 1.000)
		
		synthetic corpus generated from royal corpus, using [Synthy.py](scripts/Synthy.py)
		- test corresponds to `classical/royal`
		- dev corresponds to `classical/royal/dev` and `classical/royal/train`
		- train is generated from `classical/royal/train` and `classical/royal/dev` using Synthy, with replacements from parallel corpus (excl. test) and royal corpus (excl. test)
		
		generated in `classical/` using the command: `python3 ../scripts/Synthy.py 35000 royal/train.conll royal/dev.conll -support parallel/dev.conll parallel/train.conll > royal-synth/train.conll`		
		
- `expanded/`
	
	CDLI-CoNLL data with one morpheme (slot) per line, otherwise following CDLI/MTAAC conventions
	the morphological head carries the original dependency and POS annotation
	
	In the expanded version, one line represents a word *or a morpheme* (or the position [slot] that a morpheme could occupy). Annotations for words (morphological heads) remain largely unchanged, except that HEAD indices are updated.
	
	Morphological slots use the slot identifier as value of the POS column, depend on the morphological head or its syntactic parent, and use the morphological gloss as dependency.
	
	This data is created from classical CDLI-CoNLL using default parameters of `Deppy.py`

## Evaluation routine

- Note that all annotated data was created semi-automatically, using different methods. They do contain errors. The idea of conjoint training over two subcorpora is that the respective errors will balanced out. This is why we need additional manual evaluation.
- As for quantitative evaluation, please adhere to the following procedure
	- For any given parser, please train and evaluate parsers in three settings:
		- train and evaluate on `classical` data sets (syntactic parsing only)
		- train and evaluate on `expanded` data sets (conjoint syntactic and morphological parsing)
		- train on `expanded` data sets, remove lines with slot information, update ID/HEAD, evaluate on `classical` data sets (to evaluate conjoint parsing against syntactic baseline)
	- As for the data sets, please train and evaluate parsers in five different settings:
		- train on `parallel`, evaluate on `parallel/test` and `royal/test`
		- train on `royal`, evaluate on `royal/test` and `parallel/test`
		- train on `royal-synth`, evaluate on `royal-synth/test` and `parallel/test`: Possible that synthetic data improves parsing performance.
		- train on `royal-synth` and `parallel`, evaluate on `royal/test` and `parallel/test` separately. The difference is that this uses synthetic data to balance training corpus size between royal and parallel.
		- train on `royal` and `parallel`, evaluate on `royal/test` and `parallel/test` separately. This is to check whether synthetic data hurts or improves performance on the royal corpus, in particular.
- For every parser, we have to run up 15 (3x5) trainings and 30 (3x10) evaluations. Start with/Prioritize training and evaluation on `expanded` and on conjoint training on `royal+parallel`.
- As for evaluation metrics, we use Labelled Attachment Score (LAS), Unlabelled Attachment Score (UAS) and Label Score (LS). The focus is on LAS. UAS and LS are only diagnostics to identify sources of errors. When reporting Labelled Attachment Score, please report it globally, for every part of speech individually and for every predicted dependency individually.

## `scripts/`

- `Synthy.py`

	takes a CDLI-CoNLL corpus and generates synthetic training data by randomly replacing words that are morphologically equivalent

	note that the syntactic structure remains untouched. Do not evaluate against data taken as input to Synthy.

	On royal corpus, about 50% of all words are being replaced.

- `Slotty.py`

	small script to augment MTAAC morphology annotations to ETCSRI-style morphology annotations: infer slot information (see below)

	tested for mtaac-morph.feats (manual MTAAC annotations), royal.feats (converted Ur-III subset from ETCSRI) and full.feats (automatic annotation of the MTAAC Ur-III corpus, trained on MTAAC and the royal subcorpus)
	
- `Deppy.py`

	small script that uses Slotty to expand morphological glosses into the expanded format.

	Note that it performs a heuristic perculation of morphological dependents to the syntactic head.

- `Heady.py`

	small script to reduce expanded CDLI-CoNLL files (as produced by Deppy.py) to syntax annotations only
	(this reverts Deppy.py)
	
## Sumerian slot grammar

Sumerian grammar is organized in slots that (can) convey morphemes that express specific aspects of grammatical function, respectively. 

verbal, finite (https://cdli-gh.github.io/guides/verbal_chain_slot_system.html)

	V1=NEG|MOD1|ANT|STEM|STEM-PL|STEM-RDP
		RDP 	Reduplicated Stem
		PL 	Plural (stems with special plural forms)
	V2=MOD2|MOD3|MOD4|MOD5|MOD6|MOD7|FIN|FIN-L1|FIN-L2|FIN|FIN-L2|FIN
	V3=COOR
	V4=VEN
	V5=MID|3-NH
	V6=1-SG|2-SG|3-SG-H|1-PL|3-PL
	V7=DAT
	V8=COM
	V9=ABL|TERM
	V10=L1|LOC-OB|L1-SYN|L2|L2-SYN|L3
	V11=1-SG-A|2-SG-A|3-SG-H-A|3-SG-H-P|3-SG-H-L3|1-SG-A-OB|3-SG-NH-A|3-SG-NH-P|3-SG-NH-L3|3-PL-H-P
	V12=V|V-PF|V.PL|V.PL|COP
		V 	Verb
		PF 	Present-Future (stems with special Maru forms)
		PL 	Plural (stems with special plural forms)
	V13=PL|PLEN
	V14=1-SG-A|1-SG-S|1-SG-P|2-SG-A|2-SG-S|2-SG-P|3-SG-S|3-SG-P|3-SG-A|3-SG-S-OB|1-PL-A|1-PL-S|1-PL|2-PL-A|2-PL-S|2-PL|3-PL-S|3-PL-P|3-PL|3-PL-A
	V15=SUB
		
verbal, non-finite (oracc.museum.upenn.edu/etcsri/parsing, https://cdli-gh.github.io/guides/verbal_chain_slot_system.html)

	?NF 	Non-Finite
	?ABS 	Absolute marker (Non-Finite only)
	?PT 	Preterite marker (Non-Finite only)
	?F 	Future marker (Non-Finite only)

	NV1=NEG
	NV2=STEM|STEM-PF|STEM-RDP|STEP-PL
	NV3=PF
	NV4=SUB
	N2=DEM
	N3=1-SG-POSS|2-SG-POSS|3-SG-H-POSS|3-SG-NH-POSS|DEM2|1-PL-POSS|2-PL-POSS|3-PL-POSS
	N4.0=PL|ORD
	N5.0=ABS|ERG|DAT-H|DAT-NH|COM|ABL|TERM|L1|L2-H|L2-NH|L3-H|L3-NH|GEN|EQU|L4|ADV
	N4.1=PL|ORD	# of parent
	N5.1=ABS|ERG|DAT-H|DAT-NH|COM|ABL|TERM|L1|L2-H|L2-NH|L3-H|L3-NH|GEN|EQU|L4|ADV
	N4.2=PL|ORD	# of grand-parent
	N5.2=ABS|ERG|DAT-H|DAT-NH|COM|ABL|TERM|L1|L2-H|L2-NH|L3-H|L3-NH|GEN|EQU|L4|ADV
	N6=COP-1-SG|COP-2-SG|COP-3-SG|COP-1-PL|COP-2-PL|COP-3-PL|EXCEPT
	
Nominal (oracc.museum.upenn.edu/etcsri/parsing)

	N1=N
	N2=DEM
	N3=1-SG-POSS|2-SG-POSS|3-SG-H-POSS|3-SG-NH-POSS|DEM2|1-PL-POSS|2-PL-POSS|3-PL-POSS
	N4.0=PL|ORD
	N5.0=ABS|ERG|DAT-H|DAT-NH|COM|ABL|TERM|L1|L2-H|L2-NH|L3-H|L3-NH|GEN|EQU|L4|ADV
	N4.1=PL|ORD	# of parent
	N5.1=ABS|ERG|DAT-H|DAT-NH|COM|ABL|TERM|L1|L2-H|L2-NH|L3-H|L3-NH|GEN|EQU|L4|ADV
	N4.2=PL|ORD	# of grand-parent
	N5.2=ABS|ERG|DAT-H|DAT-NH|COM|ABL|TERM|L1|L2-H|L2-NH|L3-H|L3-NH|GEN|EQU|L4|ADV
	N6=COP-1-SG|COP-2-SG|COP-3-SG|COP-1-PL|COP-2-PL|COP-3-PL|EXCEPT

However, Sumerian morphology is partially reflected in surface forms only, and transcriptions cannot be directly decomposed into morphs because of idiosyncrasies of the writing system. We can thus not provide a reliable morphological segmentation prior to syntactic parsing.

The approach taken here is to create pseudo-tokens for *all* imaginable slots of any given verb or noun, with the word being repeated, and to mark them as being applicable or empty (_). If a full-form re-occurs, a morphological analysis from the training data can be applied (unless overridden by syntactic context). If an unseen form occurs, the syntactic context will override any clues that might be drawn from morphology.
The original POS tag is then applied to the location of the stem, all "copies" of the target word take the slot name as POS and the value as dependency label. Note that the POS serves to disambiguate morphology and syntactic relations where these take the same form (e.g., ERG for the ergative morpheme and the grammatical relation between argument and verb). The head of all slots is the stem. In a future revision, the head of N4.1, N5.1 etc. may be set to the parent, the head of N5.2 to grant-parent, if these can be reliably identified in the gold data. 

original
	ba-zi	MID.V.3-SG-S		
	
expanded	
	1	ba-zi	V1	12	_
	2	ba-zi	V2	12	_
	3	ba-zi	V3	12	_
	4	ba-zi	V4	12	_
	5	ba-zi	V5	12	MID
	6	ba-zi	V6	12	_
	7	ba-zi	V7	12	_
	8	ba-zi	V8	12	_
	9	ba-zi	V9	12	_
	10	ba-zi	V10	12	_
	11	ba-zi	V11	12	_
	12	ba-zi	V	0	root
	13	ba-zi	V13	12	_
	14	ba-zi	V14	12	3-SG-S
	15	ba-zi	V15	12	_

original
	ba-an-na-zi	MID.3-SG-H.DAT.V.3-SG-S		
		
expanded		
	1	ba-an-na-zi	V1	12	_
	2	ba-an-na-zi	V2	12	_
	3	ba-an-na-zi	V3	12	_
	4	ba-an-na-zi	V4	12	_
	5	ba-an-na-zi	V5	12	MID
	6	ba-an-na-zi	V6	12	3-SG-H
	7	ba-an-na-zi	V7	12	DAT
	8	ba-an-na-zi	V8	12	_
	9	ba-an-na-zi	V9	12	_
	10	ba-an-na-zi	V10	12	_
	11	ba-an-na-zi	V11	12	_
	12	ba-an-na-zi	V	0	root
	13	ba-an-na-zi	V13	12	_
	14	ba-an-na-zi	V14	12	3-SG-S
	15	ba-an-na-zi	V15	12	_

original

	szul-e2-du3-du3-e 	PN.ERG
	szu 	N.L3-NH
	ba-ti 	MID.3-SG-H-A.V.3-SG-P

expanded
	1	szul-e2-du3-du3-e 	PN	32	ERG
	2	szul-e2-du3-du3-e 	N2	1	_
	3	szul-e2-du3-du3-e 	N3	1	_
	4	szul-e2-du3-du3-e 	N4.0	1	_
	5	szul-e2-du3-du3-e 	N5.0	1	ERG
	6	szul-e2-du3-du3-e 	N4.1	1	_
	7	szul-e2-du3-du3-e 	N5.1	1	_
	8	szul-e2-du3-du3-e 	N4.2	1	_
	9	szul-e2-du3-du3-e 	N5.2	1	_
	10	szul-e2-du3-du3-e 	N6	1	_
	11	szu 	N	32	LOC
	12	szu 	N2	11	_
	13	szu 	N3	11	_
	14	szu 	N4.0	11	_
	15	szu 	N5.0	11	L3-NH
	16	szu 	N4.1	11	_
	17	szu 	N5.1	11	_
	18	szu 	N4.2	11	_
	19	szu 	N5.2	11	_
	20	szu 	N6	11	_
	21	ba-ti 	V1	32	_
	22	ba-ti 	V2	32	_
	23	ba-ti 	V3	32	_
	24	ba-ti 	V4	32	_
	25	ba-ti 	V5	32	MID
	26	ba-ti 	V6	32	_
	27	ba-ti 	V7	32	_
	28	ba-ti 	V8	32	_
	29	ba-ti 	V9	32	_
	30	ba-ti 	V10	32	_
	31	ba-ti 	V11	32	3-SG-H-A
	32	ba-ti 	V	0	root
	33	ba-ti 	V13	32	_
	34	ba-ti 	V14	32	3-SG-P
	35	ba-ti 	V15	32	_

	
On this basis, then, a conventional syntactic parser can be trained, taking WORD and POS columns as input, and predicting HEAD and DEP columns. Its output is, however, to be simplified prior to evaluation in that the "dependency labels" of morphemes are aggregated into a single, .-separated gloss and indexing is to be updated. Evaluation should be conducted over morphological parsing (aggregated), unlabelled dependencies (aggregated) and labelled dependencies (aggregated) separately and compared with plain dependency parsing (without expansion, without morphological features, same parser) and lookup-based morphological glossing (https://github.com/cdli-gh/glosser).

Future refinements may include using the correct attachment of nominal case (to parents, grant-parents, etc.) and more sophisticated ways for morphological segmentation.
