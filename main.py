import os
import sys
import math
import json
import pytesseract
from PIL import Image
from datetime import datetime
from collections import defaultdict
from itertools import combinations, chain

from env import MENU_LIST, USERS_LIST

def printHeader(header_spacer, margin_spacer, heading):
    """
    This Function generates header

    Args:
        header_spacer (int): length of design char
        margin_spacer (int): length of spaces
        heading (str): heading string
    """
    print('\n')
    print('=' * header_spacer)
    print('\n {0}{1}\n'.format(' '  * margin_spacer, heading))
    print('=' * header_spacer)

def convertImageToRawText():
    
    """
    This Function converts uploaded screenshot image data into text
    using Optical Character Recognition Technique.

    Args:
        image_name_with_path (str): image file path

    Returns:
        str: string object (image to text converted)
    """
    ss_queue = []
    print('\nEnter Screenshot details : ')
    ss_count = int(input('\nEnter number of screenshots to be uploaded : '))
    for _ in range(ss_count):
        ss_input = input('\nPlease enter path of the screenshot : ')
        ss_queue.append(ss_input)
    try:
        while ss_queue:
            image_name_with_path = ss_queue.pop(0)
            if os.path.exists(image_name_with_path):
                image_to_str_obj = pytesseract.image_to_string(Image.open(image_name_with_path))
            filename = writingImageToStringObjToFile(image_to_str_obj)
        return filename
    except Exception as e:
        print('\nError while converting image to text : {0}'.format(e))
        sys.exit(1)

def formatItemsDataFileUpload():

    """
    This Function formates the text data in file to a
    proper JSON object containing item data.

    Returns:
        JSON str: item data along with name and price of each
        item under respective categories.
    """

    stack = []
    queue = []
    data = []
    result_list = []
    new_formatted_item_list = []
    product_store = defaultdict()
    temp_dict = defaultdict()
    menu_list = MENU_LIST
    
    input_data = input('\nPlease Enter file path : ')
    
    if not os.path.exists(input_data):
        print('\nInvalid Path!')
        sys.exit(1)
    
    with open(input_data, 'r')as p:
        lines = p.readlines()

    for line in lines:
        line = line.strip('\n')
        if line != '':
            new_formatted_item_list.append(line)
    
    new_formatted_item_list.append('HEB')

    for product in new_formatted_item_list:
        if not product in menu_list:
            stack.append(product)
        else:
            queue.append(product)
            if stack:
                category = queue.pop(0)
                while stack:
                    itm = stack.pop()
                    if itm.startswith('Qty:'):
                        if temp_dict:
                            temp_dict['name'] = list(set(data))
                            result_list.append(temp_dict)
                            temp_dict = defaultdict()
                            data = []
                        temp_dict['Qty'] = itm.split(':')[1]
                    elif itm.startswith('$'):
                        temp_dict['price'] = itm
                    else:
                        data.append(itm)
                if temp_dict:
                    temp_dict['name'] = list(set(data))
                    result_list.append(temp_dict)
                    temp_dict = defaultdict()
                    data = []
                product_store[category] = result_list
                result_list = []
    
    products_info_json = json.dumps(product_store, indent=4)

    if not stack:
        return products_info_json

def userInputForFileOrSs():

    """
    This Function allows user to 
    upload items data as a file or
    as a screen shot

    Returns:
        JSON obj str: JSON of items with
        name, price and Qty for each item. 
    """
    
    print('\nPlease select from below two options : \n')

    menu_list = {
        1 : 'Upload a File having items list',
        2 : 'Upload screenshots'
    }

    for key, val in menu_list.items():
        print(f'\n{key}. {val}')
    
    user_input = int(input('\nSelect option : '))
    
    if user_input and user_input in menu_list:
        if user_input == 1:
            json_item_data = formatItemsDataFileUpload()
        else:
            json_item_data = generateFormatedItemsListFromSs()
    
    return json_item_data

def writingImageToStringObjToFile(image_to_str_obj):

    """
    This Functions writes the text data to a file

    Args:
        image_to_str_obj (str): image to text converted file
    
    Returns:
        str: filename
    """

    filename = '_'.join(
        [
        'image_text_converted',
        str(datetime.utcnow().date()),
        str(datetime.utcnow().time()).split('.')[0].replace(':', '_')
        ]
    )
    try:
        with open(filename, 'a')as p:
            p.write(image_to_str_obj)
        return filename
    except Exception as e:
        print('\nUnable to write to file : {0}'.format(e))
        sys.exit(1)
    
def readingDataFromFile(file_name):
    
    """
    This Function reads the data in file
    using readlines function of file context manager.

    Args:
        file_name (file obj)): image to text converted data file

    Returns:
        list: reads every line and appends it to a list
    """
    
    try:
        with open(file_name, 'r')as q:
            lines = q.readlines()
        return lines
    except Exception as e:
        print('\nError occured while reading file : {0}'.format(e))
        sys.exit(1)

