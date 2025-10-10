import math
print("CALCULATOR")
a = int(input("Enter one number"))
b = int(input("Enter second number"))
while True:
    print("make your choice")
    print("For addition press 1")
    print("For subtraction press 2")
    print("For multiplication press 3")
    print("For division press 4")
    print("For square press 5")
    print("For square-root press 6")
    print("To exit, press 0")

    choice = int(input("Enter the number as per your choice"))
    
    if choice == 1:
        print("result = ", a+b)
    elif choice == 2:
        print("result = ", a-b)
    elif choice == 3:
        print("result = ", a*b)
    elif choice == 4:
        if b!=0:
            print("result = ", a/b)
        else:
            print("Cannot divide by 0!")
    elif choice == 5:
        print("square of a = ", a**2)
        print("square of b = ", b**2)
    elif choice == 6:
        print("square root of a = ", math.sqrt(a))
        print("square root of b = ", math.sqrt(b))
    elif choice == 0:
        print("Exiting the code...")
        break
    else:
        print("Put the number from the list above")