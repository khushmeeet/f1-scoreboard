def datetime_format(value, format="%d-%m-%y"):
    return value.strftime(format)

def laptime_format(value, format="%M:%S.%f"):
    return value.strftime(format)[1:-3]
