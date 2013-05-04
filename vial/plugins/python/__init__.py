from vial import manager

def init():
    manager.on('filetype:python', python_buffer)

def python_buffer(buf):
    pass
