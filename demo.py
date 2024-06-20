random_name = {}

calc = 30
alegbra = 20
geo = 10


classes = {
    "Calculus": 30,
    "Algebra": 20,
    "Geometry": 10
}



print(classes)
classes["Algebra"] = 32
print(classes)

[2,3,4,5,6,6,5]


events = {
    "Planting Trees" : ["john", "adam", "weoifh", "rerg", "rerg", "John"],
    "Cleaning up parks" : [],
    "Feeding the homeless" : [],
    "Tutoring children": [],
}
print(events)
events["Cleaning up parks"].append("Rob")
print(events)

["bob", "Comstock", "hi@gmail.com"]


site = {
    "Name": ["Bob", "Shubhan", "Ishaan"],
    "Description":["Comstock", "N/A", "Gob"],
    "Email": ["hi@gmail.com", "s@gmail.com", "ip@gmail.com"]

}



{
    "Name": "Bob",
    "Description": "Comstock",
    "Email": "hi@gmail.com"
}

{
    "Name": "Shubhan",
    "Description": "N/A",
    "Email": "
}




def findDescription(name):
    index = -1
    for i in range(len(site["Name"])):
        if site["Name"][i] == name:
            index = i
            break
    
    if site["Address"][index] == "N/A":
        return "Address not found"
    
    return site["Address"][index]


            

        


