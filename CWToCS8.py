#!/usr/bin/env python
import sys
import numpy

def make_am_samples(amplitude, length_units, frequency=300.0):
    sample_rate = 48000
    unit_seconds = 0.05
    length_samples = int(round(unit_seconds * length_units * sample_rate))
    t = numpy.arange(length_samples, dtype=numpy.float32) / sample_rate

    carrier = amplitude * (1 + 0.5 * numpy.sin(2 * numpy.pi * frequency * t))
    return carrier.astype(numpy.float32)

def make_fm_samples(amplitude, length_units, carrier_frequency=100000.0, modulation_frequency=1000.0, deviation=75000.0, sample_rate=48000):
    unit_seconds = 0.05
    length_samples = int(round(unit_seconds * length_units * sample_rate))
    t = numpy.arange(length_samples, dtype=numpy.float32) / sample_rate
    instantaneous_phase = (2 * numpy.pi * carrier_frequency * t + (deviation / modulation_frequency) * numpy.sin(2 * numpy.pi * modulation_frequency * t))

    signal_fm = amplitude * numpy.sin(instantaneous_phase)
    return signal_fm.astype(numpy.float32)

def convert_to_CW(message: str, modulation: str = 'AM'):
    character_to_symbols_map = {
        'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.',
        'F': '..-.', 'G': '--.', 'H': '....', 'I': '..', 'J': '.---',
        'K': '-.-', 'L': '.-..', 'M': '--', 'N': '-.', 'O': '---',
        'P': '.--.', 'Q': '--.-', 'R': '.-.', 'S': '...', 'T': '-',
        'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-', 'Y': '-.--',
        'Z': '--..',
        '1': '.----', '2': '..---', '3': '...--', '4': '....-', '5': '.....',
        '6': '-....', '7': '--...', '8': '---..', '9': '----.', '0': '-----',
        ' ': ' ',
        'É': '..-..', '.': '.-.-.-', ',': '--..--', ':': '---...',
        '?': '..--..', '!': '-.-.--', '\'': '.----.', '-': '-....-', '|': '-..-.',
        '(': '-.--.-', ')': '-.--.-', 'À': '.--.-', '@': '.--.-.',
        '<': '-.-.-', '>': '.-.-.', '+': '.-.-.', '/': '-..-.', '=': '-...-',
    }
    amplitude = 127
    dot_units = 1
    dash_units = dot_units * 3
    space_internal_units = 1
    space_letters_units = 3
    space_words_units = 7

    if modulation.upper() == 'AM':
        make_samples = make_am_samples
    elif modulation.upper() == 'FM':
        make_samples = make_fm_samples
    else:
        raise ValueError("Unsupported modulation type")

    baseband_dot = make_samples(1, dot_units)
    baseband_dash = make_samples(1, dash_units)
    baseband_between_symbols = make_samples(0, space_internal_units)
    baseband_between_letters = make_samples(0, space_letters_units - space_internal_units)
    baseband_space = make_samples(0, space_words_units - space_letters_units - space_internal_units)

    symbol_to_baseband_map = {
        '.': baseband_dot,
        '-': baseband_dash,
        ' ': baseband_space,
    }

    output = [baseband_space]
    full_message = ' < ' + message.upper() + ' > '

    for character in full_message:
        if character not in character_to_symbols_map:
            raise ValueError(f"Character not supported in Morse mapping: {repr(character)}")

        symbols = character_to_symbols_map[character]
        for symbol in symbols:
            output.append(symbol_to_baseband_map[symbol])
            output.append(baseband_between_symbols)
        output.append(baseband_between_letters)

    output.append(baseband_space)
    ouput = numpy.concatenate(output).astype(numpy.float32) * amplitude
    return output

def write_toCS8(IQ, file):
    output_int = numpy.empty((len(IQ) * 2,), dtype=numpy.int8)
    output_int[0::2] = numpy.round(IQ.real).astype(numpy.int8)
    output_int[1::2] = 0
    output_int.tofile(file)

def usage():
    print("Usage:")
    print("Plaintext mode : python ./CWToCS8.py PLAINTEXT <message> <output_file> <AM|FM>")
    print("")
    print("Cipher_B64 mode: python ./CWToCS8.py CIPHER_B64 <cipher_b64> <output_file> <AM|FM>")
    print("")
    print("E.g.:")
    print(" python ./CWToCS8.py PLAINTEXT \"Hello world\" test-hello.cs8 AM")
    print(" python ./CWToCS8.py CIPHER_B64 \"BASE64_CIPHERTEXT...\" test-cipher.cs8 FM")

if __name__ == "__main__":
    if len(sys.argv) != 5:
        usage()
        sys.exit(0)

    mode = sys.argv[1].upper()
    message = sys.argv[2]
    output_file = sys.argv[3]
    modulation = sys.argv[4].upper()

    if mode not in ("PLAINTEXT", "CIPHER_B64"):
        print(f"Unknown mode: {mode}")
        usage()
        sys.exit(1)

    try:
        IQ = convert_to_CW(message, modulation)
        write_toCS8(IQ, output_file)
        print(f"[OUT] CS8 file generated: {output_file}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

