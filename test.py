"""
test.py
"""
import unittest
import time

from pedalpi import (
    PEDAL_RPI_MAPPING,
    MidiChannel,
    PedalBoard
    )


class MidiNoteTest(unittest.TestCase):
    def test_play_test_piece(self):
        midi_channel = MidiChannel('MidiChannel TestChannel', 2)

        for itme in range(10):
            midi_channel.play_test_piece()
            time.sleep(1)



##class PedalBoardTest(unittest.TestCase):
##    def test_upper(self):
##        midi_channel = MidiChannel('PedalBoard TestChannel')
##        pedal = PedalBoard(PEDAL_RPI_MAPPING, midi_channel)
##        self.assertEqual(len(pedal.reeds), 13)
##        pedal.config_gpio()
##        self.assertEqual(len(pedal.reeds), 13)
##        pedal.add_callbacks()


if __name__ == '__main__':
    unittest.main()
