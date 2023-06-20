# -*- coding: utf-8 -*-
"""Colab: Prediction of global terrorist attacks

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1vbh4hrH64X5ie9-5EjFHfrCvKXkx18y-

![background.png](https://www.vifindia.org/sites/default/files/terrorism-gold-text-black-background-d-rendered-royalty-free-stock-picture-image-can-be-used-online-website-banner-87918799.jpg)

---
# **Analysis and Predictive Modelling of global terrorism attack success or failure**
---
> The primary objective of this project is to anlayze global terrorism trends draw insightful conclusions from the data on terrorist attack patterns and build a predictive model that will predict the probability of success of terrorist attacks.

>The model will utilize historical data on previous attacks, which include factors such as

>>```
country, city, region, attack type,
weapon type, target type, attack duration greater than 24 hours or less,
whether a kid was held hostage, group name,
and if the attack was single or multiple.
```
>>
to identify patterns which determines which attack is most likely to be succesful and thus advice on necessary action to take.
"""

#@title Library Imports
import chardet
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objs as go
import warnings
from sklearn.impute import SimpleImputer
from IPython.display import display, HTML     #for scrollable view

warnings.filterwarnings("ignore")
pd.set_option('display.max_info_rows', 1000)
pd.set_option('display.max_info_columns', 1000)
pd.set_option('display.max_columns', 150)
pd.set_option('display.max_rows', 150)
plt.style.use('ggplot')
sns.set_context('notebook')

#@title Download Dataset
# download dataset


#@title Detect file Encoding
# detect file encoding
with open('globalterrorismdb_0718dist.csv', 'rb') as raw:
  result=chardet.detect(raw.read(90000))
print(result)

# Abdul Basit
#function for scrollable view

def create_scrollable_table(df, table_id, title):
    html = f'<h3>{title}</h3>'
    html += f'<div id="{table_id}" style="height:200px; overflow:auto;">'
    html += df.to_html()
    html += '</div>'
    return html

#@title Load and Display Data
terrorism_df= pd.read_csv('globalterrorismdb_0718dist.csv', encoding="ISO-8859-1")

raw_data = create_scrollable_table(terrorism_df.head(20),'raw_dataset', 'Global Terrorism Data Raw Data')
display(HTML(raw_data))

# Abdul Basit
data_description = create_scrollable_table(terrorism_df.describe(), 'numerical_features', 'Description of the dataset')
display(HTML(data_description))

"""---

## **Data Cleaning**

---


"""

# print dataset number of rows and columns
terrorism_df.shape

"""> There are 135 features and 181,691 observations in the dataset.


---
#### ***Subset the data for the variables of interest***

Furthermore, as regards the project objective, we will subset the original dataset for only the features we consider relevant to our objective. This is based on information gained from the dataset description.
"""

project_df = terrorism_df[['iyear', 'imonth', 'iday', 'country_txt',
                           'region_txt','extended', 'city', 'multiple',
                           'success', 'attacktype1_txt',
                           'targtype1_txt','weaptype1_txt',
                           'ishostkid', 'gname']]

# Abdul Basit
project_data = create_scrollable_table(project_df.head(50),'dataset', 'Global Terrorism Data')
display(HTML(project_data))

"""#### ***Rename Columns***"""

#MUHEENAT
# rename the columns to a more human readable form

column_names = {'iyear':'year', 'imonth':'month', 'iday':'day', 'country_txt':'country_name',
                'region_txt':'region_name', 'extended': 'Duration>24hrs',
                'attacktype1_txt':'attacktype', 'multiple':'ismultiple',
                'targtype1_txt':'targettype_name', 'gname':'group_name',
                'weaptype1_txt':'weapontype_name', 'ishostkid':'kid_is_hostage'}
project_df.rename(columns=column_names, inplace=True)
print(project_df.shape)
# Abdul Basit
project_data = create_scrollable_table(project_df.head(50),'renamed_dataset', 'Columns are renamed')
display(HTML(project_data))

"""#### ***Check Dtype and Column with null features***"""

# check data type of every feature
project_df.dtypes

#  check for columns contaning null values
null_columns = project_df.isnull().sum().loc[lambda x : x > 0]
print(null_columns.sort_values())
print("Number of null columns: ", len(null_columns))

"""> There are 3 out 19 columns in the dataset with null values.

#### ***Imputation of missing values***
"""

# multiple or single attack
print(project_df.ismultiple.value_counts())

