brands = ["nike", "jordan", "puma", "adidas", "reebok"]
colors = ["black", "white", "red", "yellow", "green", "gray", "blue", "beige", "brown", "orange"]
types = ["sneakers", "hoodie", "outerwear", "pants"]


# Funcion to pack items into dict with more useful structure.
# add_size parameter is used if front needs to show size in list of items
# (used to show items in cart)
def pack_items(db_result, add_size = False):
    # Array for items.
    items_to_send = []
    # Make dict for every item and add it to final array.
    for i, _ in enumerate(db_result):
        tmp = list(db_result[i])
        tmp_dict = {"item_id" : tmp[0], "name" : tmp[1], "price" : tmp[2], "main_photo_src" : tmp[3]}
        # If front needs to know size (used to show items cart)
        if add_size:
            tmp_dict["size"] = tmp[4]

        items_to_send.append(tmp_dict)
                
    return {"items" : items_to_send, "item_counter" : len(items_to_send)}

