KERNEL := /home/cmp408/rpisrc/linux
PWD := $(shell pwd)
obj-m += piirq.o

all:
	make ARCH=arm CROSS_COMPILE=$(CROSS) -C $(KERNEL) M=$(PWD) modules
clean:
	make -C $(KERNEL) M=$(PWD) clean
##On the receiving end 
#nc -l -p 1234 > lkm01.file
##On the sending end 
#nc -w 3 192.168.0.7 1234 < lkm01.ko

##Insert module
# sudo insmod lkm01.ko
##remove module
# sudo rmmod lkm01.ko
#Enter below make command in console or add it to Eclipse (Project Properties -> C/C++ Build -> Build Command under Builder)
#make KERNEL=/home/cmp408/rpisrc/linux CROSS=/home/cmp408/tools/arm-bcm2708/arm-linux-gnueabihf/bin/arm-linux-gnueabihf-