# kid_is_hostage
print(project_df.kid_is_hostage.value_counts())

# city
print(project_df.city.value_counts())

"""The following can be observed upon inspecting the values in the columns with the missing values:

1. The most frequent value in the 'ismultiple' column is '0.0'
2. The most frequent value in the 'kid_is_hostage' column is '0.0'
3. The 'kid_is_hostage' contains a minority group of '-9.0' this will later be filled in with the most frequent value.
4. The most frequent value in the 'city' column is 'Unknown'
"""

# imputation of null values using sklearn simpleimputer library
# and using the 'most_frequent' strategy

# instantiate the imputer
imputer_most_frequent = SimpleImputer(strategy='most_frequent',
                                      missing_values=np.nan)
# transform the null columns
null_series=imputer_most_frequent.fit_transform(
    project_df[list(null_columns.index)])
# set the original values to the transformed values
project_df[list(null_columns.index)] = null_series

# check that there are no longer
# columns with missing values
project_df.isnull().any()

"""#### ***Fix dtypes and invalid values***
The following cleaning will be carried out in this section

1. Data types of multiple_or_single and kid_is_hostage will be changed to int64 from float
2. The minority '-9' value in the kid_is_hostage feature will be replaced with '0'
"""

# change dtype from float to int
# of kid_is_hostage and multiple_or_single
project_df['kid_is_hostage'] = project_df['kid_is_hostage'].astype(np.int64)
project_df['ismultiple'] = project_df['ismultiple'].astype(np.int64)

# check
project_df[['ismultiple', 'kid_is_hostage']].dtypes

# replace minority value '-9' with 0
project_df.loc[project_df['kid_is_hostage']== -9, 'kid_is_hostage'] = 0
project_df['kid_is_hostage'].value_counts()

"""---

## **Exploratory Data Analysis**

---

#### ***Univariate Exploration***
In this section, we will be exploring the distributions of values in the features we have chosen to focus on.
>*Target Feature(Success)*
"""

def annotate_without_hue_percent(ax, feature):
  """
  Annotates the bars of a countplot
  without the hue parameter with percentages
  with percentages of their value

  Credit: stackoverflow link(https://stackoverflow.com/questions/31749448/how-to-add-percentages-on-top-of-grouped-bars)
  """
  total = len(feature)
  for p in ax.patches:
    percentage = '{:.1f}%'.format(100 * p.get_height()/total)
    x = p.get_x() + p.get_width() / 2 - 0.25
    y = p.get_y() + p.get_height()
    ax.annotate(percentage, (x, y), size = 12)

#carla
g=sns.catplot(x = "success", data= project_df, kind='count', height=5, aspect=0.8)
g.set_xticklabels({'Failed':0, 'Successful':1})
g.ax.set_title("Successful and Failed\n terrorist attacks", fontsize=14, fontweight=700);
annotate_without_hue_percent(g.ax, project_df.success)
plt.gca().figure.savefig("success.png", dpi=1080, bbox_inches='tight')

"""There are more successful attacks (89%) in the data than failed attacks (11%). This could lead to a bias in the classification of attacks. To handle this we will look into some of the techniques mentioned [here](https://www.analyticsvidhya.com/blog/2021/06/5-techniques-to-handle-imbalanced-data-for-a-classification-problem/#:~:text=Imbalanced%20data%20refers%20to%20those,very%20low%20number%20of%20observations.) and choose an appropriate one for our project.

> The following features will be explored in this section

1. Duration>24hrs (If attack duration was greater than 24hrs or not)
2. ismultiple (Was the attack a single attack or multiple attack)
3. kid_is_hostage (Was a kid held hostage)
"""

fig, axes=plt.subplots(1, 3, figsize=(8, 5), sharey=True)
for ax, col_name in zip(axes, ['Duration>24hrs', 'ismultiple', 'kid_is_hostage']):
  sns.countplot(data=project_df, x=col_name, ax=ax)
  ax.tick_params(axis=u'both', which=u'both',length=0)
  ax.set_xticklabels(['No', 'Yes'])
  if col_name in ['ismultiple', 'kid_is_hostage']:
    ax.set_ylabel("")
  annotate_without_hue_percent(ax=ax, feature=project_df[col_name])
fig.savefig("duration_mult_host.png", dpi=1080, bbox_inches='tight')

