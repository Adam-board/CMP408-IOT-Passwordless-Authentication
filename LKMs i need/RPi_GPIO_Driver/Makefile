KERNEL := /home/abertay/linux
PWD := $(shell pwd)
obj-m += piio.o

all:
	make ARCH=arm CROSS_COMPILE=$(CROSS) -C $(KERNEL) M=$(PWD) modules
clean:
	make -C $(KERNEL) SUBDIRS=$(PWD) clean

#Enter below make command in console or add it to Eclipse (Project Properties -> C/C++ Build -> Build Command under Builder)
#make KERNEL=/home/cmp408/rpisrc/linux CROSS=/home/cmp408/tools/arm-bcm2708/arm-linux-gnueabihf/bin/arm-linux-gnueabihf-
