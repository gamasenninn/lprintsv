from jsonc_parser.parser import JsoncParser
import socket
import sys
import datetime
import time

# --- config value ------
IS_SEND = False
IS_LOG = True
LOG_FILE_PATH = "tpcl_send.log"
RECV_LOG_FILE_PATH = "tpcl_recv.log"
LOG_FILE_ENCODING = "utf-8"
SOCKET_TIME_OUT = 5

# ----- error code -----
ERR_SOCKET_TIME_OUT = -101
ERR_CNNECTION_REFUSED = -102
ERR_RECIEVE_TIME_OUT = -103

# ----ロギング -----
def write_log(log_message, log_file_path):
    current_time = datetime.datetime.now()
    log_entry = f"[{current_time}] {log_message}\n"

    with open(log_file_path, "a",encoding=LOG_FILE_ENCODING) as log_file:
        log_file.write(log_entry)

def write_send_log(log_message):
    write_log(log_message, LOG_FILE_PATH)

def write_recv_log(log_message):
    write_log(log_message, RECV_LOG_FILE_PATH)


# ----コマンド送信 -----
def ssend(com_str, socket, prt_encoding='cp932'):
    # print(com_str)
    b_com = b'\x1b' + com_str.encode(prt_encoding) + b'\x0a\x00'
    # print(b_com)
    if IS_SEND:
        socket.send(b_com)
    if IS_LOG:
        write_send_log(com_str)
        #encoding = 'utf-8'
        #with open(LOG_FILE_PATH, 'a', encoding=encoding) as f:                # ファイルを開く (encoding 注意)
        #    f.write(com_str+"\n")


def ssend_recv(com_str, socket, prt_encoding='cp932'):
    b_com = b'\x1b' + com_str.encode(prt_encoding) + b'\x0a\x00'
    if IS_SEND:
        socket.send(b_com)
        data = socket.recv(1024)
    else:
        data = []

    if IS_LOG:
        encoding = 'utf-8'
        write_send_log(com_str)
        write_recv_log(com_str)
        write_recv_log(data)

        #with open(LOG_FILE_PATH, 'a', encoding=encoding) as f:                # ファイルを開く (encoding 注意)
        #    f.write(com_str+"\n")

    return data

# ----- JSONC定義ファイルの読み込み -------


def read_jsonc_file(jsonc_filepath, encoding='utf-8'):

    with open(jsonc_filepath, 'r', encoding=encoding) as f:                # ファイルを開く (encoding 注意)
        try:
            jsonc_text = f.read()
            return JsoncParser.parse_str(jsonc_text)

        except FileNotFoundError:
            print('ファイルが存在しません。')
            return {}

# ------ check status -----


def check_status(conf):
    # --- printer IP ----
    ip = conf['device']['ip']
    port = int(conf['device']['port'])
    response = {}
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        # connect to printer
        sock.settimeout(SOCKET_TIME_OUT)
        sock.connect((ip, port))
        commands = ["WN", "WS", "WA", "WB", "WV"]
        for command in commands:
            data = ssend_recv(command, sock)
            response[command] = data
    return response


def analize_status(conf):
    result = check_status(conf)
    data = []
    for k, v in result.items():
        if k == "WS": 
            data.append(
                {
                    "command": k,
                    "status": v[2:4].decode(),
                    "status2": v[4:5].decode(),
                    "remainPaper": v[5:9].decode()
                }
            )
        elif k== "WB":
            data.append(
                {
                    "command": k,
                    "status": v[2:4].decode(),
                    "status2": v[4:5].decode(),
                    "remainPaper": v[5:9].decode(),
                    "length": v[9:11].decode(),
                    "buffReamain": v[11:16].decode(),
                    "buffSize": v[16:21].decode(),
                }
            )
        elif k== "WN":
            data.append(
                {
                    "command": k,
                    "usb": v[3:4].decode(),
                    "RTC": v[4:5].decode(),
                    "100base": v[5:6].decode(),
                    "usbFunc": v[6:7].decode(),
                    "cutter": v[7:8].decode(),
                    "sirial": v[8:9].decode(),
                    "centro": v[9:10].decode(),
                    "RS232C": v[10:11].decode(),
                    "wlan": v[11:12].decode(),
                }
            )
        elif k== "WA":
            data.append(
                {
                    "command": k,
                    "mac": v[2:19].decode(),
                }
            )
        elif k== "WV":
            data.append(
                {
                    "command": k,
                    "createDate": v[2:11].decode(),
                    "type": v[11:18].decode(),
                    "version": v[18:23].decode(),
                }
            )
    #print(data)
    return data