"""Most terrorist attacks in our dataset have the following in common:

1. The duration  leisss than 24hrs.
2. They are mostly single attacks.
3. No Kid was held hostage in 93% of the attacks.
4. Most of the attacks are successful.

> **Which Region, Country and City have the highest number of terrorist attacks?**
"""

def plot_column_value_count(df, column_name):
  """This function takes in  a dataframe and
     column name and plots a bar chart of the
     count of values for the top 20 values
     in that column.

     Input:
      df: pandas dataframe
      column_name: Name of column to plot the bar chart for.
  """
  column_title = column_name.split('_')[0].title()
  # carla   #Muheenat - I changed the title of the graph from Top 20 region to Total Attacks by Region.
  # count the values
  graph=df[column_name].value_counts().to_frame(name='count').reset_index().head(10)
  graph.rename(columns = {'index':column_title}, inplace = True)

  # customize the plot
  ax = sns.barplot(x='count', y=column_title, data=graph)
  ax.set_title(f"Total Attacks by {column_title}", fontsize=15, fontweight=700)
  for container in ax.containers:
      ax.bar_label(container)

plot_column_value_count(project_df, 'region_name')
plt.gca().figure.savefig("total_attack_count_by_region.png", dpi=1080, bbox_inches='tight')

"""Middle East and North Africa followed by South Asia have the highest number (500474 and 44974 respectively) of terrorist attacks.

Now we are going to visualize the top 10 most attacked countries and cities.
"""

#carla
plot_column_value_count(project_df, 'country_name')
plt.gca().figure.savefig("total_attack_count_by_country.png", dpi=1080, bbox_inches='tight')

#carla
plot_column_value_count(project_df[project_df.city != "Unknown"], 'city')

"""In conclusion, as of 2017, the terrorist attack is most common in the Middle East and South Asia in the country of Iraq and Pakistan and the city of Baghdad. Though in [recent](https://en.wikipedia.org/wiki/January_2021_Baghdad_bombings) years, terrorist attacks seem to be dropping in frequency.

> **Which is the most common target type, attack type and group?**
"""

plot_column_value_count(project_df, 'targettype_name')
plt.gca().figure.savefig("total_attack_count_by_target.png", dpi=1080, bbox_inches='tight')

plot_column_value_count(project_df, 'attacktype')
plt.gca().figure.savefig("total_attack_count_by_attack.png", dpi=1080, bbox_inches='tight')

plot_column_value_count(project_df[project_df.group_name != 'Unknown'], 'group_name')
plt.gca().figure.savefig("total_attack_count_by_group.png", dpi=1080, bbox_inches='tight')

"""> **Which group have the highest rate of successful attacks?**"""

graph_data=pd.DataFrame(project_df.query("success==1")['group_name'].value_counts().reset_index())
graph_data.rename(columns={'index': 'Group_Name', 'group_name': 'Success_Count'}, inplace=True)
graph_data=graph_data.query('Group_Name != "Unknown"').head(10)

ax=sns.barplot(data=graph_data, x='Success_Count',
              y='Group_Name')
ax.set_title("Count of Successful terrorist attacks by group",  fontsize=15, fontweight= 700)
for container in ax.containers:
  ax.bar_label(container)
ax.figure.savefig("attack_count_by_group.png", dpi=1080, bbox_inches='tight')

"""The most common terrorist ***attack type, target type, group, and the group with the highest number of success*** are ***Bombing and explosion, Private Citizens and property, Taliban and Taliban*** respectively.

#### ***Bivariate and Multivariate Exploration***

>**How has terrorist attacks increased or decreased between the year 1970 to 2017?**
"""

# carla (modified)
def plot_trends_by_year(column_name):
  """
  This function takes a column name
  and plot the trend for that feature
  between the year 1970 to 2017

  Input
        column_name: feature to plot
  Return
        fig: A plotly figure object for further customization
            of the plot
  """

  graph_plot=project_df.query(f"{column_name} != 'Unknown'")
  graph_plot=graph_plot[[column_name,'year']]\
        .groupby(['year'])[column_name].value_counts()\
        .to_frame(name='total_attacks').reset_index()
  graph_plot = graph_plot.query('total_attacks>=150')

  fig = px.line(graph_plot, x='year', y='total_attacks',
          color=column_name, symbol=column_name)
  return fig

# ##carla
#carla
fig = plot_trends_by_year('region_name')
fig.update_layout(title="Count of terrorist attacks from\n 1970 to 2017 by region")
fig.show()

