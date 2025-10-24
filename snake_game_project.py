'''
1 is for snake
-1 is for water
0 is for gun
'''

import random

computer = random.choice([-1, 1, 0])
youstr = input("enter your choice: S/W/G: ")
youDict = {"S": 1, "W" : -1, "G" : 0}
reverseDict = {1 : "Snake", -1 : "Water", 0 : "Gun"}
you = youDict[youstr.upper()]

print(f"You chose {reverseDict[you]}\nComputer chose {reverseDict[computer]}")

if(computer == you):
    print("it's a draw")

else:
    if(computer == -1 and you == 1) or (computer == 1 and you == 0) or (computer == 0 and you == -1):
        print("you win")
    else:
        print("you lose")