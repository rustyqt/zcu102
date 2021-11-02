/******************************************************************************
* Copyright (c) 2021 Xilinx, Inc. All rights reserved.
* SPDX-License-Identifier: MIT
******************************************************************************/
#include <stdio.h>
#include <unistd.h>
#include <sys/socket.h>
#include <linux/if_alg.h>
#include <linux/socket.h>
#include <string.h>
#ifndef SOL_ALG
#define SOL_ALG     279
#endif
#ifndef ALG_SET_KEY_TYPE
#define ALG_SET_KEY_TYPE 6
#endif
 
#define KEY_SIZE        32
#define IV_SIZE         12
#define GCM_TAG_SIZE    16
#define DATA_SIZE 68
#define AES_KUP_KEY     0
#define AES_DEVICE_KEY  1
#define AES_PUF_KEY     2
 
int main(void)
{
  int len = DATA_SIZE + GCM_TAG_SIZE;
  int opfd;
  int tfmfd;
  struct sockaddr_alg sa = {
    .salg_family = AF_ALG,
    .salg_type = "skcipher",
    .salg_name = "xilinx-zynqmp-aes"
  };
  struct msghdr msg = {};
  struct cmsghdr *cmsg;
  char cbuf[CMSG_SPACE(4) + CMSG_SPACE(1024)] = {0};
  char buf[len];
  struct af_alg_iv *iv;
  struct iovec iov;
  int i;
 
 __u8 key[] = { /* Key to be used for the AES encryption and decryption */
     0xF8, 0x78, 0xB8, 0x38, 0xD8, 0x58, 0x98, 0x18, 0xE8, 0x68, 0xA8, 0x28, 0xC8, 0x48,
     0x88, 0x08, 0xF0, 0x70, 0xB0, 0x30, 0xD0, 0x50, 0x90, 0x10, 0xE0, 0x60, 0xA0, 0x20,
     0xC0, 0x40, 0x80, 0x00
};
__u8 key_type[] = {AES_KUP_KEY};
 
 __u8 usr_iv[] = { /* Initialization Vector for the AES encryption and decryption */
     0xD2, 0x45, 0x0E, 0x07, 0xEA, 0x5D, 0xE0, 0x42, 0x6C, 0x0F, 0xA1, 0x33
};
__u8 input[DATA_SIZE + GCM_TAG_SIZE] = { /* The Input Data should be multiples of 4 bytes */
 0xed, 0xaa, 0xe8, 0x26, 0xb6, 0xb4, 0x16, 0xbb, 0xd2, 0x81, 0x58, 0x79, 0x69, 0x20, 0x58, 0xf1, 0x6d, 0xf1, 0x13, 0x3c, 0x72,
 0x22, 0xd5, 0x49, 0x14, 0x1d, 0xcf, 0xef, 0x0f, 0xaf, 0x01, 0xaf, 0xd6, 0x43, 0x3f, 0x9d, 0xc6, 0xbb, 0x7d, 0x32, 0x07, 0xd4,
 0xa5, 0x31, 0xcd, 0xf5, 0xe6, 0xeb, 0xf5, 0x96, 0xbd, 0x4a, 0x0c, 0x3d, 0x43, 0x03, 0x13, 0xce, 0x88, 0xe2, 0xb9, 0xe1, 0x6c,
 0x08, 0x6e, 0x63, 0x3d, 0x24,
  
 0xb5, 0x2b, 0x80, 0xcd, 0x51, 0x17, 0xaf, 0xb4, 0x7b, 0x11, 0x6d, 0x4a, 0x8f, 0x89, 0xcf, 0x75
};
  tfmfd = socket(AF_ALG, SOCK_SEQPACKET, 0);
  bind(tfmfd, (struct sockaddr *)&sa, sizeof(sa));
  /* Set key type to use for AES operation */
  setsockopt(tfmfd, SOL_ALG, ALG_SET_KEY_TYPE, key_type, 0);
  /* Set key for AES operation */
  setsockopt(tfmfd, SOL_ALG, ALG_SET_KEY, key,KEY_SIZE);
  opfd = accept(tfmfd, NULL, 0);
  msg.msg_control = cbuf;
  msg.msg_controllen = sizeof(cbuf);
  cmsg = CMSG_FIRSTHDR(&msg);
  cmsg->cmsg_level = SOL_ALG;
  cmsg->cmsg_type = ALG_SET_OP;
  cmsg->cmsg_len = CMSG_LEN(4);
  /* Set the AES operation type Encrption/Decryption */
  *(__u32 *)CMSG_DATA(cmsg) = ALG_OP_DECRYPT;
  cmsg = CMSG_NXTHDR(&msg, cmsg);
  cmsg->cmsg_level = SOL_ALG;
  cmsg->cmsg_type = ALG_SET_IV;
  cmsg->cmsg_len = CMSG_LEN(1024);
  iv = (void *)CMSG_DATA(cmsg);
  iv->ivlen = IV_SIZE;
  memcpy(iv->iv, usr_iv, IV_SIZE);
  iov.iov_base = input;
  iov.iov_len = len;
  msg.msg_iov = &iov;
  msg.msg_iovlen = 1;
   /* Send AES decryption request to AES driver */
  sendmsg(opfd, &msg, 0);
  /* Read the output buffer for decrypted data */
  read(opfd, buf, len);
  printf("Data Out:\r\n");
  for (i = 0; i < len - GCM_TAG_SIZE; i++) {
    printf("%02x", (unsigned char)buf[i]);
  }
  printf("\n");
 
  close(opfd);
  close(tfmfd);
 
  return 0;
}
