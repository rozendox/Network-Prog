import pynput


def on_press(key):
    try:
        print(f'alphanumeric key: {key.char}')
    except AttributeError:
        print(f'special key: {key}')


def on_release(key):
    if key == pynput.keyboard.Key.esc:
        print('Exiting...')
        return False


with pynput.keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()

