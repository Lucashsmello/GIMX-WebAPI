from typing import Iterator
import random
import string

from collections import deque
from flask import Response, request
from gevent.queue import Queue
import gevent
from time import sleep
from threading import Thread
import logging

def generate_id(size=6, chars=string.ascii_lowercase + string.digits):
	return ''.join(random.choice(chars) for _ in range(size))


class ServerSentEvent(object):
	"""Class to handle server-sent events."""
	def __init__(self, data, event):
		self.data = data
		self.event = event
		self.event_id = generate_id()
		self.desc_map = {
			self.data: "data",
			self.event: "event",
			self.event_id: "id"
		}

	def encode(self) -> str:
		"""Encodes events as a string."""
		if not self.data:
			return ""
		lines = ["{}: {}".format(name, key)
				 for key, name in self.desc_map.items() if key]

		return "{}\n\n".format("\n".join(lines))


class Channel(object):
	def __init__(self, history_size=32):
		self.subscriptions = []
		self.history = deque(maxlen=history_size)
		self.history.append(ServerSentEvent('start_of_history', None))

	def notify(self, message):
		"""Notify all subscribers with message."""
		for sub in self.subscriptions[:]:
			sub.put(message)

	def event_generator(self, last_id) -> Iterator[ServerSentEvent]:
		"""Yields encoded ServerSentEvents."""
		q = Queue()
		self._add_history(q, last_id)
		self.subscriptions.append(q)
		try:
			while True:
				yield q.get()
		except GeneratorExit:
			self.subscriptions.remove(q)

	def subscribe(self):
		def gen(last_id) -> Iterator[str]:
			for sse in self.event_generator(last_id):
				yield sse.encode()
		return Response(
			gen(request.headers.get('Last-Event-ID')),
			mimetype="text/event-stream")

	def _add_history(self, q, last_id):
		add = False
		for sse in self.history:
			if add:
				q.put(sse)
			if sse.event_id == last_id:
				add = True

	def publish(self, message):
		LOGGER.info("SSE publish:%s" % message)
		sse = ServerSentEvent(str(message), None)
		self.history.append(sse)
		gevent.spawn(self.notify, sse)

	def get_last_id(self) -> str:
		return self.history[-1].event_id

LOGGER = logging.getLogger('gimx_webapi')
def _autoPublishLoop(data_callback,channel,sleep_time_sec):
	global LOGGER
	if(sleep_time_sec>0):
		while(True):
			d=data_callback()
			if(len(d)>0):
				channel.publish(d)
			sleep(sleep_time_sec)
	else:
		while(True):
			d=data_callback()
			if(len(d)>0):
				channel.publish(d)
		

def autoPublish(data_callback,channel,sleep_time_sec=1):
	T = Thread(target=_autoPublishLoop, args=(data_callback,channel,sleep_time_sec))
	T.daemon=True
	T.start()
