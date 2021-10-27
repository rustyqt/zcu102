#!/bin/sh

# Install missing dependencies
sudo apt install libtinfo5

# PetaLinux Setup for ZCU102 Evaluation Board
# PetaLinux Version: 2021.1

# Source Petalinux settings.sh
source /home/lynx/petalinux/settings.sh

# Create petalinux project
petalinux-create --type project --template zynqMP --name zcu102

# Configure hw platform (Set DTG Settings -> template to "zcu102-rev1.0")
petalinux-config --get-hw-description="/home/lynx/mpsoc_preset_wrapper.xsa"

# Launch the root file system configuration menu
petalinux-config -c rootfs

# Launch the kernel configuration menu
petalinux-config -c kernel

# Build PetaLinux
petalinux-build

# Generate Boot Image
petalinux-package --boot --format BIN --fsbl images/linux/zynqmp_fsbl.elf --u-boot images/linux/u-boot.elf --pmufw images/linux/pmufw.elf --fpga images/linux/*.bit --force

# Copy to SD card
cp images/linux/BOOT.BIN images/linux/rootfs.cpio.gz.u-boot images/linux/system.bit images/linux/system.dtb images/linux/Image images/linux/boot.scr /media/lynx/9016-4EF8/

# Unmount SD card
umount /media/lynx/9016-4EF8/

# Build, package, copy and umount
petalinux-build && petalinux-package --boot --format BIN --fsbl images/linux/zynqmp_fsbl.elf --u-boot images/linux/u-boot.elf --pmufw images/linux/pmufw.elf --fpga images/linux/*.bit --force && cp images/linux/BOOT.BIN images/linux/rootfs.cpio.gz.u-boot images/linux/system.bit images/linux/system.dtb images/linux/Image images/linux/boot.scr /media/lynx/9016-4EF8/ && umount /media/lynx/9016-4EF8/


# Connect to serial console
sudo picocom -b 115200 /dev/ttyUSB3

# Load xilinx-axidma driver and run axidma-benchmark application
root@zcu102:~# modprobe xilinx-axidma
[  298.432173] axidma: axidma_dma.c: axidma_dma_init: 717: DMA: Found 1 transmit channels and 1 receive channels.
[  298.442184] axidma: axidma_dma.c: axidma_dma_init: 719: VDMA: Found 0 transmit channels and 0 receive channels.
root@zcu102:~# axidma-benchmark 
AXI DMA Benchmark Parameters:
	Transmit Buffer Size: 7.91 MiB
	Receive Buffer Size: 7.91 MiB
	Number of DMA Transfers: 1000 transfers

Using transmit channel 0 and receive channel 1.
Single transfer test successfully completed!
Beginning performance analysis of the DMA engine.

DMA Timing Statistics:
	Elapsed Time: 20.79 s
	Transmit Throughput: 380.55 MiB/s
	Receive Throughput: 380.55 MiB/s
	Total Throughput: 761.10 MiB/s
root@zcu102:~#




# Optional bootargs: Set maximum addressable Memory to 2GB and maximum DMA buffer size to 25MB
u-boot-> setenv bootargs "${bootargs} mem=2G cma=25M"
u-boot-> run bootcmd





###########################################
# Converting bitstream from .bit to .bin: #
###########################################

# 1. Create a bif file with below content
all:
{
        [destination_device = pl] <bitstream in .bit> ( Ex: system.bit )

}
# 2. Run following command
bootgen -w -image bitstream.bif -arch zynqmp -process_bitstream bin

# Note: The bit/bin file name should be same as the firmware 
#       name specified in pl.dtsi (design_1_wrapper.bit.bin).



#######################
## DMA Kernel Driver ##
#######################

# Create Kernel Module
petalinux-create -t modules --name dma-proxy --enable

# Create Application
petalinux-create -t apps --name dma-proxy-test --enable

# Copy Sources to <path>/files directory and edit .bb files to include header files

# Add dma_proxy node to system-user.dtsi located at
./project-spec/meta-user/recipes-bsp/device-tree/files/system-user.dtsi

dma_proxy {  
  compatible ="xlnx,dma_proxy";
  dmas = <&axi_dma_0 0 &axi_dma_0 1>;
  dma-names = "dma_proxy_tx", "dma_proxy_rx";  
  dma-coherent;
} ;


######################
## ZCU102 GPIO Demo ##
######################

# Check for PL AXI GPIO device
root@zcu102:~# cat /sys/class/gpio/gpiochip500/label 
a0000000.gpio

# GPIO Demo
gpio-demo -g 500 -o 0x55

################
## ZCU102 DMA ##
################

# Load module
modprobe dma-proxy

# Show loaded modules
lsmod

# Remove module
rmmod dma-proxy

# Check devices major numbers
cat /proc/devices | grep dma
ls -la /dev/dma_proxy_*

# Start DMA proxy test application
dma-proxy-test 1 1





############################
##  FPGA Manager enabled  ##
############################


# FPGA Manager Enabled: Add dma_proxy node to pl-custom.dtsi located at
./project-spec/meta-user/recipes-bsp/device-tree/files/pl-custom.dtsi

# Load bitstream and device tree overlay using FPGA Manager Tool
# Device Tree Blob Overlay gets enabled when FPGA Manager Tool selected.
fpgautil -o /lib/firmware/xilinx/base/base.dtbo -b /lib/firmware/xilinx/base/mpsoc_preset_wrapper.bit.bin

# Added pl-custom.dtsi to ./project-spec/meta-user/recipes-bsp/device-tree/device-tree.bbappend
SRC_URI_append = " file://config file://system-user.dtsi file://pl-custom.dtsi"
