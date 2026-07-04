import time
def find_last(word, char):
    last_index = -1
    while word.find(char) != -1:
        last_index = word.find(char)
        word = word[:last_index] + "&" + word[last_index + 1:]
    return last_index

p = {"block_back"}
pr = {1, 2, 3, 4, "block_back"}
print(list(pr))

def remove_duplicates(garbage_list) -> list:
    clean_list = []
    for garbage in garbage_list:
        if garbage not in clean_list:
            clean_list.append(garbage)
    return clean_list