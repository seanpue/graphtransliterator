#!/usr/bin/env python
# coding: utf-8

# In[1]:


from graphtransliterator import GraphTransliterator


# In[2]:


yaml_ = """
  tokens:
    a: [vowel]               # type of token ("a") and its class (vowel)
    bb: [consonant, b_class] # type of token ("bb") and its classes (consonant, b_class)
    ' ': [wb]                # type of token (" ") and its class ("wb", for wordbreak)
  rules:
    a: A       # transliterate "a" to "A"
    bb: B      # transliterate "bb" to "B"
    a a: <2AS> # transliterate ("a", "a") to "<2AS>"
    ' ': ' '   # transliterate ' ' to ' '
  whitespace:
    default: " "        # default whitespace token
    consolidate: false  # whitespace should not be consolidated
    token_class: wb     # whitespace token class
"""
gt_one = GraphTransliterator.from_yaml(yaml_)
gt_one.transliterate('a')


# In[3]:


gt_one.transliterate('bb')


# In[4]:


gt_one.transliterate('aabb')


# In[5]:


gt_one.tokenize('abba')


# In[6]:


yaml_ = """
  tokens:
    a: []      # "a" token with no classes
    aa: []     # "aa" token with no classes
    ' ': [wb]  # " " token and its class ("wb", for wordbreak)
  rules:
    aa: <DOUBLE_A>  # transliterate "aa" to "<DOUBLE_A>"
    a: <SINGLE_A>   # transliterate "a" to "<SINGLE_A>"
  whitespace:
    default: " "        # default whitespace token
    consolidate: false  # whitespace should not be consolidated
    token_class: wb     # whitespace token class
"""
gt_two = GraphTransliterator.from_yaml(yaml_)
gt_two.transliterate('a')


# In[7]:


gt_two.transliterate('aa')


# In[8]:


gt_two.transliterate('aaa')


# In[9]:


gt_two.tokens


# In[10]:


yaml_ = """
  tokens:
    a: []
    b: []
    c: [class_of_c]
    ' ': [wb]
  rules:
    a: <<A>>
    a b: <<AB>>
    b: <<B>>
    c: <<C>>
    ' ': _
    <class_of_c> a b: <<AB_after_C>>
  whitespace:
    default: " "
    consolidate: false
    token_class: wb
"""
gt_three = GraphTransliterator.from_yaml(yaml_)
gt_three.transliterate("ab")  # should match rule "a b"


# In[11]:


gt_three.transliterate("cab") # should match rules: "c", and "<class_of_c> a b"


# In[12]:


gt_three.rules


# In[13]:


yaml_ = """
  tokens:
    a: []
    ' ': [wb]
  rules:
    <wb> a: _A
    a <wb>: A_
    <wb> a <wb>: _A_
    a: a
    ' ': ' '
  whitespace:
    default: " "        # default whitespace token
    consolidate: true   # whitespace should be consolidated
    token_class: wb     # whitespace token class
"""
gt = GraphTransliterator.from_yaml(yaml_)
gt.transliterate('a')   # whitespace present at start of string


# In[14]:


gt.transliterate('aa')  # whitespace present at start and end of string


# In[15]:


gt.transliterate(' a')  # consolidate removes whitespace at start of string


# In[16]:


gt.transliterate('a ')  # consolidate removes whitespace at end of string


# In[17]:


gt.whitespace


# In[18]:


yaml_ = """
  tokens:
    a: [vowel]
    ' ': [wb]
  rules:
    a: A
    ' ': ' '
  whitespace:
    default: " "
    consolidate: false
    token_class: wb
  onmatch_rules:
    - <vowel> + <vowel>: ',' # add a comma between vowels
 """
gt = GraphTransliterator.from_yaml(yaml_)
gt.transliterate('aa')


# In[19]:


gt.onmatch_rules


# In[20]:


yaml_ = """
  tokens:
    a: []
    ' ': [wb]
  rules:
    a: A
    ' ': ' '
  whitespace:
    default: " "
    consolidate: false
    token_class: wb
  metadata:
    author: Author McAuthorson
    version: 0.1.1
    description: A sample Graph Transliterator
  """
gt = GraphTransliterator.from_yaml(yaml_)
gt.metadata


# In[21]:


