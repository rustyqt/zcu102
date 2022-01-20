#!/usr/bin/python3.8

import sys
sys.path.insert(0, '../client/')

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

from datetime import datetime

from jsonrpc_pyclient.connectors import socketclient
from jsonrpc_client import jsonrpc_client

if __name__ == '__main__':    

    # Create TCP Socket Client
    connector = socketclient.TcpSocketClient("192.168.0.140", 4000)
    
    # Create RPC client
    rpc = jsonrpc_client(connector)

    # Demo RPC calls
    result = rpc.demo_echo("Hello JSON RPC!")
    print("rpc.demo_echo('Hello JSON RPC!') -> " + str(result))

    result = rpc.demo_set_val(2)
    print("rpc.demo_set_val(2) -> " + str(result))

    result = rpc.demo_get_val()
    print("rpc.demo_get_val() -> " + str(result))
    

    # TFTP
    result = rpc.tftp_config(host="192.168.0.142", port=69, blksize=2**16)
    print("rpc.tftp_config(host='192.168.0.142', port=69, blksize=2**16) -> " + str(result))

    result = rpc.tftp_download(remote_filename="system.bit", local_filename="system.bit", dma=False)
    print("rpc.tftp_download() -> " + str(result))

    result = rpc.tftp_upload(remote_filename="test.bit", local_filename="system.bit", dma=False)
    print("rpc.tftp_upload() -> " + str(result))



    # AES GCM

    key = get_random_bytes(32)
    iv  = get_random_bytes(12)

    key0x = hex(int.from_bytes(key, byteorder='big'))
    iv0x  = hex(int.from_bytes(iv, byteorder='big'))

    aad_len = 32
    pt_len  = 2**22

    pt = get_random_bytes(pt_len)
    tx_id = get_random_bytes(20)

    aad = tx_id + iv
    aad_pt = aad + pt

    tag_length        = 16
    aad_pt_length     = aad_len + pt_len
    aad_ct_tag_length = aad_len + pt_len + tag_length

    print("aad_pt_length: " + str(aad_pt_length))
    print("aad_ct_tag_length: " + str(aad_ct_tag_length))

    fp = open("/srv/tftp/aad_pt.raw", "wb")
    fp.write(aad_pt)
    fp.close()

    ###############################
    ### Run Software Encryption ###
    ###############################

    # Start Timer
    time_sw_start = datetime.now()

    # Configure Crypto Kernel
    rpc.aes_gcm_config(key0x=key0x, iv0x=iv0x, aad_len=aad_len, pt_len=pt_len)

    # Start Encryption
    cipher = AES.new(key, AES.MODE_GCM, nonce=iv)
    cipher.update(aad_pt[0:aad_len])
    ct, tag =  cipher.encrypt_and_digest(aad_pt[aad_len:aad_pt_length])

    # Stop Timer
    time_sw_end = datetime.now()
    time_sw = time_sw_end - time_sw_start

    aad_ct_tag_sw = aad + ct + tag


    ####################################
    ### Print AES-GCM Configuration  ###
    ####################################

    print("key[" + str(len(key)) + "] = " + str(key.hex()))
    print("iv[" + str(len(iv)) + "] = " + str(iv.hex()))
    print("tx_id[" + str(len(tx_id)) + "] = " + str(tx_id.hex()))


    ################################
    ### Run Hardware Encryption  ###
    ################################

    rpc.axidma_malloc(buf_id="aad_pt", size=aad_pt_length)
    rpc.axidma_malloc(buf_id="aad_ct_tag", size=aad_ct_tag_length)

    rpc.tftp_download(remote_filename="aad_pt.raw", local_filename="aad_pt", dma=True)

    # Configure Crypto Kernel
    rpc.aes_gcm_config(key0x=key0x, iv0x=iv0x, aad_len=aad_len, pt_len=pt_len)

    # Start Timer
    time_hw_start = datetime.now()

    # Start Encryption
    rpc.aes_gcm_encrypt(ibuf="aad_pt", obuf="aad_ct_tag")

    # Stop Timer
    time_hw_end = datetime.now()
    time_hw = time_hw_end - time_hw_start

    rpc.tftp_upload(remote_filename="aad_ct_tag.raw", local_filename="aad_ct_tag", dma=True)

    rpc.axidma_free(buf_id="aad_pt")
    rpc.axidma_free(buf_id="aad_ct_tag")

    fp = open("/srv/tftp/aad_ct_tag.raw", "rb")
    aad_ct_tag_hw = fp.read()
    fp.close()

    ###############################
    ### Run Software Decryption ###
    ###############################

    tx_id = aad_ct_tag_hw[0:len(aad)-len(iv)]
    iv    = aad_ct_tag_hw[len(aad)-len(iv):len(aad)]
    ct    = aad_ct_tag_hw[len(aad):len(aad)+len(pt)]
    tag   = aad_ct_tag_hw[len(aad)+len(pt):len(aad)+len(pt)+tag_length]

    aad = tx_id + iv

    # Let's assume that the key is somehow available again
    cipher = AES.new(key, AES.MODE_GCM, nonce=iv)

    # Update the cipher with AAD
    cipher.update(aad)

    # Decrypt cipher text and verify data authenticity using the TAG
    decrypted_plaintext = cipher.decrypt_and_verify(ct, tag)



    #################################
    ## Perform Verification Checks ##
    #################################

    print("Time Software Encryption: " + str(time_sw.seconds) + "s " + str(time_sw.microseconds) + "us")
    print("Time Hardware Encryption: " + str(time_hw.seconds) + "s " + str(time_hw.microseconds) + "us")

    assert decrypted_plaintext == pt, "Decrypted message is not plaintext."
    print("\nDecrypt. OK.")

    # Print plaintext in case of short messages
    if len(pt) <= 256:    
        print("decrypted_plaintext = " + str(decrypted_plaintext.hex()))

    # Check for differences in software vs hardware encryption
    print("PT:")
    print(aad_pt[0:16].hex())
    print(aad_pt[16:32].hex())
    print(aad_pt[32:48].hex())
    print(aad_pt[48:64].hex())
    print("HW:")
    print(aad_ct_tag_hw[0:16].hex())
    print(aad_ct_tag_hw[16:32].hex())
    print(aad_ct_tag_hw[32:48].hex())
    print(aad_ct_tag_hw[48:64].hex())
    print("SW:")
    print(aad_ct_tag_sw[0:16].hex())
    print(aad_ct_tag_sw[16:32].hex())
    print(aad_ct_tag_sw[32:48].hex())
    print(aad_ct_tag_sw[48:64].hex())
    assert aad_ct_tag_hw == aad_ct_tag_sw, "Error: Hardware and Software aad_ct_tag differ."

    print("Success: HW and SW encryption is identical!")