"""From the above, it can be seen that there has been an increase in the number of terrorist attacks in at least five regions over the years with the most notable being South Asia and Middle East&North Africa most especially between the years 2000 to 2014.

A decrease in activity can also be seen from 2014 onward.

***which weapon type have seen increasing use between 1970 and 2017***
"""

#carla
fig = plot_trends_by_year('weapontype_name')
fig.update_layout(title="Weapons type usage from 1970 from 2017")
fig.show()

"""Explosives and firearms have seen an increasing use compared to other weapons.

***how has terrorist group activities changed between 1970 and 2017***
"""

#carla
fig = plot_trends_by_year('group_name')
fig.update_layout(title="Trends in group activities between 1970 from 2017")
fig.show()

"""I.S.I.L (Islamic State of Iraq and the Levant), Taliban and Al-Shabab are the most active terrorist groups in recent years with I.S.I.L having launched more attacks overall.

---
## **Modelling**
---
"""


import category_encoders as ce
from sklearn.model_selection import train_test_split

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import GaussianNB
from xgboost import XGBClassifier
from imblearn.ensemble import BalancedBaggingClassifier

from sklearn.metrics import classification_report, ConfusionMatrixDisplay
from sklearn.metrics import RocCurveDisplay

"""### **Prepare Data**"""

# dropping the year month and day columns
project_df = project_df.drop(['year','month', 'day'], axis=1)

# split the data into feature and target variable
model_df = project_df.sample(frac=0.5, random_state=42)

X = model_df.drop(columns = ['success'])
y = model_df['success']

# encode the categorical data using base2 encoder
categorical_cols = ['country_name', 'region_name', 'city','attacktype', 'targettype_name', 'weapontype_name','group_name']
encoder = ce.BaseNEncoder(cols=categorical_cols, return_df=True, base=2)
features_encoded = encoder.fit_transform(X, columns=categorical_cols)

features_encoded.head()

X_train, X_test, y_train, y_test = train_test_split(features_encoded, y, test_size=0.2, random_state=42)

#carla
def generate_roc_curve(Xtrain, Xtest, ytrain, ytest):

    # Create a dictionary of classification algorithms
    clfs = ( GaussianNB(),
            LogisticRegression(),
            RandomForestClassifier(random_state=42),
            BalancedBaggingClassifier(random_state=42),
            XGBClassifier()
    )
    fig, ax_roc = plt.subplots(1, 1, figsize=(8,6))
    for clf in clfs:

        # Fit the algorithm on the training data
        clf.fit(Xtrain, ytrain)
        RocCurveDisplay.from_estimator(clf, Xtest, ytest, ax=ax_roc,
                                       name=type(clf).__name__)


# princezuko
def evaluate_classification_algorithm(clf, Xtrain, Xtest, ytrain, ytest):

  # Fit the algorithm on the training data
  clf.fit(Xtrain, ytrain)

  # Generate classification report
  classification_report_result = classification_report(ytest, clf.predict(Xtest))
  print("Classification Report:")
  print(classification_report_result)

  # Generate heatmap confusion matrix
  ConfusionMatrixDisplay.from_estimator(clf, Xtest, ytest, cmap='Blues')
  plt.title(f"{type(clf).__name__} Confusion Matrix")

"""### ***Before Oversampling***"""

generate_roc_curve(X_train, X_test, y_train, y_test)
plt.gca().figure.savefig("roc_auc_before_balance.png", dpi=1080, bbox_inches='tight')

evaluate_classification_algorithm(XGBClassifier(), X_train, X_test, y_train, y_test)

evaluate_classification_algorithm(BalancedBaggingClassifier(random_state=42), X_train, X_test, y_train, y_test)

evaluate_classification_algorithm(RandomForestClassifier(random_state=42), X_train, X_test, y_train, y_test)

"""### ***Oversampling due to imbalance***"""

from imblearn.over_sampling import SMOTEN

model_smote = SMOTEN(random_state=42, n_jobs = -1)
X_train_smote, y_train_smote = model_smote.fit_resample(X_train, y_train.ravel())

# to demonstrate the effect of SMOTE over imbalanced datasets
fig, (ax1, ax2) = plt.subplots(ncols = 2, figsize =(15, 5))
ax1.set_title('Before SMOTE')
pd.Series(y_train).value_counts().plot.bar(ax=ax1)


ax2.set_title('After SMOTE')
pd.Series(y_train_smote).value_counts().plot.bar(ax=ax2)

