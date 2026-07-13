#!/usr/bin/env python
# coding: utf-8

# In[1]:


import graphtransliterator
import graphtransliterator.cli as cli
from click.testing import CliRunner
runner = CliRunner()
def run(func, parameters):
  print(runner.invoke(func, parameters).output)


# In[2]:


run(cli.main, ['--help'])


# In[3]:


run(cli.dump, ['--help'])


# In[4]:


run(cli.dump, ['--from', 'bundled', 'Example'])


# In[5]:


run(cli.dump, ['--from', 'yaml_file', '../graphtransliterator/transliterators/example/example.yaml'])


# In[6]:


run(cli.dump, ['--from', 'bundled', 'Example', '--check-ambiguity']) # not human readable, with graph


# In[7]:


run(cli.dump, ['--from', 'bundled', 'Example', '--compression-level', '0'])


# In[8]:


run(cli.dump, ['--from', 'bundled', 'Example', '--compression-level', '1'])


# In[9]:


run(cli.dump, ['--from', 'bundled', 'Example', '--compression-level', '2'])


# In[10]:


run(cli.dump_tests, ['--help'])


# In[11]:


run(cli.dump_tests, ['Example'])


# In[12]:


run(cli.dump_tests, ['--to', 'json', 'Example'])


# In[13]:


run(cli.generate_tests, ['--help'])


# In[14]:


run(cli.generate_tests, ['--from', 'bundled', 'Example'])


# In[15]:


run(cli.test, ['--help'])


# In[16]:


run(cli.test, ['Example'])


# In[17]:


run(cli.transliterate, ['--help'])


# In[18]:


run(cli.transliterate, ['--from', 'bundled', 'Example', 'a'])


# In[19]:


run(cli.transliterate, ['-f', 'json_file', '../graphtransliterator/transliterators/example/example.json', 'a'])


# In[20]:


run(cli.transliterate, ['-f', 'yaml_file', '../graphtransliterator/transliterators/example/example.yaml', 'a'])


# In[21]:


run(cli.transliterate, ['-f', 'json_file', '../graphtransliterator/transliterators/example/example.json', 'a', 'a'])


# In[22]:


run(cli.transliterate, ['-f', 'bundled', 'Example', 'a'])


# In[23]:


run(cli.transliterate, ['-f', 'bundled', 'Example', '--to', 'json', 'a'])


# In[24]:


run(cli.transliterate, ['-f', 'bundled', 'Example', '--to', 'python', 'a', 'a'])


# In[25]:


run(cli.transliterate, ['-f', 'bundled', 'Example', '--to', 'json', 'a', 'a'])

