print("    " + " ".join([str(i).rjust(2, " ") for i in range(1, 10)]))
print("   " + "---" * 9)
for i in range(1, 10):
    print(str(i).rjust(2, " ") + "|", end="")
    for j in range(1, 10):
        print(str(i * j).rjust(3, " "), end="") 
    print()