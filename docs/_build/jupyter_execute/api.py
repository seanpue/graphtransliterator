#!/usr/bin/env python
# coding: utf-8

# In[1]:


from graphtransliterator import GraphTransliterator, OnMatchRule, TransliterationRule, WhitespaceRules
settings = {'tokens': {'a': {'vowel'}, ' ': {'wb'}}, 'onmatch_rules': [OnMatchRule(prev_classes=['vowel'], next_classes=['vowel'], production=',')], 'rules': [TransliterationRule(production='A', prev_classes=None, prev_tokens=None, tokens=['a'], next_tokens=None, next_classes=None, cost=0.5849625007211562), TransliterationRule(production=' ', prev_classes=None, prev_tokens=None, tokens=[' '], next_tokens=None, next_classes=None, cost=0.5849625007211562)], 'metadata': {'author': 'Author McAuthorson'}, 'whitespace': WhitespaceRules(default=' ', token_class='wb', consolidate=False)}
gt = GraphTransliterator(**settings)
gt.transliterate('a')


# In[2]:


yaml_ = '''
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
  - <vowel> + <vowel>: ','  # add a comma between vowels
metadata:
  author: "Author McAuthorson"
'''
gt = GraphTransliterator.from_yaml(yaml_)
gt.dump()


# In[3]:


yaml_ = '''
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
    - <vowel> + <vowel>: ','  # add a comma between vowels
  metadata:
    author: "Author McAuthorson"
'''
gt = GraphTransliterator.from_yaml(yaml_)
gt.dumps()


# In[4]:


tokens = {
    'ab': ['class_ab'],
    ' ': ['wb']
}
whitespace = {
    'default': ' ',
    'token_class': 'wb',
    'consolidate': True
}
onmatch_rules = [
    {'<class_ab> + <class_ab>': ','}
]
rules = {'ab': 'AB',
         ' ': '_'}
settings = {'tokens': tokens,
            'rules': rules,
            'whitespace': whitespace,
            'onmatch_rules': onmatch_rules}
gt = GraphTransliterator.from_easyreading_dict(settings)
gt.transliterate("ab abab")


# In[5]:


yaml_ = '''
tokens:
  a: [class1]
  ' ': [wb]
rules:
  a: A
  ' ': ' '
whitespace:
  default: ' '
  consolidate: True
  token_class: wb
onmatch_rules:
  - <class1> + <class1>: "+"
'''
gt = GraphTransliterator.from_yaml(yaml_)
gt.transliterate("a aa")


# In[6]:


from collections import OrderedDict
settings =           {'tokens': {'a': ['vowel'], ' ': ['wb']},
 'rules': [OrderedDict([('production', 'A'),
               # Can be compacted, removing None values
               # ('prev_tokens', None),
               ('tokens', ['a']),
               ('next_classes', None),
               ('next_tokens', None),
               ('cost', 0.5849625007211562)]),
  OrderedDict([('production', ' '),
               ('prev_classes', None),
               ('prev_tokens', None),
               ('tokens', [' ']),
               ('next_classes', None),
               ('next_tokens', None),
               ('cost', 0.5849625007211562)])],
 'whitespace': {'default': ' ', 'token_class': 'wb', 'consolidate': False},
 'onmatch_rules': [OrderedDict([('prev_classes', ['vowel']),
               ('next_classes', ['vowel']),
               ('production', ',')])],
 'metadata': {'author': 'Author McAuthorson'},
 'onmatch_rules_lookup': {'a': {'a': [0]}},
 'tokens_by_class': {'vowel': ['a'], 'wb': [' ']},
 'graph': {'edge': {0: {1: {'token': 'a', 'cost': 0.5849625007211562},
    3: {'token': ' ', 'cost': 0.5849625007211562}},
   1: {2: {'cost': 0.5849625007211562}},
   3: {4: {'cost': 0.5849625007211562}}},
  'node': [{'type': 'Start', 'ordered_children': {'a': [1], ' ': [3]}},
   {'type': 'token', 'token': 'a', 'ordered_children': {'__rules__': [2]}},
   {'type': 'rule',
    'rule_key': 0,
    'accepting': True,
    'ordered_children': {}},
   {'type': 'token', 'token': ' ', 'ordered_children': {'__rules__': [4]}},
   {'type': 'rule',
    'rule_key': 1,
    'accepting': True,
    'ordered_children': {}}],
  'edge_list': [(0, 1), (1, 2), (0, 3), (3, 4)]},
 'tokenizer_pattern': '(a|\ )',
 'graphtransliterator_version': '0.3.3'}
