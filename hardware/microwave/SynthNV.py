import sys
import threading
import time

import pyvisa

lock = threading.Lock()


class SynthNV:
    _rm = pyvisa.ResourceManager()
    _am_flag = False

    def __init__(self, id: str):
        try:
            self._mw = self._rm.open_resource(id)
        except Exception as e:
            print("open source failed, available instr id are: \n{}".format(self._rm.list_resources()))
            print("Exception occur while open resources: \n{}".format(e))
            sys.exit(-1)

        self._am = 1

    @property
    def frequency(self):
        return self._mw.query("f?")

    @property
    def am(self):
        return self._am

    @am.setter
    def am(self, freq):
        self._am = freq

    def _mw_on(self):
        self._mw.write("o1")

    def _mw_off(self):
        self._mw.write("o0")

    def start_thread(self):
        self._thread = threading.Thread(target=self._start_am)
        self._am_flag = True
        self._thread.start()

    def stop_am(self):
        while input("press enter to stop am: ") != "":
            pass
        self._am_flag = False
        self._mw_off()

    def _start_am(self):
        count = 0
        sleep_time = 1 / 2 / self.am
        while self._am_flag:
            print(count)
            self._mw_on()
            time.sleep(sleep_time)
            self._mw_off()
            time.sleep(sleep_time)
            count += 1

    def stop_thread(self):
        self._am_flag = False
        self._mw_off()

    @property
    def output(self):
        return self._mw.query("o?")

    def stop_am_after(self, duration):
        time.sleep(duration)
        self._am_flag = False
        self._mw_off()

    def set_power(self, value):
        self._mw.write("a{}".format(value))

    def get_power(self):
        print(self._mw.query("a?"))

    def set_frequency(self, freq):
        self._mw.write("f{}".format(freq))

    def get_frequency(self):
        return self._mw.query("f?")


if __name__ == '__main__':
    mw_id = "ASRL3::INSTR"
    synthNV = SynthNV(mw_id)
    synthNV.am = 3.5
    # synthNV.set_power(63)
    # synthNV.set_frequency(2870)
    # print(synthNV.get_frequency())
    # # synthNV.get_power()
    synthNV.start_thread()
    input()
    synthNV.stop_thread()
    # synthNV.stop_am_after(10 / synthNV.am)
