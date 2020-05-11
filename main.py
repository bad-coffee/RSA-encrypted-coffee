from os.path import exists
from os import system
import supports
import rsa

modes = \
'''
[0] 解密
[1] 加密
[2] 更改密码
[3] 重载密钥列表

请输入模式>>>\
'''

def check_self_pem():
    exist_pri = exists('private.pem')
    exist_pub = exists('public.pem')
    if not exist_pri or not exist_pri: return False
    else: return True


def find_pubkeys():
    key_list = supports.find('pem')
    key_list.insert(0, {
        'name': 'Yourself',
        'path': './public.pem'})
    return key_list

if __name__ == '__main__':
    prikey = None
    if not check_self_pem():
        print('你可以手动修复这个问题，或者重新生成密钥')
        if input('密钥不完整，是否重新生成(Y/N)>>>').lower() == 'y':
            prikey, pubkey = supports.genkeys(input('请输入密码，留空为没有密码>>>'))
            with open('private.pem', 'wb') as f:
                f.write(prikey)
            with open('public.pem', 'wb') as f:
                f.write(pubkey)
        else: exit()

    if not prikey:
        while True:
            password = input('请输入密码，若没有请留空>>>')
            status, prikey = supports.load_prikey('private.pem', password)
            if status: break
    pubkeys = find_pubkeys()

    while True:
        mode = input(modes)
        if mode == '0':
            for index in range(len(pubkeys)):
                print('[{index}] {name}'.format(
                index=index, name=pubkeys[index]['name']))
            index = int(input("请选择发件人>>>"))
            with open(pubkeys[index]['path'], "rb") as f:
                third = f.read()

            text = supports.get_text()
            if not len(text.split('\n')) > 2:
                with open('result.rsa', 'r') as f:
                    text = f.read()
            _, code, result = supports.decrypt(prikey, third, text)
            if   code == 0: print(result, '\n√ 签名有效')
            elif code == 1: print(result, '\n× 签名无效')
            elif code == 2: print(result, '\n× 没有签名')
            elif code == -1: print('无效密文')
            elif code == -2: print('无法解密，这可能不是给你的消息')

        elif mode == '1':
            for index in range(len(pubkeys)):
                print('[{index}] {name}'.format(
                index=index, name=pubkeys[index]['name']))
            index = int(input("请选择收信人 >>>"))
            with open(pubkeys[index]['path'], "rb") as f:  # 加载 别人的公钥
                third = f.read()

            message = input('Message >>>')
            need_sig = True if input('是否签名(Y/N)>>>').lower() == 'y' else False

            _, result = supports.encrypt(message, prikey, third, need_sig)
            with open('result.rsa', 'w') as resultfile:
                resultfile.write(result)
            supports.set_text(result.encode('ascii'))
            print('已将密文输出至 result.rsa和剪切板')