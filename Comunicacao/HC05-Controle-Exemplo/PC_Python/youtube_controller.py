import pyautogui
import serial
import argparse
import time
import logging

from urllib.request import urlopen
import requests
import json
import threading
import time



def is_live_stream():
    url = "https://api.twitch.tv/kraken/streams/veguinho98?client_id=uf2ck23nxqeaohmgy79zamz0p65o1e"

    streamer_html = requests.get(url)
    streamer = json.loads(streamer_html.content)
    time.sleep(1)
    print(streamer["stream"])
    return streamer["stream"] is not None

class MyControllerMap:
	def __init__(self):
		self.button = {'A':['ctrl','s'],'B': 'M'} # Fast forward (10 seg) pro Youtube
	  # Fast forward (10 seg) pro Youtube
class SerialControllerInterface:
	# Protocolo   sssddsMMMMMssMM
	# byte 1 -> Botão 1 (estado - Apertado 1 ou não 0)
	# byte 2 -> EOP - End of Packet -> valor reservado 'X'

	def __init__(self, port, baudrate):
		self.ser = serial.Serial(port, baudrate=baudrate)
		self.mapping = MyControllerMap()
		self.incoming = '0'
		pyautogui.PAUSE = 0  ## remove delay
	
	def update(self):
		## Sync protocolMMMMMMMMMMMMMMMMMMMMMMMMMMM
		while self.incoming != b'X':
			self.incoming = self.ser.read()
			logging.debug("Received INCOMING: {}".format(self.incoming))

			self.ser.write("dwadaddawdwa")
		data = self.ser.read()
		logging.debug("Received DATA: {}".format(data))

		if data == b'1':
			data = self.ser.read()
			if data == b'L':
				logging.info("KEYDOWN A")
				pyautogui.hotkey('ctrl','s')
			if data == b'M':
				logging.info("KEYDOWN B")
				pyautogui.keyDown(self.mapping.button['B'])

		elif data == b'0':
			logging.info("KEYUP A")
			pyautogui.keyUp('ctrl','s')
			logging.info("KEYDOWN B")
			pyautogui.keyUp(self.mapping.button['B'])



		self.incoming = self.ser.read()


class DummyControllerInterface:
	def __init__(self):
		self.mapping = MyControllerMap()

	def update(self):
		pyautogui.keyDown(self.mapping.button['A'])
		time.sleep(0.1)
		pyautogui.keyUp(self.mapping.button['A'])
		logging.info("[Dummy] Pressed A button")
		time.sleep(1)


if __name__ == '__main__':
	interfaces = ['dummy', 'serial']
	argparse = argparse.ArgumentParser()
	argparse.add_argument('serial_port', type=str)
	argparse.add_argument('-b', '--baudrate', type=int, default=9600)
	argparse.add_argument('-c', '--controller_interface', type=str, default='serial', choices=interfaces)
	argparse.add_argument('-d', '--debug', default=False, action='store_true')
	args = argparse.parse_args()

	if args.debug:
		logging.basicConfig(level=logging.DEBUG)

	print("Connection to {} using {} interface ({})".format(args.serial_port, args.controller_interface, args.baudrate))
	if args.controller_interface == 'dummy':
		controller = DummyControllerInterface()
	else:
		controller = SerialControllerInterface(port=args.serial_port, baudrate=args.baudrate)

	while True:
		threading.Thread(target=is_live_stream).start()
		controller.update()
