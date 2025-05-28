import os

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa

import Storage.Printer
import Storage.USB
import Security.Crypto
import Security.SSS
import Recovery.RecoveryInterface


def perform_printer_test():
    Storage.Printer.print_file_with_cups("test.txt")
    return True


import zlib

def compress_string(string):
    compressed_data = zlib.compress(bytes(string, 'utf-8'))
    return compressed_data

def decompress_string(data):
    decompressed_data = zlib.decompress(data)
    return decompressed_data.decode('utf-8')


def perform_rsa_test():
    Security.Crypto.Asymmetric.rsa_keygen("test_user")

    example_msg = "hello world"
    print("明文： " + example_msg)

    example_msg_cipher = Security.Crypto.Asymmetric.rsa_encryption(example_msg)
    print("密文：")
    print(example_msg_cipher)

    example_msg_decrypted = Security.Crypto.Asymmetric.rsa_decryption(example_msg_cipher)
    print("解密： " + example_msg_decrypted)
    return True


def shamir_test():
    CWD = os.getcwd()

    KEY_PATH = f'{CWD}/key/key.key'
    print("开始测试")
    aes_key=Recovery.RecoveryInterface.load_aes_key_bytes(KEY_PATH)
    #
    # raw_secret = Recovery.RecoveryInterface.load_secret("Yac_tdP4m0vtADbFNkz36rn5ipYOBaF-Vjx8cZPleVA=")
    #
    # Security.SSS.start_verify(raw_secret)
    # Security.SSS.start_verify(Recovery.RecoveryInterface.load_private_key_bytes(Security.Crypto.PRIVATE_KEY_PATH))
    # shares=Recovery.RecoveryInterface.split_private_key_bytes(
    #     Recovery.RecoveryInterface.load_private_key_bytes(Security.Crypto.PRIVATE_KEY_PATH)
    # )
    #
    # Recovery.RecoveryInterface.reconstruct_secret(
    #     Recovery.RecoveryInterface.load_private_key_bytes(Security.Crypto.PRIVATE_KEY_PATH),
    #     p =420980254453935008154505624481442383441615288088445880985778480721118366200529297662844223875542909878193618383615603475713639264410350373698151412688347944499416741772515069793024550389858263257671132201850967093794635420934592902972252186204604501778542125108222467602496485109294886014106398808705549529824677784747748837884875071005873927577874198472525645674931317724199867860136095632404788376205994229901216339433987568263008103029350627815366016290240983353580057456878680727890686653353313452946297864991916453905705716329261607785145363724798622186541388981272943093285082113942908496023426820951717367975656864826992215938211996700694216838727282673229236432056368929184843775049855990573967476101945368510067410822466881297597557578839817562098827589416924567376251351377861868976455618293542511085042936831850968299002562960903081650307671493771637192147193849547550575629110750111482211453228748747015746147310985184740137153138125287805665634047825666658596731658983057554294073292401585663430738516013985378090545960125427844650842568345827240482672182385730597435782404105447689154663779212990916564753208475671335811065948373309633034156969539012525157147378909560734480194711117232059511791763926112655525863809004431462057178809000875304767958713273626314935133195374134848664124582132104816905400966153302935680745261186147748799608398856044204857793004948099184383671954836450169044196468960997333602201318239870095894207912274670170153174670398937935693964721647597830265393894699525847698522600474844368147283941304989493641086617222208756300091556969039543433430369924600120741145170194638069555002206023954884092116093649788924279,
    #     shares=shares)


def generate_safe_prime(bit_length):
    """生成安全素数（实际为RSA素数生成方法）"""

    return rsa.generate_private_key(

        public_exponent=65537,
        key_size=bit_length,
        backend=default_backend()
    ).private_numbers().p


def usb_test():
    Storage.USB.main()

if __name__ == "__main__":

    Security.SSS.start_verify()
    #   #  p>1524
    # new_p = generate_safe_prime(11000)
    # print(new_p)
    # print(len(str(new_p)))

