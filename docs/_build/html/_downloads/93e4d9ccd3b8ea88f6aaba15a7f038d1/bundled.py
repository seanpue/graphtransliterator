#!/usr/bin/env python
# coding: utf-8

# In[1]:


import graphtransliterator.transliterators as transliterators
example_transliterator = transliterators.Example()
example_transliterator.transliterate('a')


# In[2]:


bundled_iterator = transliterators.iter_transliterators()
next(bundled_iterator)


# In[3]:


bundled_names_iterator = transliterators.iter_names()
next(bundled_names_iterator)


# In[4]:


from graphtransliterator.transliterators import Example


# In[5]:


transliterator = Example()
transliterator.directory


# In[6]:


import pprint
transliterator = next(transliterators.iter_transliterators())
pprint.pprint(transliterator.metadata)

