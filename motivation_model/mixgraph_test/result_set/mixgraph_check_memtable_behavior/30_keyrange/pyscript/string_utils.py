def bandwidth_string_sort(x,y):
    if len(x) < len(y):
        return True
    else:
        return x < y


def pk_list_to_columns(primary_key_list):
    data_row = ""

    data_row += '"%s",' % primary_key_list[-3].replace("StorageMaterial.","")
    data_row += '"%s",' % primary_key_list[-2]
    data_row += '"%s",' % primary_key_list[-1]
    return data_row