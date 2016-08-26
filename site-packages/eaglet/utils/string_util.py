# -*- coding: utf-8 -*-

__author__ = 'chuter'

import binascii

def __is_hex_char(char):
    assert (char is not None)

    char = char.upper()
    return (ord(char) >= ord('0') and ord(char) <= ord('9')) or\
         (ord(char) >= ord('A') and ord(char) <= ord('F'))

def is_hax_str(hex_str):
    if hex_str is None or len(hex_str) == 0:
        return False

    if len(hex_str) % 2 != 0:
        return False

    for char in hex_str:
        if not __is_hex_char(char):
            return False

    return True

def byte_to_hex(byte_str, join_with=''):
    """
    Convert a byte string to it's hex string representation e.g. for output.
    """

    if byte_str is None or len(byte_str) == 0:
        return byte_str

    if isinstance(byte_str, unicode):
        byte_str = byte_str.encode('utf-8')

    if is_hax_str(byte_str):
        return byte_str
    else:
        return binascii.b2a_hex(byte_str).upper()

    # Uses list comprehension which is a fractionally faster implementation than
    # the alternative, more readable, implementation below
    #   
    #    hex = []
    #    for aChar in byte_str:
    #        hex.append( "%02X " % ord( aChar ) )
    #
    #    return ''.join( hex ).strip()        

    # return ''.join( [ "%02X%s" % (ord(x), join_with) for x in byte_str ] ).strip()

#-------------------------------------------------------------------------------

def hex_to_byte(hex_str):
    """
    Convert a string hex byte values into a byte string. The Hex Byte values may
    or may not be space separated.
    """
    # The list comprehension implementation is fractionally slower in this case    
    #
    #    hex_str = ''.join( hex_str.split(" ") )
    #    return ''.join( ["%c" % chr( int ( hex_str[i:i+2],16 ) ) \
    #                                   for i in range(0, len( hex_str ), 2) ] )

    if hex_str is None or len(hex_str) == 0:
        return hex_str

    if not is_hax_str(hex_str):
        return hex_str

    bytes = []

    hex_str = ''.join(hex_str.split(" "))

    for i in range(0, len(hex_str), 2):
        bytes.append(chr(int(hex_str[i:i+2], 16 )))

    return ''.join(bytes)