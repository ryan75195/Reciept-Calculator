class Files:
    def __init__(self):
        pass

    def addItem(self,Store, ItemName, ItemValue):
        file = open(f"./{Store}.txt", "a")
        file.write(f"{''.join(ItemName.rstrip().lstrip())},{ItemValue.rstrip()}\n")
        file.flush()
        file.close()


    def getItems(self, Store):
        file = open(f"./{Store}.txt", "r")
        dict = {}
        for line in file:
            # print(line)
            name,price = line.strip("\n").split(",")
            dict[name] = price

        # print(dict)
        return dict