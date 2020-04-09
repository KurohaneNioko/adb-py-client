import threading
import enum
import time


class StreamFlow(enum.Enum):
     U = Upload = 0
     D = Download = 1


class TransferStatus(enum.Enum):
    End = 0
    Ready = 1


class TransferRecord:

    def __init__(self, flow, source, dest, status=TransferStatus.Ready):
        self.flow = flow
        self.status = status
        self.source = source
        self.dest = dest

    def set_status(self, status):
        self.status = status


def transfer_wrapper(transfer_function, flow, records, lock):
    while True:
        lock.acquire()
        print(records)
        r = None
        for _r in records:
            if _r.flow==flow and _r.status==TransferStatus.Ready:
                r = _r
        lock.release()
        if r is not None:
            # self.push_function(self.filename, Path(os.path.join(self.remote_dir, self.filename.split('/')[-1])).as_posix())
            transfer_function(r.source, r.dest)
            lock.acquire()
            r.set_status(TransferStatus.End)
            lock.release()
        time.sleep(0.2)


class TransferManager:

    def __init__(self, upload_function=None, download_function=None):
        self.upload_function = upload_function
        self.download_function = download_function
        self.list_lock = threading.Lock()  # for records
        self.records = []
        self.thread_list = [0, 1]

    def add_records(self, *argv):
        self.records.append(TransferRecord(*argv, status=TransferStatus.Ready))

    def threads(self):
        self.thread_list[0] = threading.Thread(
            target=transfer_wrapper, args=(self.upload_function,StreamFlow.Upload,self.records,self.list_lock))
        self.thread_list[1] = threading.Thread(
            target=transfer_wrapper, args=(self.download_function,StreamFlow.D,self.records,self.list_lock))
        self.thread_list[0].setDaemon(True)
        self.thread_list[1].setDaemon(True)
        self.thread_list[0].start()
        self.thread_list[1].start()

    def set_function(self, upload_function, download_function):
        self.upload_function = upload_function
        self.download_function = download_function
