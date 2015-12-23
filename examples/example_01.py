# basic operations

from valve_keyvalues_python.keyvalues import KeyValues

filename_vdf = "example_01.vdf"

kv = KeyValues(filename=filename_vdf)
print(kv)
# dump only one part
print(kv.dump(mapper=kv["second"]))

kv["second"]["second_fourth"] = "second_fourth value"
kv["second"]["second_first"] = "I don't like this notation."
del kv["third"]
print(kv)