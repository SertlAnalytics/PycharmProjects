# Gist example of IB wrapper ...
#
# Download API from http://interactivebrokers.github.io/#
#
# Install python API code /IBJts/source/pythonclient $ python3 setup.py install
#
# Note: The test cases, and the documentation refer to a python package called IBApi,
#    but the actual package is called ibapi. Go figure.
#
# Get the latest version of the gateway:
# https://www.interactivebrokers.com/en/?f=%2Fen%2Fcontrol%2Fsystemstandalone-ibGateway.php%3Fos%3Dunix
#    (for unix: windows and mac users please find your own version)
#
# Run the gateway
#
# user: edemo
# pwd: demo123
#
# Now I'll try and replicate the time telling example

from ibapi.wrapper import EWrapper
from ibapi.client import EClient
from ibapi.wrapper import BarData
from sertl_analytics.mydates import MyDate
from ibapi.contract import Contract
from ibapi.account_summary_tags import AccountSummaryTags
from threading import Thread
import queue


class MyIBKRWrapper(EWrapper):
    """
       The wrapper deals with the action coming back from the IB gateway or TWS instance
       We override methods in EWrapper that will get called when this action happens, like currentTime
       """
    def __init__(self):
        self._my_errors_queue = queue.Queue()
        self._time_queue = queue.Queue()
        self._account_summary_queue = queue.Queue()
        self._historical_data_queue = queue.Queue()

    def init_error_queue(self):
        self._my_errors_queue = queue.Queue()

    def error(self, id, error_code, error_str):
        error_msg = "IB error (id={}, code={}): {}".format(id, error_code, error_str)
        if id > 0:
            self._my_errors_queue.put(error_msg)

    def get_error(self):
        error_list = self.__get_queue_entries_as_list__(self._my_errors_queue)
        if len(error_list) == 0:
            print("No errors")
        else:
            print('\n'.join(error_list))

    def init_time_queue(self):
        self._time_queue = queue.Queue()

    def currentTime(self, time_from_server):
        self._time_queue.put(time_from_server)

    def get_time(self):
        return self.__get_queue_entry__(self._time_queue)

    def init_account_summary_queue(self):
        self._account_summary_queue = queue.Queue()

    def accountSummary(self, reqId:int, account:str, tag:str, value:str, currency:str):
        """Returns the data from the TWS Account Window Summary tab in response to reqAccountSummary()."""
        account_info = 'id={}, account={}, tag={}, value={}, ccy={}'.format(reqId, account, tag, value, currency)
        self._account_summary_queue.put(account_info)

    def get_account_summary(self):
        return self.__get_queue_entry__(self._account_summary_queue)

    def init_historical_data_queue(self):
        self._historical_data_queue = queue.Queue()

    def historicalData(self, req_id: int, bar: BarData):
        print('bar={}'.format(bar))

    def get_historical_data(self):
        return self.__get_queue_entry__(self._historical_data_queue)

    @staticmethod
    def __get_queue_entry__(data_queue: queue.Queue, timeout=10):
        try:
            return data_queue.get(timeout=timeout)
        except queue.Empty:
            print("Exceeded maximum wait for wrapper to respond")

    @staticmethod
    def __get_queue_entries_as_list__(input_queue: queue.Queue):
        return_list = []
        while not input_queue.empty():
            return_list.append(input_queue.get())
        return return_list


class MyIBKRClient(EClient):
    """
    The client method We don't override native methods, but instead call them from our own wrappers
    """
    def __init__(self, wrapper: MyIBKRWrapper):  # Set up with a wrapper inside
        EClient.__init__(self, wrapper)

    def get_time_by_client(self):
        self.wrapper.init_time_queue()
        self.reqCurrentTime()
        return self.wrapper.get_time()

    def get_account_summary_by_client(self):
        self.wrapper.init_account_summary_queue()
        self.reqAccountSummary(1001, 'All', "TotalCashValue")
        return self.wrapper.get_account_summary()

    def get_historical_data_by_client(self):
        self.wrapper.init_historical_data_queue()
        date_from = MyDate.adjust_by_days(MyDate.get_datetime_object(), -180)
        date_from_str = MyDate.get_date_time_as_string_from_date_time(date_from, '%Y%m%d %H:%M:%S')
        print(date_from_str)
        qqq = Contract()
        qqq.symbol = 'MMEN'
        qqq.secType = 'STK'
        qqq.exchange = 'CSE'
        qqq.currency = 'CAD'
        self.reqHistoricalData(4001, qqq, date_from_str, "1 M", "1 day", "MIDPOINT", 1, 1, False, [])
        return self.wrapper.get_historical_data()

class MyIBKR(MyIBKRWrapper, MyIBKRClient):
    def __init__(self, ip_address, port_id, client_id):
        MyIBKRWrapper.__init__(self)
        MyIBKRClient.__init__(self, wrapper=self)
        self.connect(ip_address, port_id, client_id)
        thread = Thread(target=self.run)
        thread.start()
        setattr(self, "_thread", thread)
        self.init_error_queue()


if __name__ == '__main__':
    ##
    ## Check that the port is the same as on the Gateway
    ## ipaddress is 127.0.0.1 if one same machine, clientid is arbitrary

    app = MyIBKR("127.0.0.1", 7497, 10)
    print(app.get_time_by_client())
    print(app.get_account_summary_by_client())
    print(app.get_historical_data_by_client())
    print(app.get_error())
    app.disconnect()
