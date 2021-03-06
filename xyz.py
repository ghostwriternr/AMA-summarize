from nltk.tokenize import RegexpTokenizer
from stop_words import get_stop_words
from nltk.stem.porter import PorterStemmer
from gensim import corpora, models
import gensim

import sys
import glob
import re
import htmlentitydefs
from nltk.tokenize import RegexpTokenizer
from stop_words import get_stop_words
from nltk.stem.porter import PorterStemmer
from gensim import corpora, models
# from nltk.tokenize import StanfordTokenizer
import gensim
######################################################################
# The following strings are components in the regular expression
# that is used for tokenizing. It's important that phone_number
# appears first in the final regex (since it can contain whitespace).
# It also could matter that tags comes after emoticons, due to the
# possibility of having text like
#
#     <:| and some text >:)
#
# Most imporatantly, the final element should always be last, since it
# does a last ditch whitespace-based tokenization of whatever is left.

# This particular element is used in a couple ways, so we define it
# with a name:
emoticon_string = r"""
    (?:
      [<>]?
      [:;=8]                     # eyes
      [\-o\*\']?                 # optional nose
      [\)\]\(\[dDpP/\:\}\{@\|\\] # mouth      
      |
      [\)\]\(\[dDpP/\:\}\{@\|\\] # mouth
      [\-o\*\']?                 # optional nose
      [:;=8]                     # eyes
      [<>]?
    )"""

# The components of the tokenizer:
regex_strings = (
    # Phone numbers:
    r"""
    (?:
      (?:            # (international)
        \+?[01]
        [\-\s.]*
      )?            
      (?:            # (area code)
        [\(]?
        \d{3}
        [\-\s.\)]*
      )?    
      \d{3}          # exchange
      [\-\s.]*   
      \d{4}          # base
    )"""
    ,
    # Emoticons:
    emoticon_string
    ,    
    # HTML tags:
     r"""<[^>]+>"""
    ,
    # Twitter username:
    r"""(?:@[\w_]+)"""
    ,
    # Twitter hashtags:
    r"""(?:\#+[\w_]+[\w\'_\-]*[\w_]+)"""
    ,
    # Remaining word types:
    r"""
    (?:[a-z][a-z'\-_]+[a-z])       # Words with apostrophes or dashes.
    |
    (?:[+\-]?\d+[,/.:-]\d+[+\-]?)  # Numbers, including fractions, decimals.
    |
    (?:[\w_]+)                     # Words without apostrophes or dashes.
    |
    (?:\.(?:\s*\.){1,})            # Ellipsis dots. 
    |
    (?:\S)                         # Everything else that isn't whitespace.
    """
    )

######################################################################
# This is the core tokenizing regex:
    
word_re = re.compile(r"""(%s)""" % "|".join(regex_strings), re.VERBOSE | re.I | re.UNICODE)

# The emoticon string gets its own regex so that we can preserve case for them as needed:
emoticon_re = re.compile(regex_strings[1], re.VERBOSE | re.I | re.UNICODE)

# These are for regularizing HTML entities to Unicode:
html_entity_digit_re = re.compile(r"&#\d+;")
html_entity_alpha_re = re.compile(r"&\w+;")
amp = "&amp;"

######################################################################

class Tokenizer:
    def __init__(self, preserve_case=False):
        self.preserve_case = preserve_case

    def tokenize(self, s):
        """
        Argument: s -- any string or unicode object
        Value: a tokenize list of strings; conatenating this list returns the original string if preserve_case=False
        """        
        # Try to ensure unicode:
        try:
            s = unicode(s)
        except UnicodeDecodeError:
            s = str(s).encode('string_escape')
            s = unicode(s)
        # Fix HTML character entitites:
        s = self.__html2unicode(s)
        # Tokenize:
        words = word_re.findall(s)
        # Possible alter the case, but avoid changing emoticons like :D into :d:
        if not self.preserve_case:            
            words = map((lambda x : x if emoticon_re.search(x) else x.lower()), words)
        return words

    def tokenize_random_tweet(self):
        """
        If the twitter library is installed and a twitter connection
        can be established, then tokenize a random tweet.
        """
        try:
            import twitter
        except ImportError:
            print "Apologies. The random tweet functionality requires the Python twitter library: http://code.google.com/p/python-twitter/"
        from random import shuffle
        api = twitter.Api()
        tweets = api.GetPublicTimeline()
        if tweets:
            for tweet in tweets:
                if tweet.user.lang == 'en':            
                    return self.tokenize(tweet.text)
        else:
            raise Exception("Apologies. I couldn't get Twitter to give me a public English-language tweet. Perhaps try again")

    def __html2unicode(self, s):
        """
        Internal metod that seeks to replace all the HTML entities in
        s with their corresponding unicode characters.
        """
        # First the digits:
        ents = set(html_entity_digit_re.findall(s))
        if len(ents) > 0:
            for ent in ents:
                entnum = ent[2:-1]
                try:
                    entnum = int(entnum)
                    s = s.replace(ent, unichr(entnum))  
                except:
                    pass
        # Now the alpha versions:
        ents = set(html_entity_alpha_re.findall(s))
        ents = filter((lambda x : x != amp), ents)
        for ent in ents:
            entname = ent[1:-1]
            try:            
                s = s.replace(ent, unichr(htmlentitydefs.name2codepoint[entname]))
            except:
                pass                    
            s = s.replace(amp, " and ")
        return s

