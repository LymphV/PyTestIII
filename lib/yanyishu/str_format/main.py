#!/usr/bin/env python
# coding: utf-8

# In[2]:


from strFormat import strFormat

l = " A -M·多 伊&nbsp;斯    "
print(strFormat(l).standardization())
print(strFormat(l,'allSpace').standardization())
print(strFormat(l,'allSpace').mysql_format())





