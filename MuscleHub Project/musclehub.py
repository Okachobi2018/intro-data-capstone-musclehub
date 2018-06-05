
# coding: utf-8

# # Capstone Project 1: MuscleHub AB Test

# ## Step 1: Get started with SQL

# Like most businesses, Janet keeps her data in a SQL database.  Normally, you'd download the data from her database to a csv file, and then load it into a Jupyter Notebook using Pandas.
# 
# For this project, you'll have to access SQL in a slightly different way.  You'll be using a special Codecademy library that lets you type SQL queries directly into this Jupyter notebook.  You'll have pass each SQL query as an argument to a function called `sql_query`.  Each query will return a Pandas DataFrame.  Here's an example:

# In[6]:


# This import only needs to happen once, at the beginning of the notebook
from matplotlib import pyplot as plt
import pandas as pd
import numpy as np

import warnings
import matplotlib.cbook
warnings.filterwarnings("ignore",category=matplotlib.cbook.mplDeprecation)
import matplotlib.ticker as mtick
from scipy.stats import ttest_1samp
from scipy.stats import ttest_ind
from scipy.stats import f_oneway
from statsmodels.stats.multicomp import pairwise_tukeyhsd
from scipy.stats import binom_test
from codecademySQL import sql_query


# In[ ]:


# Here's an example of a query that just displays some data
#sql_query('''
#SELECT *
#FROM visits
#LIMIT 5
#''')


# In[ ]:


# Here's an example where we save the data to a DataFrame
#df = sql_query('''
#SELECT *
#FROM applications
#LIMIT 5
#''')


# ## Step 2: Get your dataset

# Let's get started!
# 
# Janet of MuscleHub has a SQLite database, which contains several tables that will be helpful to you in this investigation:
# - `visits` contains information about potential gym customers who have visited MuscleHub
# - `fitness_tests` contains information about potential customers in "Group A", who were given a fitness test
# - `applications` contains information about any potential customers (both "Group A" and "Group B") who filled out an application.  Not everyone in `visits` will have filled out an application.
# - `purchases` contains information about customers who purchased a membership to MuscleHub.
# 
# Use the space below to examine each table.

# In[10]:


# Examine visits here
visits = pd.read_csv('visits.csv')
print visits.head()

#sql_query('''
#SELECT *
#FROM visits where visit_date >= '7-1-17' ''')


# In[11]:


# Examine fitness_tests here
fitness = pd.read_csv('fitness_tests.csv')
print fitness.head()


# In[12]:


# Examine applications here
applications = pd.read_csv('applications.csv')
print applications.head()


# In[13]:


# Examine purchases here
purchases = pd.read_csv('purchases.csv')
print purchases.head()


# We'd like to download a giant DataFrame containing all of this data.  You'll need to write a query that does the following things:
# 
# 1. Not all visits in  `visits` occurred during the A/B test.  You'll only want to pull data where `visit_date` is on or after `7-1-17`.
# 
# 2. You'll want to perform a series of `LEFT JOIN` commands to combine the four tables that we care about.  You'll need to perform the joins on `first_name`, `last_name`, and `email`.  Pull the following columns:
# 
# 
# - `visits.first_name`
# - `visits.last_name`
# - `visits.gender`
# - `visits.email`
# - `visits.visit_date`
# - `fitness_tests.fitness_test_date`
# - `applications.application_date`
# - `purchases.purchase_date`
# 
# Save the result of this query to a variable called `df`.
# 
# Hint: your result should have 5004 rows.  Does it?

# In[14]:


df = sql_query('''Select visits.first_name, visits.last_name, visits.gender, visits.visit_date, t2.fitness_test_date, t3.application_date, t4.purchase_date from visits
left join fitness_tests as t2 on visits.first_name = t2.first_name and visits.last_name = t2.last_name and visits.email = t2.email 
left join applications as t3 on visits.first_name = t3.first_name and visits.last_name = t3.last_name and visits.email = t3.email
left join purchases as t4 on visits.first_name = t4.first_name and visits.last_name = t4.last_name and visits.email = t4.email where visit_date >= '7-1-17'
''')
print df


# ## Step 3: Investigate the A and B groups

# We have some data to work with! Import the following modules so that we can start doing analysis:
# - `import pandas as pd`
# - `from matplotlib import pyplot as plt`

# We're going to add some columns to `df` to help us with our analysis.
# 
# Start by adding a column called `ab_test_group`.  It should be `A` if `fitness_test_date` is not `None`, and `B` if `fitness_test_date` is `None`.

# In[15]:


df['ab_test_group'] = df.apply(lambda row: 'B' if row.fitness_test_date == None else 'A', axis = 1)
print df