###############################################################################

# if __name__ == '__main__':
#     tok = Tokenizer(preserve_case=False)
#     samples = (
#         u"RT @ #happyfuncoding: this is a typical Twitter tweet :-)",
#         u"HTML entities &amp; other Web oddities can be an &aacute;cute <em class='grumpy'>pain</em> >:(",
#         u"It's perhaps noteworthy that phone numbers like +1 (800) 123-4567, (800) 123-4567, and 123-4567 are treated as words despite their whitespace."
#         )

#     for s in samples:
#         print "======================================================================"
#         print s
#         tokenized = tok.tokenize(s)
#         print "\n".join(tokenized)
tok = Tokenizer(preserve_case=False)
#en_stop = get_stop_words('en')

# Create p_stemmer of class PorterStemmer
p_stemmer = PorterStemmer()
tokenizer = RegexpTokenizer(r'\w+')

# create English stop words list
en_stop = get_stop_words('en')

# Create p_stemmer of class PorterStemmer
p_stemmer = PorterStemmer()
    

doc_new_set = []
doc_test_set = []

path = './data/tech1/*.txt'
files = glob.glob(path) 
doc_name=[]
print files 
for name in files[0:]: # 'file' is a builtin type, 'name' is a less-ambiguous variable name.
    try:
        doc_name.append(name)
        # print name
        with open(name) as f: # No need to specify 'r': this is the default.
            doc_new_set.append(f.read())
    except IOError as exc:
        if exc.errno != errno.EISDIR: # Do not fail if a directory is found, just ignore it.
            raise # Propagate other kinds of IOError.


for name in files[0:]: # 'file' is a builtin type, 'name' is a less-ambiguous variable name.
    try:
        with open(name) as f: # No need to specify 'r': this is the default.
            doc_test_set.append(f.read())
    except IOError as exc:
        if exc.errno != errno.EISDIR: # Do not fail if a directory is found, just ignore it.
            raise # Propa


# print len(doc_new_set)
print len(doc_test_set)
# print doc_new_set
# list for tokenized documents in loop
texts = []
texts_test = []

# loop through document list
for i in doc_new_set:
    
    # clean and tokenize document string
    raw = i.lower()
    tokens = tok.tokenize(raw)

    # remove stop words from tokens
    stopped_tokens = [i for i in tokens if not i in en_stop]
    
    # stem tokens
    stemmed_tokens = [p_stemmer.stem(i) for i in stopped_tokens]
    stemmed_tokens= [j for j in stemmed_tokens if len(j)>1]
    # add tokens to list
    texts.append(stemmed_tokens)


# turn our tokenized documents into a id <-> term dictionary
dictionary = corpora.Dictionary(texts)
    
# convert tokenized documents into a document-term matrix
corpus = [dictionary.doc2bow(text) for text in texts]

for i in doc_test_set:
    
    # clean and tokenize document string
    raw = i.lower()
    tokens = tok.tokenize(raw)

    # remove stop words from tokens
    stopped_tokens = [i for i in tokens if not i in en_stop]
    
    # stem tokens
    stemmed_tokens = [p_stemmer.stem(i) for i in stopped_tokens]
    stemmed_tokens= [j for j in stemmed_tokens if len(j)>1]
    # add tokens to list
    texts_test.append(stemmed_tokens)

# turn our tokenized documents into a id <-> term dictionary
dictionary_test = corpora.Dictionary(texts_test)
    
# convert tokenized documents into a document-term matrix
corpus_test = [dictionary_test.doc2bow(text) for text in texts_test]

# generate LDA model
# ldamodel = gensim.models.LdaMulticore(corpus, num_topics=10, id2word = dictionary, passes=200,workers=7)
ldamodel=gensim.models.ldamodel.LdaModel.load('ldaNew.model')
# ldamodel.save('ldaNew.model')

#print (corpus[0])
K = ldamodel.num_topics
# doc_f_bow = dictionary.doc2bow(doc_f.lower().split())
a = list((ldamodel[corpus_test]))
print a
print '\n'
count=0
for i in a:
    print doc_name[count]
    i = list(sorted(i, key=lambda x: x[1]))
    print i[-1]
    print '\n'
    print ldamodel.print_topic(i[-1][0])
    print '\n'
    count=count+1
# topicWordProbMat = ldamodel.print_topics(K)
# print K
# print topicWordProbMat
