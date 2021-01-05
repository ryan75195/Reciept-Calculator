from Files import Files
import pytesseract as ps
import cv2 as cv2
import numpy as np


class Reciept:
    def __init__(self, path):
        original = cv2.imread(path)
        print(path.lstrip("/").split("-"))
        data = path.rstrip("/").split("-")


        self.store = str(data[0].split("/")[-1]).lower()
        self.date = data[1]
        self.time = data[2]
        self.payment = data[3].split(".")[0]
        print(self.store,self.date,self.time,self.payment)
        Image = self.showReciept(original)

        recieptString = ps.image_to_string(Image, lang="eng", config='--psm 1')

        self.itemList = self.getItems(recieptString, self.store)
        self.totalCost = self.getTotalCost(recieptString)

        file = open(f"/home/ryan/PycharmProjects/Reciept-Calculator/Reciepts/TextFiles/{self.store}-{self.date}-{self.time}-{self.payment}.txt", "w+")
        for item in self.itemList.keys():
            for i in range(0,int(self.itemList[item][0])):
                file.write(f"{item},{self.itemList[item][1]}\n")
        file.write(f"Total={self.totalCost}")


        # print(self.error(self.getCalculatedCost(), self.totalCost))


    def nothing(self):
        pass

    def showReciept(self, image):
        def nothing():
            pass
        cv2.namedWindow('Colorbars')
        cv2.moveWindow('Colorbars',700,100)
        Image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        cv2.imshow('Colorbars', Image)

        cv2.createTrackbar("hl", 'Colorbars', 100 , 255,lambda x:x)

        scale_percent = 40  # percent of original size
        width = int(Image.shape[1] * scale_percent / 100)
        height = int(Image.shape[0] * scale_percent / 100)
        dim = (width, height)
        # resize image

        while(1):
            low = cv2.getTrackbarPos("hl", 'Colorbars')
            (thresh, blackAndWhiteImage) = cv2.threshold(Image, low, 255, cv2.THRESH_BINARY)


            resized = cv2.resize(blackAndWhiteImage, dim, interpolation=cv2.INTER_AREA)

            cv2.imshow('Colorbars',np.array(resized, dtype = np.uint8 ))
            k = cv2.waitKey(1)
            # print(k)
            if k == 27:
                # print("true")
                break

        cv2.destroyAllWindows()

        return blackAndWhiteImage




    def getCalculatedCost(self):
        tc = 0
        for i in self.itemList.keys():
            tc += (float(self.itemList[i][0]) * float(self.itemList[i][1].strip("£")))
        print(f"£{tc}")
        return tc

    def error(self, calculated, true):
        return true - calculated

    def getDate(self, recieptString):
        pass

    def getTime(self, recieptString):
        pass

    def stripStrayCharacters(self,String):
        newString = String
        blacklist = [" x "," * "," « "," «x "]
        for i in blacklist:
            if i in newString:
                newString = newString.strip(i)
        return newString


    def checkSimilarities(self, itemName, dictKeys):
        # Things to consider:
        #   - World Length
        #   - Letter Frequency
        #   - Letter Distance
        similarites = {}
        for item in dictKeys:
            letterFrequency = {}
            for char in itemName: # add letters to dict
                letterFrequency[char] = 0
            for char in item:
                if char in letterFrequency.keys():
                    letterFrequency[char] += 1


            similarites[item] = sum(letterFrequency.values())/len(itemName)*100
            print(item + " " + str(letterFrequency))

        print(sum(letterFrequency.values()))
        # exit(0)
        vals = list(similarites.values())
        maxSimilarity = max(vals)
        closestItem = max(similarites, key=lambda key: similarites[key])
        print(similarites)
        # exit(0)
        return maxSimilarity, closestItem


    def checkDictionary(self, Store, ScannedItem, ScannedPrice):
        dict = Files().getItems(Store)
        ScannedItem = ''.join(ScannedItem.rstrip().lstrip())
        ScannedPrice = ''.join(ScannedPrice.rstrip().lstrip())

        # print("hi")
        TrueItem = ""
        TruePrice = ""

        # for item in dict:
        #     if item in ScannedItem or ScannedItem in item:
        #         ScannedItem = item

        if ScannedItem in dict.keys():
            return ''.join(ScannedItem.rstrip().lstrip()), dict[''.join(ScannedItem.rstrip().lstrip())]
        else:
            loop = True
            similar = self.checkSimilarities(ScannedItem,dict.keys()) #[0] is similarity score and [1] is closest item name
            if similar[0] > 80:
                print(f"I suspect that this item name {ScannedItem} is supposed to be {similar[1]}. is this correct?")
                response = input()
                if response == "yes":
                    TrueItem = similar[1]
                    TruePrice = dict[TrueItem]
                    loop = False
            while loop:
                print(
                    f"{''.join(ScannedItem.rstrip().lstrip())} does not appear to be stored in the dictionary, Would you like to add it? (yes/rename/skip)")
                response = input()
                TrueItem = ScannedItem
                TruePrice = ScannedPrice
                if response == "skip":
                    TrueItem = -1
                    TruePrice = -1
                    break
                if response == "rename":
                        print("Please enter the name of the item.")
                        TrueItem = input()
                        if TrueItem in dict.keys():
                            print("Item is already in dictionary")
                            TruePrice = dict[TrueItem]
                            break
                        response = "yes"

                if response == "yes":
                    print(f"Adding {TrueItem} to the dictionary, is {ScannedPrice} the correct price?")
                    response = input()
                    if response == "yes":
                        print(f"Successfully added {TrueItem} to the dictionary with price {ScannedPrice}")
                        loop = False
                    elif response == "no":
                        print("Please enter the correct price")
                        TruePrice = f"£{input()}"
                        print(f"Successfully added {TrueItem} to the dictionary with price {TruePrice}")
                        loop = False
                else:
                    print("invalid response, please try again.")
            if TrueItem != -1 and TrueItem != -1:
                Files().addItem(Store, TrueItem, TruePrice)

        # print(TrueItem,TruePrice)
        return TrueItem, TruePrice

    def getItems(self, recieptString, Store):
        nameBuffer = ""
        priceBuffer = ""
        Items = {}
        stage = "Name"
        atException = False
        for i in recieptString:
            # print(priceBuffer)
            if stage == "Name":
                if i == "@":
                    atException = True
                if "SUB-TOTAL" in nameBuffer:
                    return Items

                if "\n" in nameBuffer and nameBuffer != "" and len(priceBuffer) > 0:
                    # print(nameBuffer)
                    priceBuffer = ""
                    nameBuffer = "".join(i)
                    stage = "Name"
                elif i == "£" or i == "€" or i == "$":
                    if not atException:
                        stage = "Price"
                    else:
                        atException = False
                else:
                    nameBuffer += i
            if stage == "Price" and "\n" not in priceBuffer:
                priceBuffer += i
            if "\n" in priceBuffer:
                # print(r' '.join(nameBuffer.strip("\n").split()))
                nameBuffer = self.stripStrayCharacters(nameBuffer)
                nameBuffer, priceBuffer = self.checkDictionary(Store, ' '.join(nameBuffer.strip("\n").split()),
                                                               priceBuffer.strip("\n"))
                if nameBuffer != -1 and priceBuffer != -1:
                    if nameBuffer not in Items.keys():
                        Items[nameBuffer] = [1, priceBuffer.strip("\n")]
                    else:
                        # print(Items[nameBuffer][0])
                        Items[nameBuffer] = [str(int(Items[nameBuffer][0]) + 1), Items[nameBuffer][1]]

                # Items[nameBuffer] = priceBuffer.strip("\n")
                priceBuffer = ""
                nameBuffer = "".join(i)
                stage = "Name"

        # print(Items)
        return Items

    def getCardNumber(self, recieptString):
        buffer = ""
        Number = ""
        for i in recieptString:
            buffer += i
            if "NUMBER" in buffer and len("".join(x for x in Number if x.isdigit())) < 4:
                # print(i)
                Number += i
        # print(buffer)
        # print(Number)
        if not Number.isdigit():
            print("Cannot Read Card Number, Please Enter Correct Number:")
            Number = input()
        # print(Number)
        return Number

    def getTotalCost(self, recieptString):
        buffer = ""
        totalCost = ""
        for i in recieptString:
            buffer += i
            if "VISA DEBIT SALE" in buffer and len(totalCost) < 6 and ("£" in totalCost or i == "£"):
                totalCost += i
        # print(buffer)
        print(totalCost)
        return totalCost.strip("£")
