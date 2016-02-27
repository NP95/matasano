#!/usr/bin/python3

import base64
from Crypto.Cipher import AES
from Crypto.Util import Counter

def BlockXOR(b1, b2):
	"""XOR of two blocks of bytes."""
	assert len(b1) == len(b2)
	res = b''

	for bIndex in range(0, len(b1)):
		res += bytes([b1[bIndex] ^ b2[bIndex]])

	return res

def DoCTR(text, key, nonce):
	"""The algorithm is the same for both encryption and decryption."""
	# Uses ECB inside for a single block.
	cipher = AES.new(key=key, mode=AES.MODE_ECB)
	resultingText = b''

	keystream = b''
	numBlocks = int(len(text) / AES.block_size)
	counter = 0

	for blockIndex in range(0, numBlocks):
		block = text[blockIndex * AES.block_size : (blockIndex + 1) * AES.block_size]

		# The keystream generator is composed by 8 bytes of the nonce +
		# 8 bytes of counter, little-endian.
		keystreamGen = bytes([nonce]) * 8
		# This is a quick hack that only works if there are not enough
		# blocks of text to need the second digit of the counter too.
		# Since that is a lot of blocks we can be a bit lazy.
		keystreamGen += bytes([counter, 0, 0, 0, 0, 0, 0, 0])

		# Careful, we always encrypt the keystream even when decrypting.
		keystream = cipher.encrypt(keystreamGen)

		# The PT is simply the CT XORed with the keystream, and vice versa.
		# Since the PT only depends on the same block of CT plus a predictable
		# keystream, CTR is very suited for parallel decryption of many blocks.
		resultingText += BlockXOR(keystream, block)
		counter += 1

	return resultingText

if __name__ == '__main__':
	c64 = 'L77na/nrFsKvynd6HzOoG7GHTLXsTVu9qvY/2syLXzhPweyyMTJULu/6/kXX0KSvoOLSFQ=='
	ciphertext = base64.b64decode(c64)

	print(DoCTR(ciphertext, b'YELLOW SUBMARINE', 0).decode('ascii'))