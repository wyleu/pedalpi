"""
sudo apt-get install idle
sudo apt-get install rpi.gpio
"""

import time
import rtmidi

try:
    import RPi.GPIO as GPIO
except RuntimeError:
    print("""Error importing RPi.GPIO!  """)

print('Mode:-', GPIO.getmode())
GPIO.setmode(GPIO.BOARD)
print('Mode:-', GPIO.getmode())

print(GPIO.RPI_INFO)
print(GPIO.RPI_INFO['P1_REVISION'])
print(GPIO.VERSION)

PEDAL_RPI_MAPPING = [
    ['C3' , 36, 40],
    ['C#3', 37, 38],
    ['D3' , 38, 37],
    ['D#3', 39, 36],
    ['E3' , 40, 33],   # Wiring Error F <> E
    ['F3' , 41, 35],   # Wiring Error E <> F
    ['F#3', 42, 32],
    ['G3' , 43, 31],
    ['G#3', 44, 29],
    ['A3' , 45, 26],
    ['A#3', 46, 24],
    ['B3' , 47, 23],
    ['C4' , 48, 22],
    ]

PEDAL_NORMALLY_CLOSED = True

[pedal.append(PEDAL_NORMALLY_CLOSED) for pedal in PEDAL_RPI_MAPPING]

class Bad_Mode(Exception):
    pass



class ReedNote(object):

    def __init__(self, args):
        self.GPIO_MODE = {
        'poll': self.poll,
        'wait': self.wait,
        'event':self.event,
        'callback': self.callback
        }

        self.gpi_mode = self.GPIO_MODE['wait']
        
        self.name=args[0]
        self.midi=args[1]
        self.io=args[2]

        self.pressed = 0  # Not Pressed

    def read_reed(self):
        return self.gpi_mode()

    def poll(self):
        return (self.name, GPIO.input(self.io))

    def wait(self):
        return (self.name,
                GPIO.wait_for_edge(
                    self.io,
                    GPIO.RISING,
                    timeout=5000
                    )
                )
    def event(self):
        return (self.name, None)

    def callback(self):
        return (self.name, None)

    def my_callback_two(self, channel):
        try:
            pressed =  GPIO.input(channel)  # pressed == 0 for magnet close

            if pressed and not self.pressed:
                print('Pressed:', channel, self.name)   #NO enabled
                note = self.midi_channel.make_note(5, 60, 112)
                
            elif pressed and self.pressed:
                pass
                print('STILL PRESSED', channel, self.name)
            elif not pressed and self.pressed:
                print('Release:', channel, self.name)  #NO Pulled up
                note.note_off()
                
            elif not pressed and not self.pressed:
                pass #print('Note finished .  . . . ')

            self.pressed = pressed
            # print('--------------')
        except KeyboardInterrupt:
            exit

    def set_gpio_mode(self, mode):
        if mode not in self.GPIO_MODE.keys():
            raise Bad_Mode
        self.gpio_mode = self.GPIO_MODE[mode]

    def clear_midi(self):
        del self.midiout


class MidiNote(object):
    def __init__(self, mchannel, note=60, velocity=64):
        self.mchannel = mchannel
        self.note = note
        self.velocity = velocity
        self.note_on = [0x90 + self.mchannel.channel, self.note , self.velocity]
        self.mchannel.midiout.send_message(self.note_on)

    def note_off(self):
        self.note_off = [0x80 + self.mchannel.channel, self.note , self.velocity]
        self.mchannel.midiout.send_message(self.note_off)

    def play_test_piece(self):
        cardiacs = (
            (60,0.5),
            (65,0.5),
            (65,0.25),
            (69,0.5),
            (71,0.5),
            (72,0.5),
            (77,0.5),
            (65,0.5),
            )
        for note,length in cardiacs:
            print('Playing test piece note %s' % note)
            self.note_on = [0x90 + self.mchannel.channel, note , self.velocity]
            self.mchannel.midiout.send_message(self.note_on)
            time.sleep(0.1)
            self.note_off = [0x80 + self.mchannel.channel, note , self.velocity]
            self.mchannel.midiout.send_message(self.note_off)
            time.sleep(length)
            

class MidiChannel(object):
    def __init__(self, name, channel):
        print('INIT_MIDI on channel %s' % channel)
        self.midiout = rtmidi.MidiOut()
        self.channel = channel
        
        self.available_ports = self.midiout.get_ports()
        print('MIDI OUT get_ports', len(self.available_ports), self.available_ports)

        if self.available_ports:
            self.midiout.open_port(0)
        else:
            print('Virtual Port:', name)
            self.midiout.open_virtual_port(name)

        port_count= self.midiout.get_port_count()
        print ('OUT Port Count:-', port_count )
        for i in range (port_count):
            print (self.midiout.get_port_name(i))

    def close_midi(self):
        del self.midiout

    def play_note(channel, note, velocity):
        return MidiNote(self.channel, note, velocity)

    def play_test_piece(self):
        midi_note = MidiNote(self)
        midi_note.play_test_piece()
        
    

midi_channel = MidiChannel('Pedalboard', 3)  
            
class PedalBoard(object):
    def __init__(self, mapping, midi_channel):
        self.midi_channel = midi_channel
        self.reeds = [ReedNote(item) for item in mapping]
        
           
    def config_gpio(self):
        self.normally_closed = PEDAL_NORMALLY_CLOSED
        for reed in self.reeds:
            try:
                GPIO.setup(reed.io, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            except RuntimeWarning:
                print('in :-',reed)
                raise

    def add_callbacks(self):
        for reed in self.reeds:
            GPIO.add_event_detect(reed.io, GPIO.BOTH, bouncetime=200)
            GPIO.add_event_callback(reed.io, reed.my_callback_two)


    def read(self):
        for reed in self.reeds:
            if self.normally_closed:
                if not reed.read_reed()[1]:
                    print('NC:',reed.name)
            else:
                if reed.read_reed()[1]:
                    print('NO:',reed.name)

            print('.')


        