gt = GraphTransliterator.load(settings)
gt.transliterate('aa')


# In[7]:


# can be compacted
settings.pop('onmatch_rules_lookup')
GraphTransliterator.load(settings).transliterate('aa')


# In[8]:


JSON_settings = '''{"tokens": {"a": ["vowel"], " ": ["wb"]}, "rules": [{"production": "A", "prev_classes": null, "prev_tokens": null, "tokens": ["a"], "next_classes": null, "next_tokens": null, "cost": 0.5849625007211562}, {"production": " ", "prev_classes": null, "prev_tokens": null, "tokens": [" "], "next_classes": null, "next_tokens": null, "cost": 0.5849625007211562}], "whitespace": {"default": " ", "token_class": "wb", "consolidate": false}, "onmatch_rules": [{"prev_classes": ["vowel"], "next_classes": ["vowel"], "production": ","}], "metadata": {"author": "Author McAuthorson"}, "ignore_errors": false, "onmatch_rules_lookup": {"a": {"a": [0]}}, "tokens_by_class": {"vowel": ["a"], "wb": [" "]}, "graph": {"node": [{"type": "Start", "ordered_children": {"a": [1], " ": [3]}}, {"type": "token", "token": "a", "ordered_children": {"__rules__": [2]}}, {"type": "rule", "rule_key": 0, "accepting": true, "ordered_children": {}}, {"type": "token", "token": " ", "ordered_children": {"__rules__": [4]}}, {"type": "rule", "rule_key": 1, "accepting": true, "ordered_children": {}}], "edge": {"0": {"1": {"token": "a", "cost": 0.5849625007211562}, "3": {"token": " ", "cost": 0.5849625007211562}}, "1": {"2": {"cost": 0.5849625007211562}}, "3": {"4": {"cost": 0.5849625007211562}}}, "edge_list": [[0, 1], [1, 2], [0, 3], [3, 4]]}, "tokenizer_pattern": "(a| )", "graphtransliterator_version": "1.2.0"}'''

gt = GraphTransliterator.loads(JSON_settings)
gt.transliterate('a')


# In[9]:


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


# In[10]:


gt.match_at(1, tokens) # returns index to rule


# In[11]:


gt.rules[gt.match_at(1, tokens)] # actual rule


# In[12]:


gt.match_at(1, tokens, match_all=True) # index to rules, with match_all


# In[13]:


[gt.rules[_] for _ in gt.match_at(1, tokens, match_all=True)]


# In[14]:


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
gt.rules


# In[15]:


gt.pruned_of('<AA>').rules


# In[16]:


gt.pruned_of(['<A>', '<AA>']).rules


# In[17]:


tokens = {'ab': ['class_ab'], ' ': ['wb']}
whitespace = {'default': ' ', 'token_class': 'wb', 'consolidate': True}
rules = {'ab': 'AB', ' ': '_'}
settings = {'tokens': tokens, 'rules': rules, 'whitespace': whitespace}
gt = GraphTransliterator.from_easyreading_dict(settings)
gt.tokenize('ab ')


# In[18]:


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


# In[19]:


from graphtransliterator import DirectedGraph
DirectedGraph()


# In[20]:


g = DirectedGraph()
g.add_node()


# In[21]:


g.add_node()


# In[22]:


g.add_edge(0,1, {'data_key_1': 'some edge data here'})


# In[23]:


g.edge


# In[24]:


g = DirectedGraph()
g.add_node()


# In[25]:


g.add_node({'datakey1': 'data value'})


# In[26]:


g.node

