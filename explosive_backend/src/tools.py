
def getFuncName():
    import inspect
    return inspect.stack()[1][3]
