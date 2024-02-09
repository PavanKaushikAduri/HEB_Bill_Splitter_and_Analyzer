                if local_store:
                    get_store = local_store.copy()
                    final_dict[item_typ].append(get_store)
                    local_store.clear()