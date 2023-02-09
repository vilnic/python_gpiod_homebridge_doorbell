import toml
import requests
from periphery import GPIO

def read_toml():
    with open("config.toml") as f:
        return toml.load(f)


def compose_url(config, element):
    host = config.get('host') or 'localhost'
    port = config.get('port') or 9091
    value = config.get('value') or 'value'
    return 'http://{}:{}/{}?{}='.format(host, port, element, value)


def send_to_homebridge(config, element, value):
    url = compose_url(config, element)
    num = 1 if value else 0
    res = requests.get(url + str(num))
    return res.status_code < 300

def main():
    the_toml = read_toml()
    config = the_toml['config']
    del the_toml['config']

    # putting everything in try block to close GPIO on exit
    try:
        # setting up current GPIO elements
        for element in the_toml:
            print("Setting up GPIO pin {} for {}".format(the_toml[element]['GPIO_pin'], element))
            the_toml[element]['GPIO_reader'] = GPIO(the_toml[element]['GPIO_pin'], "in")
            the_toml[element]['state'] = the_toml[element]['GPIO_reader'].read()
            send_to_homebridge(config, element, the_toml[element]['state'])

        # running loop
        while True:
            for element in the_toml:
                new_state = the_toml[element]['GPIO_reader'].read()
                if new_state != the_toml[element]['state']:
                    the_toml[element]['state'] = new_state
                    send_to_homebridge(config, element, new_state)

    except KeyboardInterrupt:
        pass

    # closing GPIO on exit
    for element in the_toml:
        the_reader = the_toml[element].get('GPIO_reader')
        if the_reader:
            the_reader.close()

if __name__ == "__main__":
    main()