# Let's do a quick sanity check that Janet split her visitors such that about half are in A and half are in B.
# 
# Start by using `groupby` to count how many users are in each `ab_test_group`.  Save the results to `ab_counts`.

# In[16]:


ab_counts = df.groupby('ab_test_group').first_name.count().reset_index().rename(columns = {'first_name' : '#_of_users'})
print ab_counts

#click_source = user_visits.groupby('utm_source').id.count().reset_index()
#print(click_source)


# We'll want to include this information in our presentation.  Let's create a pie cart using `plt.pie`.  Make sure to include:
# - Use `plt.axis('equal')` so that your pie chart looks nice
# - Add a legend labeling `A` and `B`
# - Use `autopct` to label the percentage of each group
# - Save your figure as `ab_test_pie_chart.png`

# In[17]:


pie_ab_names = ['A', 'B']
pie_ab = [2504, 2500]
plt.pie(pie_ab, autopct='%0.2f%%')
plt.axis('equal')
plt.legend(pie_ab_names)
plt.show()
plt.savefig('ab_test_pie_chart.png')


# ## Step 4: Who picks up an application?

# Recall that the sign-up process for MuscleHub has several steps:
# 1. Take a fitness test with a personal trainer (only Group A)
# 2. Fill out an application for the gym
# 3. Send in their payment for their first month's membership
# 
# Let's examine how many people make it to Step 2, filling out an application.
# 
# Start by creating a new column in `df` called `is_application` which is `Application` if `application_date` is not `None` and `No Application`, otherwise.

# In[18]:


df['is_application'] = df.apply(lambda row: 'No Application' if row.application_date == None else 'Application', axis = 1)
print df


# Now, using `groupby`, count how many people from Group A and Group B either do or don't pick up an application.  You'll want to group by `ab_test_group` and `is_application`.  Save this new DataFrame as `app_counts`

# In[19]:


app_counts = df.groupby(['ab_test_group', 'is_application']).count().first_name.reset_index().rename(columns = {'first_name' : '#_of_users'})
print app_counts


# We're going to want to calculate the percent of people in each group who complete an application.  It's going to be much easier to do this if we pivot `app_counts` such that:
# - The `index` is `ab_test_group`
# - The `columns` are `is_application`
# Perform this pivot and save it to the variable `app_pivot`.  Remember to call `reset_index()` at the end of the pivot!

# In[20]:


app_pivot = app_counts.pivot(
columns = 'is_application',
index = 'ab_test_group',
values = '#_of_users').reset_index()
print app_pivot


# Define a new column called `Total`, which is the sum of `Application` and `No Application`.

# In[21]:


app_pivot['Total'] = app_pivot.Application + app_pivot['No Application']
print app_pivot


# Calculate another column called `Percent with Application`, which is equal to `Application` divided by `Total`.

# In[22]:


app_pivot['Percent with Application'] = (app_pivot.Application/app_pivot.Total)*100
print app_pivot


# It looks like more people from Group B turned in an application.  Why might that be?
# 
# We need to know if this difference is statistically significant.
# 
# Choose a hypothesis tests, import it from `scipy` and perform it.  Be sure to note the p-value.
# Is this result significant?

# In[58]:


#More people might have turned in an applicaiton for Group B maybe because they were more likely to test out the gym
#because they have not done so before.

pval = binom_test(250, n=2504, p=0.0998)
print pval

pval2 = binom_test(325, n=2500, p=0.13)
print pval2

#the p-value results are not significantly different


# ## Step 4: Who purchases a membership?

# Of those who picked up an application, how many purchased a membership?
# 
# Let's begin by adding a column to `df` called `is_member` which is `Member` if `purchase_date` is not `None`, and `Not Member` otherwise.

# In[23]:


df['is_member'] = df.apply(lambda row: 'Not Member' if row.purchase_date == None else 'Member', axis = 1)
print df


# Now, let's create a DataFrame called `just_apps` the contains only people who picked up an application.

# In[24]:


just_apps = df[df.is_application == 'Application']
print just_apps


# Great! Now, let's do a `groupby` to find out how many people in `just_apps` are and aren't members from each group.  Follow the same process that we did in Step 4, including pivoting the data.  You should end up with a DataFrame that looks like this:
# 
# |is_member|ab_test_group|Member|Not Member|Total|Percent Purchase|
# |-|-|-|-|-|-|
# |0|A|?|?|?|?|
# |1|B|?|?|?|?|
# 
# Save your final DataFrame as `member_pivot`.

# In[25]:


app_counts = just_apps.groupby(['ab_test_group', 'is_member']).count().first_name.reset_index().rename(columns = {'first_name' : '#_of_users'})
print app_counts

