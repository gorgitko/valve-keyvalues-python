# using the optional functions

from valve_keyvalues_python.keyvalues import KeyValues

filename_vdf = "example_02.vdf"

kv = KeyValues(filename=filename_vdf, key_modifier=str.upper, key_sorter=sorted)

# all keys modified to uppercase, key sorted alphabetically
print(kv)

kv["AAA"] = "I want to be first."
print(kv.dump())

print(print(kv) == print(kv.dump()))