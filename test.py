fruits = [("apple", 1),("apple1", 0)]

print([x[0] for x in fruits if "a" in x[0]])

#fruits.sort(key=lambda a: a[1])
print(fruits[slice(2)])
#print(min([x[1] for x in fruits]))