member_pivot = app_counts.pivot(
columns = 'is_member',
index = 'ab_test_group',
values = '#_of_users').reset_index()

member_pivot['Total'] = member_pivot.Member + member_pivot['Not Member']

member_pivot['Percent Purchase'] = (member_pivot.Member/member_pivot.Total)*100

print member_pivot



# It looks like people who took the fitness test were more likely to purchase a membership **if** they picked up an application.  Why might that be?
# 
# Just like before, we need to know if this difference is statistically significant.  Choose a hypothesis tests, import it from `scipy` and perform it.  Be sure to note the p-value.
# Is this result significant?

# In[52]:


#Since the people who took the fitness test have already invested some time testing out the gym they might have been more likely
#purchase a membership 

pval = binom_test(200, n=250, p=0.8)
print pval

pval2 = binom_test(250, n=325, p=0.769)
print pval2

#this result is not significantly different


# Previously, we looked at what percent of people **who picked up applications** purchased memberships.  What we really care about is what percentage of **all visitors** purchased memberships.  Return to `df` and do a `groupby` to find out how many people in `df` are and aren't members from each group.  Follow the same process that we did in Step 4, including pivoting the data.  You should end up with a DataFrame that looks like this:
# 
# |is_member|ab_test_group|Member|Not Member|Total|Percent Purchase|
# |-|-|-|-|-|-|
# |0|A|?|?|?|?|
# |1|B|?|?|?|?|
# 
# Save your final DataFrame as `final_member_pivot`.

# In[26]:


app_counts = df.groupby(['ab_test_group', 'is_member']).count().first_name.reset_index().rename(columns = {'first_name' : '#_of_users'})

final_member_pivot = app_counts.pivot(
columns = 'is_member',
index = 'ab_test_group',
values = '#_of_users').reset_index()

final_member_pivot['Total'] = final_member_pivot.Member + final_member_pivot['Not Member']

final_member_pivot['Percent Purchase'] = (final_member_pivot.Member/final_member_pivot.Total)*100

print final_member_pivot


# Previously, when we only considered people who had **already picked up an application**, we saw that there was no significant difference in membership between Group A and Group B.
# 
# Now, when we consider all people who **visit MuscleHub**, we see that there might be a significant different in memberships between Group A and Group B.  Perform a significance test and check.

# In[54]:


pval = binom_test(200, n=2504, p=0.07987)
print pval

pval2 = binom_test(250, n=2500, p=0.10)
print pval2


# ## Step 5: Summarize the acquisition funel with a chart

# We'd like to make a bar chart for Janet that shows the difference between Group A (people who were given the fitness test) and Group B (people who were not given the fitness test) at each state of the process:
# - Percent of visitors who apply
# - Percent of applicants who purchase a membership
# - Percent of visitors who purchase a membership
# 
# Create one plot for **each** of the three sets of percentages that you calculated in `app_pivot`, `member_pivot` and `final_member_pivot`.  Each plot should:
# - Label the two bars as `Fitness Test` and `No Fitness Test`
# - Make sure that the y-axis ticks are expressed as percents (i.e., `5%`)
# - Have a title

# In[32]:


Tests = ['Fitness Test', 'No Fitness Test']
plt.bar(range(len(Tests)), app_pivot['Percent with Application'])

plt.title('Percent of Visitors Who Apply')



ax = plt.subplot()
fmt = '%.0f%%' 
yticks = mtick.FormatStrFormatter(fmt)
ax.yaxis.set_major_formatter(yticks)
ax.set_xticks(range(len(Tests)))
ax.set_xticklabels(Tests, rotation = 30)
plt.show()


# In[31]:


Tests = ['Fitness Test', 'No Fitness Test']
plt.bar(range(len(Tests)), member_pivot['Percent Purchase'])

plt.title('Percent of Applicants Who Purchase a Membership')


ax = plt.subplot()
fmt = '%.0f%%'
yticks = mtick.FormatStrFormatter(fmt)
ax.yaxis.set_major_formatter(yticks)
ax.set_xticks(range(len(Tests)))
ax.set_xticklabels(Tests, rotation = 30)
plt.show()


# In[30]:


Tests = ['Fitness Test', 'No Fitness Test']
plt.bar(range(len(Tests)), final_member_pivot['Percent Purchase'])

plt.title('Percent of Visitors Who Purchase a Membership')



ax = plt.subplot()
fmt = '%.0f%%'
yticks = mtick.FormatStrFormatter(fmt)
ax.yaxis.set_major_formatter(yticks)
ax.set_xticks(range(len(Tests)))
ax.set_xticklabels(Tests, rotation = 30)
plt.show()

