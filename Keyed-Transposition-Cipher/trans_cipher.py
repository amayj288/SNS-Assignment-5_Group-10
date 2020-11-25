from pycipher import ColTrans

key = input("Enter the Key: ")
PT = input("Enter Plain Text: ")
CT = ColTrans(key).encipher(PT)
print("Cipher Text is: ", CT)
Msg = ColTrans(key).decipher(CT)
print("Original Message is: ", Msg)
