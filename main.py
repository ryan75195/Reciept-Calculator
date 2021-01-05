import pytesseract as pt
import Reciept
import Files

# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

def getStage(character):
    if character == "£":
        return "Price"
    elif character == "\n":
        return "Name"

def getItems(recieptString):
    ItemName = ""
    Price = ""
    CardNumber = ""
    TotalCost = ""
    itemDict = {}
    buffer = ["Name", "Price", "Card Number", "Total Cost"]
    Stage = "Name"


    for i in recieptString:
        if Stage == "Name":
            if i == "£":
                Stage = "Price"
            else:
                ItemName += i
                if "VISA DEBIT SALE" in ItemName:
                    if len("".join([x for x in TotalCost if x.isalnum()])) < 5:
                        print("".join([x for x in TotalCost if x.isalnum()]))
                        TotalCost += i
        if Stage == "Price":
            if len(Price) == 5:
                itemDict[ItemName.strip("\n")] = Price
                Stage = "Name"
                ItemName = "".join(i)
                Price = ""
            else:
                Price += i

    # print(itemDict)
    # print(TotalCost)
    for i in itemDict.keys():
        print(i)
    return TotalCost



def run(name):
    # Use a breakpoint in the code line below to debug your script.
    reciept = Reciept.Reciept("./Reciepts/Images/Tesco-30_11_20-2322-4627.jpg")
    print(reciept.itemList)
    # print(reciept)
    # print(Files.Files().getItems("Tesco"))  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    run("hi")
    # run('PyCharm')
    # Reciept.Reciept("./reciept.jpg").checkDictionary("Tesco", "Bread", "£0.99")
    # Files.Files().addItem("Tesco", "TestItem1", "£999.99")
    # print(Files.Files().getItems("Tesco"))  # Press Ctrl+F8 to toggle the breakpoint.

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