def generateFormatedItemsListFromSs():
    
    """
    This Function formates the text data in file to a
    proper JSON object containing item data.

    Returns:
        str: item data along with name and price of each
        item under respective categories.
    """
    stack = []
    queue = []
    local_store = {}
    final_dict = defaultdict(list)

    file_name_text = convertImageToRawText()
    lines = readingDataFromFile(file_name_text)
    menu = MENU_LIST

    for item_type in menu:
        final_dict[item_type]
    
    for item in lines:
        item = item.strip('\n')
        if item in menu:
            queue.append(item)
            if stack[-1].startswith('$'):
                item_typ = queue.pop(0)
                while stack:
                    itm_data = stack.pop()
                    if itm_data.startswith('$'):
                        if local_store:
                            get_store = local_store.copy()
                            final_dict[item_typ].append(get_store)
                            local_store.clear()
                        name = ''
                        local_store['price'] = itm_data
                    else:
                        name += itm_data
                        local_store['name'] = name
                if local_store:
                    get_store = local_store.copy()
                    final_dict[item_typ].append(get_store)
                    local_store.clear()
        else:
            if item != '':
                stack.append(item)
    
    return json.dumps(final_dict, indent=4)

def userDeatilsForTags():

    """
    This Function gets the user details
    for tags generation

    Returns:
        list and dict: user tags list and 
        tags - user map
    """
    user_tag = []
    user_tag_final = []
    user_initial_map = defaultdict()
    
    if USERS_LIST:
        users_count = len(USERS_LIST)
        for i in range(users_count):
            user_name = USERS_LIST[i]
            user_tag.append(user_name[0])
            user_initial_map[user_name[0]] = user_name
    else:
        users_count = int(input('\nTotal Number of Users : '))
        for _ in range(users_count):
            if not USERS_LIST:
                user_name = input('\nEnter User Name : ')
                user_tag.append(user_name[0])
                user_initial_map[user_name[0]] = user_name
    
    tags_list = list(chain(*map(lambda x: combinations(user_tag, x), range(1, users_count+1))))
    
    for j in tags_list:
        user_tag_final.append(''.join(j))
    
    return user_tag_final, user_initial_map

def addTagsToItems(json_data):

    """
    This Function adds user tags to each
    item in basket

    Args:
        json_data (json object): json items data

    Returns:
        list, str, user_initial_map: user-item-allocation list
        max_combination_of_users_str, user-initial-map
    """
    user_item_allot_details = []

    user_details, user_initial_mp = userDeatilsForTags()
    
    print('\nPlease add tag to each item displayed below : ')
    
    json_data = json.loads(json_data)
    
    for key,val in json_data.items():
        print('\nCategory : {0}'.format(key))
        print('-' * 50)
        for item in val:
            print(f' \nName of item : {item["name"]}\n')
            print(f'Price of item : {item["price"]}\n')
            print(f'Select Tags {user_details}')
            while 1:
                user_tag = input('\nEnter Tag [Press ENTER To split equally]: ')
                print('=' * 10)
                if not user_tag:
                    user_tag = user_details[-1]
                user_tag = user_tag.upper()
                if not user_tag in user_details:
                    print('\nThis tag is not present in above list')
                else:
                    break
            user_item_allot_details.append([user_tag, float(item["price"].split()[-1][1:])])
    
    return user_item_allot_details, user_details[-1], user_initial_mp

def doSplit(user_item_map):

    """
    This Function generates dict containing user initial
    as key and split amount as value for each item.

    Args:
        user_item_map (list): list of tuples having user
        and amount details.

    Returns:
        dict: dict containing user as key and value as list of
        split amounts for each item.
    """
    temp_dict = defaultdict(list)
    for users, amount in user_item_map:
        for user in users:
            ind_amt = round(amount/len(users), 3)
            temp_dict[user].append(ind_amt)
    return temp_dict

def generateSplitBill(user_item_map, user_det, user_ini_map):

    """
    This Function generates the splits
    between users and provides verification
    efforts.

    Args:
        user_item_map (dict): Dict having user and 
        amount for each item. 
        user_det (str): combinations of all user initials
        user_ini_map (dict): user-initial map
    """

    total_sum = 0
    order_sum = 0

    print('\nVerifying Billing details : ')
    print('-' * 30)

    tax_amt = input('\nEnter Tax Amount [Press enter for $0.14]: ')
    del_fee = input('\nEnter Delivery fee [Press enter for $6.95]: ')

    if not tax_amt:
        tax_amt = 0.14

    if not del_fee:
        del_fee = 6.95
    
    split_dict = doSplit(user_item_map)
    
    tax_split = float(tax_amt)/3
    del_fee_split = float(del_fee)/3
    
    for key, val in split_dict.items():
        total_split = sum(val)
        total_sum += total_split
        split_dict[key] = total_split + tax_split + del_fee_split
        order_sum += split_dict[key]

    print(f'\nSub Total : {total_sum}')

    print(f'\nTotal : {order_sum}')

    printHeader(50, 15, 'BILL SPLIT SUMMARY')

    for key,val in split_dict.items():
        print(f'\n{user_ini_map[key]} has to Pay ${round(val, 3)}')
    
if __name__ == "__main__":

    printHeader(70, 25, 'HEB SPLIT CLI TOOL')
    
    json_data = userInputForFileOrSs()
    
    try:
        json_obj = json.loads(json_data).values()
        for val in json_obj:
            if not val:
                print("\nSomething went wrong when converting and formating the data!")
    except Exception as e:
        print('\nError occurred while fetching item data!')
        sys.exit(1)
    
    get_user_item_map, user_det, user_ini_map = addTagsToItems(json_data)
    
    generateSplitBill(get_user_item_map, user_det, user_ini_map)
    
    print('\nThank you, see you again!\n')
    










