import os
debug = not os.path.isfile(
                os.path.join(
                    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    '.sudo_as_admin_successful'
                )
            )

def empty(x):
    return (not x) and (x is not 0)

def exist(f, x):
    return x in f and not empty(f[x])