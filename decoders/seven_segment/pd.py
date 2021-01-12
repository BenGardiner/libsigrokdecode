##
## This file is part of the libsigrokdecode project.
##
## Copyright (C) 2019 Benedikt Otto <benedikt_o@web.de>
##
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program; if not, see <http://www.gnu.org/licenses/>.
##

import sigrokdecode as srd

class ChannelError(Exception):
    pass

# The segment names:
#  A
# F B
#  G
# E C
#  D
#
#    A  B  C  D  E  F  G
digits = {
    (0, 0, 0, 0, 0, 0, 0): ' ',
    (0, 1, 0, 0, 0, 1, 0): '"',
    (1, 1, 0, 1, 1, 1, 1): "&",
    (0, 0, 0, 0, 0, 1, 0): "'",
    (0, 1, 0, 0, 0, 0, 0): "'",
    (0, 0, 1, 1, 0, 0, 0): ',',
    (0, 0, 0, 0, 0, 0, 1): '-',
    (0, 0, 0, 0, 1, 0, 0): '.',
    (1, 0, 0, 0, 0, 0, 1): '=',
    (0, 0, 0, 1, 0, 0, 1): '=',
    (1, 1, 0, 0, 1, 0, 1): '?',
    (1, 1, 0, 0, 0, 1, 0): '^',
    (0, 0, 0, 1, 0, 0, 0): '_',
    (1, 1, 1, 1, 1, 1, 0): '0',
    (0, 1, 1, 0, 0, 0, 0): '1',
    (1, 1, 0, 1, 1, 0, 1): '2',
    (1, 1, 1, 1, 0, 0, 1): '3',
    (0, 1, 1, 0, 0, 1, 1): '4',
    (1, 0, 1, 1, 0, 1, 1): '5',
    (1, 0, 1, 1, 1, 1, 1): '6',
    (1, 1, 1, 0, 0, 1, 0): '7',
    (1, 1, 1, 0, 0, 0, 0): '7',
    (1, 1, 1, 1, 1, 1, 1): '8',
    (1, 1, 1, 1, 0, 1, 1): '9',
    (1, 1, 1, 0, 1, 1, 1): 'A',
    (1, 1, 1, 1, 1, 0, 1): 'a',
    (0, 0, 1, 1, 1, 1, 1): 'b',
    (1, 0, 0, 1, 1, 1, 0): 'C',
    (0, 0, 0, 1, 1, 0, 1): 'c',
    (0, 1, 1, 1, 1, 0, 1): 'd',
    (1, 0, 0, 1, 1, 1, 1): 'E',
    (1, 0, 0, 0, 1, 1, 1): 'F',
    (1, 0, 1, 1, 1, 1, 0): 'G',
    (0, 1, 1, 0, 1, 1, 1): 'H',
    (0, 0, 1, 0, 1, 1, 1): 'h',
    (0, 0, 0, 0, 1, 1, 0): 'I',
    (1, 0, 0, 0, 1, 0, 0): 'i',
    (0, 0, 1, 0, 0, 0, 0): 'i',
    (0, 1, 1, 1, 1, 0, 0): 'J',
    (0, 1, 1, 1, 0, 0, 0): 'J',
    (1, 0, 1, 1, 0, 0, 0): 'j',
    (1, 0, 1, 0, 1, 1, 1): 'K',
    (0, 0 ,0, 1, 1, 1, 0): 'L',
    (1, 0, 1, 0, 1, 0, 0): 'M',
    (1, 0, 1, 0, 1, 0, 1): 'M',
    (1, 1, 1, 0, 1, 1, 0): 'N',
    (0, 0, 1, 0, 1, 0, 1): 'n',
    (0, 0, 1, 1, 1, 0, 1): 'o',
    (1, 1, 0, 0, 1, 1, 1): 'p',
    (1, 1, 1, 0, 0, 1, 1): 'q',
    (1, 1, 0, 0, 1, 1, 0): 'R',
    (0, 0, 0, 0, 1, 0, 1): 'r',
    (0, 0, 0, 1, 1, 1, 1): 't',
    (0, 0, 1, 1, 1, 0, 0): 'u',
    (0, 1, 0, 1, 0, 1, 0): 'V',
    (0, 1, 0, 0, 1, 1, 1): 'V',
    (0, 1, 1, 1, 1, 1, 0): 'V',
    (0, 1, 0, 0, 0, 1, 1): 'v',
    (0, 1, 0, 1, 0, 1, 1): 'W',
    (0, 0, 1, 0, 1, 0, 0): 'x',
    (0, 1, 1, 1, 0, 1, 1): 'y',
    (1, 1, 0, 1, 1, 0, 0): 'Z',
}

