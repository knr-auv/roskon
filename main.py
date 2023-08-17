import threading
import time
from serial import Serial
import rclpy
import serial
from serial.threaded import Protocol, ReaderThread
from std_msgs.msg import String
import tcm_parser
from okon_enums import MessageFromOkon, MessageToOkon, MessageToOkonRequest, MessageToOkonService
import numpy as np

class OkonReaderThread(ReaderThread):
    def __init__(self, serial_instance, protocol_factory):
        super().__init__(serial_instance, protocol_factory)

    def run(self):
        """Reader loop"""
        if not hasattr(self.serial, 'cancel_read'):
            self.serial.timeout = 1
        self.protocol = self.protocol_factory()
        try:
            self.protocol.connection_made(self)
        except Exception as e:
            self.alive = False
            self.protocol.connection_lost(e)
            self._connection_made.set()
            return
        error = None
        self._connection_made.set()
        while self.alive and self.serial.is_open:
            try:
                msg = tcm_parser.receive_msg(self.serial)
                if msg:
                    self.protocol.data_received(msg)
            except serial.SerialException as e:
                # probably some I/O problem such as disconnected USB serial
                # adapters -> exit
                error = e
                break
            # else:
            #     if data:
            #         # make a separated try-except for called user code
            #         try:
            #             self.protocol.data_received(data)
            #         except Exception as e:
            #             error = e
            #             break
        self.alive = False
        self.protocol.connection_lost(error)
        self.protocol = None,
    

class SerialProtocol(Protocol):
    def __init__(self):
        super().__init__()
        self.transport = None
        self.node = rclpy.create_node("tcm_bridge")
        self.pub = self.node.create_publisher(String, "dummy_topic_pub", 10)
        self.pub2 = self.node.create_publisher(String, "dummy_topic_pub2", 10)
        self.sub = self.node.create_subscription(String, 'topic', self.tcm_sub_callback, 10)
        self.sub2 = self.node.create_subscription(String, 'topic2', self.tcm_sub_callback, 10)
        self.publishers = {} # msg_type -> publisher ?
        self.subscribers = {}
    
    def connection_made(self, transport):
        self.transport = transport
        print("Serial connection established.")

    def data_received(self, msg):
        data, msg_type = msg
        self.parse_data(data, msg_type)
        
    def connection_lost(self, exc):
        self.transport = None
        if isinstance(exc, Exception):
            raise exc
        
    # pub.publish(String(data=str(line)))
    def tcm_sub_callback(self, msg):
        print("callback", msg, threading.get_ident())
        self.pub2.publish(String(data=str('-_-')))
        # msg = tcm_parser.create_msg(3, bytes(msg.data))
        # self.transport.write(msg) # READER THREADSAFE ISSUE !!
    
    def parse_data(self, data: bytearray, msg_type: int) -> None:
        print("parse_data", data, msg_type)
        if msg_type == MessageFromOkon.PID:
            pids = np.frombuffer(data, dtype=np.float32)
            #callbacks.NewPids?.Invoke(pids)
        elif msg_type == MessageFromOkon.SERVICE_CONFIRM:
            confirm_type = data[0]
            msg = ""
            # callbacks.NewConfirm?.Invoke(msg);
            self.pub.publish(String(data=str(confirm_type)))
        elif msg_type == MessageFromOkon.CL_MATRIX:
            cl_matrix = np.frombuffer(data, dtype=np.float32)
            # callbacks.NewCLMatrix?.Invoke(cl_matrix);

def main():
    rclpy.init()
    connection = serial.Serial()
    connection.port = "COM8"            # WARN CHANGE COM NAME!
    connection.baudrate = 115200
    connection.parity = serial.PARITY_NONE
    connection.stopbits = serial.STOPBITS_ONE
    connection.bytesize = serial.EIGHTBITS
    connection.open()
    reader = OkonReaderThread(connection, SerialProtocol)
    with reader as protocol:
        while True:
            time.sleep(1)
            msg = tcm_parser.create_msg(MessageFromOkon.SERVICE_CONFIRM, bytes(b'7'*100))
            reader.write(msg)

if __name__ == "__main__":
    main()