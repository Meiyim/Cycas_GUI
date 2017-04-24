import logging
from PyQt4 import QtCore

logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename='cycas_gui.log',
                filemode='w')

def dict_to_str(dict):
    lines = []
    for k, v in dict.iteritems():
        lines.append(str(k) + ':' + str(v))
    return  ', '.join(lines)

class SignalCenter(QtCore.QObject):
    update_progress_bar_signal = QtCore.pyqtSignal(int)
    update_status_signal = QtCore.pyqtSignal(str)
    log_signal = QtCore.pyqtSignal(str)
    report_part_list_signal = QtCore.pyqtSignal(dict)
    clear_parts_signal = QtCore.pyqtSignal()
    render_signal = QtCore.pyqtSignal()
    fit_signal = QtCore.pyqtSignal()
    def __init__(self):
        super(SignalCenter, self).__init__()

# gloabl
signal_center = SignalCenter()



