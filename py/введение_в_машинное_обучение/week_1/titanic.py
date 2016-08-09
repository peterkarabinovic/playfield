import pandas, re
data = pandas.read_csv('titanic.csv', index_col='PassengerId')

# print data["Pclass"].value_counts(True, sort=True)

# first_class = data["Pclass"]
# first_class = first_class[first_class]

print data['Survived'].value_counts(True, sort=True)




# print data['Age'].mean(), data['Age'].median()

# print data[['SibSp', 'Parch']].corr()

femaleNames = data[data['Sex'] == 'female' ]['Name']

spliting = [re.findall('([a-zA-Z]\w+)',x) for x in femaleNames.dropna() ] 
print len(spliting)
spliting = reduce(lambda x,y: x+y,spliting)
print pandas.Series(spliting).value_counts(sort=True)