plt.show()

"""#### ***After Oversampling***"""

generate_roc_curve(X_train_smote, X_test, y_train_smote.ravel(), y_test)
plt.gca().figure.savefig("roc_auc_after_balance.png", dpi=1080, bbox_inches='tight')

evaluate_classification_algorithm(XGBClassifier(), X_train_smote, X_test, y_train_smote.ravel(), y_test)

evaluate_classification_algorithm(BalancedBaggingClassifier(random_state=42), X_train_smote, X_test, y_train_smote, y_test)

evaluate_classification_algorithm(RandomForestClassifier(random_state=42), X_train_smote, X_test, y_train_smote, y_test)

"""It can seen that the XGBClassifier generally performs better than the other evaluated models. Also, oversampling with 'SMOTEN' does not have positive effect on the models performance. The XGBClassifier will be tuned further to improve its performance where possible.

### **Model Tuning**
"""

from sklearn.model_selection import RandomizedSearchCV

# parameters tuning (long execution time)
# params = { 'max_depth': [3, 5, 6, 10, 15, 20],
#            'learning_rate': [0.01, 0.1, 0.2, 0.3],
#            'subsample': np.arange(0.5, 1.0, 0.1),
#            'colsample_bytree': np.arange(0.4, 1.0, 0.1),
#            'colsample_bylevel': np.arange(0.4, 1.0, 0.1),
#            'n_estimators': [100, 500, 1000]}
# xgbclf = XGBClassifier(seed = 20)

# clf = RandomizedSearchCV(estimator=xgbclf,
#                          param_distributions=params,
#                          scoring='f1',
#                          n_iter=25,
#                          verbose=1)
# evaluate_classification_algorithm(clf, X_train, X_test, y_train, y_test)
# print("Best parameters:", clf.best_params_)

# best parameters after tuning
best_parameters= {'subsample': 0.7999999999999999,
                  'n_estimators': 100,
                  'max_depth': 10,
                  'learning_rate': 0.1,
                  'colsample_bytree': 0.5,
                  'colsample_bylevel': 0.7999999999999999}

"""### ***Build model pipeline***"""

tuned_clf = XGBClassifier(seed=20, **best_parameters)

from sklearn.compose import ColumnTransformer
from sklearn.pipeline import make_pipeline
preprocessor = ColumnTransformer(
    transformers =[
        ('encoder', ce.BaseNEncoder(base=2), categorical_cols)
    ]
)

model=make_pipeline(
    preprocessor,
    tuned_clf
)
model

Xtrain, Xtest, ytrain, ytest = train_test_split(X, y,test_size=0.3, random_state=42)
evaluate_classification_algorithm(model, Xtrain, Xtest, ytrain, ytest)
plt.gca().figure.savefig("confusion_matrix_final.png", dpi=1080, bbox_inches='tight')

model.feature_names_in_

"""### ***Save Model***"""

from joblib import dump
dump(model, 'model.joblib')

"""## **Summary and Conclusion**

From the exploration of the dataset, the following observations were made


1. The duration of most attacks is less than 24hrs.
2. Terrorist attacks are mostly single attacks.
3. No Kid was held hostage in 93% of terrorist attacks recorded.
4. Most of the terrorist attacks recorded were successful.
5. Terrorist attacks are most common in the ***Middle East and South Asia in the country of Iraq and Pakistan and the city of Baghdad***.
6. The most common terrorist ***attack type, target type, group, and the group with the highest number of successes*** are ***Bombing and explosion, Private Citizens and property, Taliban and Taliban*** respectively.


The following trends were observed in terrorist activities, type of weapon used and regions most attacked within the period (1970 to 2017)

1. An increase in the number of terrorist attacks in at least five regions over the years with the most notable being South Asia and Middle East&North Africa most especially between the years 2000 to 2014.

2. A decrease in activity can also be observed from 2014 onward.

3. Explosives and firearms are the most common weapon of choice in the majority of terrorist activities within this period.

4. I.S.I.L (Islamic State of Iraq and the Levant), Taliban and Al-Shabab are the most active terrorist groups in recent years with I.S.I.L having launched more attacks overall.

## **Credit and Thanks**
"""

# We would love to appreciate Hamoye Data Science team for providing this opprotunity to add to our growth and career. Specific recognition to the major contributors of this notebook - Muheenat, Temitayo, Carla, Prince Zuko, Hajara, Chiemela