yaml_ = """
  tokens:
    b: []
    c: []
    ' ': [wb]
  rules:
    b: \N{LATIN CAPITAL LETTER B}
    c: \u0043    # hexadecimal Unicode character code for 'C'
    ' ': ' '
  whitespace:
    default: " "
    consolidate: false
    token_class: wb
  """
gt = GraphTransliterator.from_yaml(yaml_)
gt.transliterate('b')


# In[22]:


gt.transliterate('c')


# In[23]:


settings = {
  'tokens': {'a': ['vowel'],
             ' ': ['wb']},
  'rules': [
      {'production': 'A', 'tokens': ['a']},
      {'production': ' ', 'tokens': [' ']}],
  'onmatch_rules': [
      {'prev_classes': ['vowel'],
       'next_classes': ['vowel'],
       'production': ','}],
  'whitespace': {
      'default': ' ',
      'consolidate': False,
      'token_class': 'wb'},
  'metadata': {
      'author': 'Author McAuthorson'}
}
gt = GraphTransliterator.from_dict(settings)
gt.transliterate('a')


# In[24]:


get_ipython().run_line_magic('xmode', 'Minimal')


# In[25]:


yaml_ = """
tokens:
  a: [class1, class2]
  b: []
  ' ': [wb]
rules:
  <class1> a: A
  <class2> a: AA # ambiguous rule
  <class1> b: BB
  b <class2>: BB # also ambiguous
whitespace:
  default: ' '
  consolidate: True
  token_class: wb
"""
gt = GraphTransliterator.from_yaml(yaml_)


# In[26]:


GraphTransliterator.from_yaml(
'''
tokens:
  a: []
  ' ': [wb]
rules:
  a: A
  ' ': '_'
whitespace:
  default: ' '
  consolidate: True
  token_class: wb
''').transliterate("a a")


# In[27]:


from graphtransliterator import GraphTransliterator
yaml_ = """
  tokens:
   a: []
   ' ': [wb]
  rules:
    a: A
    ' ': ' '
  whitespace:
    default: " "
    consolidate: true
    token_class: wb
"""
GraphTransliterator.from_yaml(yaml_).transliterate("a!a") # ignore_errors=False


# In[28]:


GraphTransliterator.from_yaml(yaml_, ignore_errors=True).transliterate("a!a") # ignore_errors=True


# In[29]:


yaml_='''
  tokens:
    a: []
    b: []
    ' ': [wb]
  rules:
    a: A
    b (a): B
  whitespace:
    default: ' '
    token_class: wb
    consolidate: False
'''
gt = GraphTransliterator.from_yaml(yaml_)
gt.transliterate("ab")


# In[30]:


gt.ignore_errors = True
gt.transliterate("ab")


# In[31]:


gt = GraphTransliterator.from_yaml('''
        tokens:
            a: []
            a a: []
            ' ': [wb]
        rules:
            a: <A>
            a a: <AA>
        whitespace:
            default: ' '
            consolidate: True
            token_class: wb
''')
tokens = gt.tokenize("aa")
tokens # whitespace added to ends


# In[32]:


gt.match_at(1, tokens) # returns index to rule


# In[33]:


gt.rules[gt.match_at(1, tokens)] # actual rule


# In[34]:


gt.match_at(1, tokens, match_all=True) # index to rules, with match_all


# In[35]:


[gt.rules[_] for _ in gt.match_at(1, tokens, match_all=True)] # actual rules, with match_all


# In[36]:


gt.transliterate("aaa")


# In[37]:


gt.last_matched_rules


# In[38]:


gt.last_matched_rule_tokens


# In[39]:


gt.rules


# In[40]:


gt.pruned_of('<AA>').rules


# In[41]:


gt.pruned_of(['<A>', '<AA>']).rules


# In[42]:


gt = GraphTransliterator.from_yaml(
    """
    tokens:
      a: []
      ' ': [wb]
    rules:
      a: b
      <wb> a: B
      ' ': ' '
    whitespace:
      token_class: wb
      default: ' '
      consolidate: false
    """)
gt.graph


# In[43]:


gt.graph.node


# In[44]:


gt.graph.edge


# In[45]:


gt.graph.edge[0][1]


# In[46]:


gt.graph.edge[1][2]


# In[47]:


gt.graph.edge_list


# In[48]:


gt.graph.node[0]


# In[49]:


gt.graph.node[1]

