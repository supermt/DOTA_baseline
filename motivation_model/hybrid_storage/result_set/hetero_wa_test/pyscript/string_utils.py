def bandwidth_string_sort(x,y):
    if len(x) < len(y):
        return True
    else:
        return x < y


def pk_list_to_columns(primary_key_list):
    data_row = ""
    data_row += '"%s",' % primary_key_list[0]
    data_row += '"%s",' % primary_key_list[1]
    
    if "&" in primary_key_list[-4]: 
        media_string = primary_key_list[-4].split("&")[0].split(
            "_")[1] + "+" + primary_key_list[-4].split("&")[1].split("_")[1]
        media1_size = primary_key_list[-4].split("&")[0].split("_")[0]
    else:
        media_string = primary_key_list[-4].replace("_"," ")
        media1_size = "10GB"
    data_row += '"%s",' % media_string
    data_row += '"%s",' % media1_size

    data_row += '"%s",' % primary_key_list[-2]
    data_row += '"%s",' % primary_key_list[-1]
    return data_row