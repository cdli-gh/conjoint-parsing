# Test data on conjoint parsing of Sumerian morphology and dependency syntax

(Note: This is sandbox data for developing a parser, in preparation of a Google Summer of Code or student project, but this is not a release candidate for any kind of corpus data. If you're looking for this, see [here](https://github.com/cdli-gh/mtaac_gold_corpus) for morphology [this is a stable release version] and [here](https://github.com/cdli-gh/mtaac_syntax_corpus) for syntax [this is still under development]. The data here won't be updated.)

To a large extent, Sumerian clausal syntax is morphologically expressed at the verb, e.g., in polypersonal agreement and dimensional affixes (that indicate semantic roles other than direct arguments). This information, even though incomplete due to idiosyncrasies of the writing system and spelling conventions) is essential for parsing, because it helps to disambiguate the attachment of nominal arguments. Similarly, nominal inflection indicates the grammatical role of the inflected noun, but also that of its parent(s). For successful dependency parsing, it is thus beneficial to perform conjoint parsing for/disambiguation of inflectional morphology and syntactic dependencies.

In this repository, we gather training, test and gold data, code for training and evaluating parsers, and scripts for data preprocessing and evaluation.
