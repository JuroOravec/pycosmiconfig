from pycosmiconfig import cosmiconfig

exporer = cosmiconfig("example")
res = exporer.search()
print(res)
print(res.config)
print(res.config["hello"])