# ------ tpcl コマンドを編集し、送信する ------
def send_tcpl_all(conf, sock):

    # --- D: setttingLable ----
    if conf['setLabel']:
        sl = conf['setLabel']
        command = f"D{sl['pitch']},{sl['width']},{sl['height']}"
        ssend(command, sock)
        if sl['isFeed']:
            if sl['isFeed'] == "True":
                censorType = sl['censorType']
                cutter = sl['cutter']
                mode = sl['mode']
                speed = sl['speed']
                ribbon = sl['ribbon']
                command = f"T{censorType}{cutter}{mode}{speed}{ribbon}"
                ssend(command, sock)


    # --- define format ----
    sf = conf['setFormat']
    # buffer clear
    if sf['bufferClear'] == "True":
        command = f"C"
        ssend(command, sock)

    # PCs
    pcs = sf['PC']
    for pc in pcs:
        align = ""
        if 'align' in pc:
            align = f",{pc['align']}"
        if 'autoLineFeed' in pc:
            align = f",P5{pc['autoLineFeed']['width']}{pc['autoLineFeed']['pitch']}{pc['autoLineFeed']['rowMax']}"

        command = f"PC{pc['number']};{pc['x']},{pc['y']},{pc['xR']},{pc['yR']},{pc['fontType']},{pc['fontSpace']},{pc['fontDeco']}{align}"
        ssend(command, sock)

    # XB_QR
    xbqrs = sf['XB_QR']
    for xq in xbqrs:
        command = f"XB{xq['number']};{xq['x']},{xq['y']},T,{xq['errorLevel']},{xq['cellSize']},{xq['mode']},{xq['rotation']},{xq['model']}"
        ssend(command, sock)

    # XB_BAR
    xbs = sf['XB_BAR']
    for xb in xbs:
        command = f"XB{xb['number']};{xb['x']},{xb['y']},{xb['type']},{xb['digit']},{xb['width']},{xb['rotation']},{xb['height']},+0000000000,000,{xb['outNumber']},{xb['zeroSup']}"
        ssend(command, sock)

    # data
    fields = conf['fields'] if 'fields' in conf else []
    data = conf['data'] if 'data' in conf else [{}]

    for d in data:
        for f in fields:
            # print(f)
            default_v = f['default'] if 'default' in f else ""
            bind_v = default_v
            if 'bind' in f:
                bind_key = f['bind']
                bind_v = d[bind_key] if bind_key in d else default_v

            if f['command'] == "RC":
                command = f"RC{f['number']};{bind_v}"
                ssend(command, sock)
            elif f['command'] == "RB":
                command = f"RB{f['number']};{bind_v}"
                ssend(command, sock)
            elif f['command'] == "XS":
                command = f"XS;I,{f['copies']},{f['cutInterval']}{f['censorType']}{f['mode']}{f['speed']}{f['ribbon']}{f['tagRotation']}{f['statusResponse']}"
                ssend(command, sock)
            elif f['command'] == "@12":
                #ssend(command, sock)
                for wf_count in range(3):
                    for i in range(3): #最大3回リトライ
                        command = f"@012;w,T24,V1,U0={bind_v}" #RFIDへの書き込み
                        print(command)
                        ret = ssend_recv(command, sock)
                        if ret[2:5] ==b'635':
                            break
                        time.sleep(1)
                        print(f"エラーリトライ:{i}")
                        write_send_log(f"エラーリトライ:{i}")
                    command = f"WF;I2,U1" #RFIDを読み込む
                    ret = ssend_recv(command, sock)
                    if bind_v.encode() in ret:
                        write_recv_log(f"送信コードが一致しました({bind_v})")
                        break
                    else:
                        print(f"ERROR!.....送信コードが一致しません({bind_v}...リトライ{wf_count})")
                        write_recv_log(f"ERROR!.....送信コードが一致しません({bind_v}...リトライ{wf_count})")
                else:
                    command = f"RC001;----------" 
                    ssend(command, sock)


    # final
    finals = conf['final']
    for fin in finals:
        if 'command' in fin:
            if fin['command'] == "IB":
                command = f"IB"
                ssend(command, sock)


def tpcl_maker(conf):

    # --- printer IP ----
    ip = conf['device']['ip']
    port = int(conf['device']['port'])
    # if 'isPrintOut' in conf['device']:
    global IS_SEND
    IS_SEND = eval(conf['device']['isPrintOut']
                   ) if 'isPrintOut' in conf['device'] else False
    # create socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        # connect to printer
        sock.settimeout(SOCKET_TIME_OUT)
        try:
            sock.connect((ip, port))
        except socket.timeout:  # タイムアウトエラー
            return ERR_SOCKET_TIME_OUT
        except ConnectionRefusedError:  # コネクション拒否エラー
            return ERR_CNNECTION_REFUSED

        send_tcpl_all(conf, sock)

    return True


# ------- initial ---------
if __name__ == '__main__':

    jsonc_filepath = 'print_conf_ip.jsonc'
    encoding = 'utf-8'
    prt_encoding = 'cp932'

    args = sys.argv
    if len(args) == 1:
        pass
    elif len(args) == 2:
        jsonc_filepath = args[1]
    else:
        print("パラメータエラー\n")
        sys.exit()

    conf = read_jsonc_file(jsonc_filepath)
    if conf:
        tpcl_maker(conf)
