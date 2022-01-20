# Xilinx ZCU102 Evaluation Board - Xilinx Zynq Ultrascale+

This README will give an overview on how to build the PetaLinux Kernel and AXI DMA drivers using the Petalinux environment.

Furthermore, the README shows how to verifiy the AES GCM crypto core which is instantiated in the PL using python.

## PetaLinux Setup for ZCU102 Evaluation Board

PetaLinux Version: 2021.1

Vivado Version: 2021.1

### Install missing dependencies
    sudo apt install libtinfo5

### Source Petalinux settings.sh
    source /home/lynx/petalinux/settings.sh

### Create petalinux project
    petalinux-create --type project --template zynqMP --name zcu102

### Configure hw platform
    petalinux-config --get-hw-description="/media/lynx/3BB9-E4E0/mpsoc_preset_wrapper.xsa"

In the config menu set DTG Settings -> template to "zcu102-rev1.0"

### Launch the root file system configuration menu
    petalinux-config -c rootfs

### Launch the kernel configuration menu
    petalinux-config -c kernel

### Configure all subsystems
    petalinux-config

### Build PetaLinux
    petalinux-build

### Generate Boot Image
    petalinux-package --boot --format BIN --fsbl images/linux/zynqmp_fsbl.elf --u-boot images/linux/u-boot.elf --pmufw images/linux/pmufw.elf --fpga images/linux/*.bit --force

### Copy to SD card
    cp images/linux/BOOT.BIN images/linux/rootfs.cpio.gz.u-boot images/linux/system.bit images/linux/system.dtb images/linux/Image images/linux/boot.scr /media/lynx/3BB9-E4E0/

### Unmount SD card
    umount /media/lynx/3BB9-E4E0/

### Build, package, copy and umount
    petalinux-build && petalinux-package --boot --format BIN --fsbl images/linux/zynqmp_fsbl.elf --u-boot images/linux/u-boot.elf --pmufw images/linux/pmufw.elf --fpga images/linux/*.bit --force && cp images/linux/BOOT.BIN images/linux/rootfs.cpio.gz.u-boot images/linux/system.bit images/linux/system.dtb images/linux/Image images/linux/boot.scr /media/lynx/3BB9-E4E0/ && umount /media/lynx/3BB9-E4E0/


### Connect to serial console
    sudo picocom -b 115200 /dev/ttyUSB3

### Connect via SSH
    ssh root@192.168.0.140
    alias ls='ls --color=auto'


## DMA Kernel Driver

### Create Kernel Module
    petalinux-create -t modules --name dma-proxy --enable

### Create Application
    petalinux-create -t apps --name dma-proxy-test --enable

### Copy Sources to <path>/files directory and edit .bb files to include header files

### Add dma_proxy node to system-user.dtsi located at
    ./project-spec/meta-user/recipes-bsp/device-tree/files/system-user.dtsi

    dma_proxy {  
      compatible ="xlnx,dma_proxy";
      dmas = <&axi_dma_0 0 &axi_dma_0 1>;
      dma-names = "dma_proxy_tx", "dma_proxy_rx";  
      dma-coherent;
    } ;

## User-space applications

### Load xilinx-axidma driver and run axidma-benchmark application

        root@zcu102:~# modprobe xilinx-axidma
        [   70.199605] axidma: axidma_dma.c: axidma_dma_init: 717: DMA: Found 1 transmit channels and 1 receive channels.
        [   70.209632] axidma: axidma_dma.c: axidma_dma_init: 719: VDMA: Found 0 transmit channels and 0 receive channels.
    
        root@zcu102:~# axidma-benchmark 
        AXI DMA Benchmark Parameters:
        	Transmit Buffer Size: 7.91 MiB
        	Receive Buffer Size: 7.91 MiB
        	Number of DMA Transfers: 1000 transfers
        
        Using transmit channel 0 and receive channel 1.
        Single transfer test successfully completed!
        Beginning performance analysis of the DMA engine.
        
        DMA Timing Statistics:
        	Elapsed Time: 5.23 s
        	Transmit Throughput: 1511.50 MiB/s
        	Receive Throughput: 1511.50 MiB/s
        	Total Throughput: 3023.00 MiB/s



### AES GCM functional verification 
    root@zcu102:~/aes-gcm# ./run_aes_gcm.py
    AXI DMA Init
    Found 1 TX DMA channel(s).
    Found 1 RX DMA channel(s).
    TX DMA channel number(s): [0]
    RX DMA channel number(s): [1]
    aad_pt_length: 4194336
    aad_ct_tag_length: 4194352
    Put aad_pt
    key[32] = 3db3c45df9d58768173e47be81fd1741f4e0439ff3fb167ec16b7e7748eac80a
    iv[12] = 73dff6575077b23433306a39
    tx_id[20] = b0bdaed2948b4f485629e9cf7f1173728bc4c9a9
    tag[16] = ba0e18bdb06bc49835cfe0c2d7605354
    Run AXI DMA two-way transfer
    Time Software Encryption: 0s 347806us  (=    96.48 Mbit/s)
    Time Hardware Encryption: 0s 3245us    (= 10340.47 Mbit/s  -> 10.34 Gbit/s)

    Decrypt. OK.
    PT:
    b0bdaed2948b4f485629e9cf7f117372
    8bc4c9a973dff6575077b23433306a39
    afa98a7a9137ed15b5175d5c17244786
    9171a760082040069b5f34ef5f2d6b64
    HW:
    b0bdaed2948b4f485629e9cf7f117372
    8bc4c9a973dff6575077b23433306a39
    29f5cb5a8c07168a3278b4398a2b28ea
    d98fca5580144873e2c16cd226c162d1
    SW:
    b0bdaed2948b4f485629e9cf7f117372
    8bc4c9a973dff6575077b23433306a39
    29f5cb5a8c07168a3278b4398a2b28ea
    d98fca5580144873e2c16cd226c162d1
    Success: HW and SW encryption is identical!



### ZCU102 GPIO Demo

Check for PL AXI GPIO device
    
    root@zcu102:~# cat /sys/class/gpio/gpiochip500/label 
    a0000000.gpio

GPIO Demo

    gpio-demo -g 500 -o 0x55

Check devices major numbers

    cat /proc/devices | grep dma
    ls -la /dev/xilinx-axidma


## U-boot TFTP

### Configure TFTP Server

    sudo apt install tftpd-hpa

    vi /etc/default/tftpd-hpa

    # /etc/default/tftpd-hpa

    TFTP_USERNAME="tftp"
    TFTP_DIRECTORY="/srv/tftp"
    TFTP_ADDRESS=":69"
    TFTP_OPTIONS="--secure -c"


    netstat -an | more

    systemctl status tftpd-hpa.service


### Configure U-boot

    setenv serverip 192.168.0.142
    setenv ipaddr 192.168.0.144

    tftpboot 0x3000000 Image
    tftpboot 0x2A00000 system.dtb
    tftpboot 0x5000000 rootfs.cpio.gz.u-boot
    booti 0x3000000 0x5000000 0x2A00000


    setenv bootcmd_tftp "tftpboot 0x3000000 Image; tftpboot 0x2A00000 system.dtb; tftpboot 0x5000000 rootfs.cpio.gz.u-boot; booti 0x3000000 0x5000000 0x2A00000"

    setenv boot_targets "tftp mmc0 jtag mmc0 mmc1 qspi0 nand0 usb0 usb1 scsi0 pxe dhcp"

    saveenv

### Post-boot TFTP Server Usage (Busybox tftp)

    tftp -g -r system.bit 192.168.0.142



## Run Demo Software

    cd; rm -rf software/; scp -r lynx@192.168.0.142:/home/lynx/git/zcu102/software .; cd -;
    cd pymods/; chmod a+x install.sh; ./install.sh; cd ../jsonrpc/app; chmod a+x *.py;
    modprobe xilinx-axidma
    ./run_aes_gcm.py


## Utilities
    
### Converting bitstream from .bit to .bin: #

1. Create a bif file with below content

    all:
    {
        [destination_device = pl] <bitstream in .bit> ( Ex: system.bit )
    }

2. Run following command

    bootgen -w -image bitstream.bif -arch zynqmp -process_bitstream bin

Note: The bit/bin file name should be same as the firmware 
name specified in pl.dtsi (design_1_wrapper.bit.bin).