class Decoder(srd.Decoder):
    api_version = 3
    id = 'seven_segment'
    name = '7-segment'
    longname = '7-segment display'
    desc = '7-segment display protocol.'
    license = 'gplv2+'
    inputs = ['logic']
    outputs = []
    tags = ['Display']
    channels = (
        {'id': 'a', 'name': 'A', 'desc': 'Segment A'},
        {'id': 'b', 'name': 'B', 'desc': 'Segment B'},
        {'id': 'c', 'name': 'C', 'desc': 'Segment C'},
        {'id': 'd', 'name': 'D', 'desc': 'Segment D'},
        {'id': 'e', 'name': 'E', 'desc': 'Segment E'},
        {'id': 'f', 'name': 'F', 'desc': 'Segment F'},
        {'id': 'g', 'name': 'G', 'desc': 'Segment G'},
    )
    optional_channels = (
        {'id': 'dp', 'name': 'DP', 'desc': 'Decimal point'},
    )
    options = (
        {'id': 'polarity', 'desc': 'Expected polarity',
            'default': 'common-cathode', 'values': ('common-cathode', 'common-anode')},
        {'id': 'show_unknown', 'desc': 'Display Unknown characters as #',
            'default': 'no', 'values': ('yes', 'no')},
    )
    annotations = (
        ('decoded-digit', 'Decoded digit'),
    )
    annotation_rows = (
        ('decoded-digits', 'Decoded digits', (0,)),
    )

    def __init__(self):
        self.reset()

    def reset(self):
        pass

    def start(self):
        self.out_ann = self.register(srd.OUTPUT_ANN)

    def putb(self, ss_block, es_block, data):
        self.put(ss_block, es_block, self.out_ann, data)

    def pins_to_hex(self, pins):
        return digits.get(pins, None)

    def decode(self):
        oldpins = self.wait()

        # Check if at least the 7 signals are present.
        if False in [p in (0, 1) for p in oldpins[:7]]:
            raise ChannelError('7 or 8 pins have to be present.')

        lastpos = self.samplenum

        self.have_dp = self.has_channel(7)

        conditions = [{0: 'e'}, {1: 'e'}, {2: 'e'}, {3: 'e'}, {4: 'e'}, {5: 'e'}, {6: 'e'}]

        if self.have_dp:
            conditions.append({7: 'e'})

        while True:
            # Wait for any change.
            pins = self.wait(conditions)

            if self.options['polarity'] == 'common-anode':
                # Invert all data lines if a common anode display is used.
                if self.have_dp:
                    oldpins = tuple((1 - state for state in oldpins))
                else:
                    oldpins = tuple((1 - state for state in oldpins[:7]))

            # Convert to character string.
            digit = self.pins_to_hex(oldpins[:7])

            if digit is None and self.options['show_unknown'] == 'yes':
                digit = '#'

            if digit is not None:
                dp = oldpins[7]

                # Check if decimal point is present and active.
                if self.have_dp and dp == 1:
                    digit += '.'

                self.putb(lastpos, self.samplenum, [0, [digit]])

            lastpos = self.samplenum

            oldpins = pins
