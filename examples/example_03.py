# "advanced" uses

from valve_keyvalues_python.keyvalues import KeyValues

filename_vdf = "example_02.vdf"

def key_modifier(key):
    return key.lower() + "_modified"

def reverse_sorter(keys):
    return sorted(keys, reverse=True)

kv = KeyValues()
kv.parse(filename_vdf)
print(kv)

# modify the keys
kv.parse(filename_vdf, key_modifier=key_modifier)
print(kv)

# print sorted alphabetically descending
print(kv.dump(key_sorter=reverse_sorter))

# print keys reversed
print(kv.dump(key_sorter=reversed))