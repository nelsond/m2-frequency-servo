import socket
import json
import random

class M2:
    def __init__(self, addr, interface=False):
        self.socket = socket.create_connection(addr)
        self.transmission_id = 0

        if (interface):
            self.connect_from(interface)

    def connect_from(self, interface):
        response_message = self.send_message(
            op= 'start_link',
            params= { 'ip_address': interface })

        return response_message.is_ok(status="ok")

    def set(self, setting, value):
        response_message = self.send_message(
                op=setting,
                params={ 'setting': [ value ] })

        return response_message.is_ok(status=[0])

    def close_connection(self):
        self.socket.close()

        return True

    def send_message(self, **kwargs):
        message = M2Message(**kwargs)

        self.socket.send(message.to_json())
        response_json = self.socket.recv(1024)

        return M2Message.from_json(response_json)

class M2Message:
    def __init__(self, op, params, transmission_id=False):
        self.op = op
        self.params = params

        if (transmission_id):
            self.transmission_id = transmission_id
        else:
            self.transmission_id = random.randint(1, 999)

    @classmethod
    def from_json(klass, json_string):
        msg = json.loads(json_string)['message']

        op              = msg['op']
        params          = msg['parameters']
        transmission_id = msg['transmission_id'][0]

        return klass(op, params, transmission_id)

    def message(self):
        return {
            'transmission_id': [self.transmission_id],
            'op': self.op,
            'parameters': self.params
        }

    def to_json(self):
        return json.dumps({'message': self.message()})

    def is_ok(self, status='ok'):
        if 'status' in self.params:
            return self.params['status'] == status
        else:
            return None

if __name__ == "__main__":
    m2 = M2(('128.138.107.135', 39933))
    print m2.connect_from('128.138.107.134')
    print m2.set('tune_resonator', 50.0)
