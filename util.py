def changeOrAddConfig(key, value,file):
    with open(file, "r") as f:
        lines = f.readlines()
    isExist = False
    with open(file, "w") as f:
        for line in lines:
            if line.startswith(key+"=") or line.startswith("#"+key+"="):
                line = f"{key}={value}\n"
                isExist = True
            f.write(line)
    if not isExist:
        with open(file, "a") as f:
            f.write(f"{key}={value}\n")