/*
 ============================================================================
 Name        : piiotest.c
 Author      : AR
 Version     :
 Copyright   : See Abertay copyright notice
 Description : Test application for piio driver
 ============================================================================
 */

#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>

#include"piio.h"

/*
 * Functions for the ioctl calls
 *
 *
 *Setup piiodev
 pi@raspberrypi:~/Downloads $ sudo insmod piio.ko
 pi@raspberrypi:~/Downloads $ sudo chmod 755 /dev/piiodev
 pi@raspberrypi:~/Downloads $ sudo ./piiotest blink 23 3

 root@raspberrypi:/home/pi# ./piiotest writepin 3 1
 User App
 WRITE:Requested pin:3 - val:1 - desc:desc
 Exit 0
 root@raspberrypi:/home/pi# ./piiotest readpin 3
 User App
 READ:Requested  pin:3 - val:1 - desc:LKMpin
 Exit 0
 root@raspberrypi:/home/pi# ./piiotest blink 23 10
 root@raspberrypi:/home/pi# ./piiotest toggle 3 0 times delay
 root@raspberrypi:/home/pi# ./piiotest toggle 3 0   5   90000
 root@raspberrypi:/home/pi# ./piiotest toggle 23 0 9 900000
 sudo ./piiotest toggle 16 0 25 1000100
 sudo ./piiotest toggle 16 0 15 500000000
 sudo ./piiotest toggle 16 0 15 99000000000
 pi@raspberrypi:~/Downloads $ sudo ./piiotest writepin 16 1 MOTOR
 */

gpio_pin apin;
lkm_data lkmdata;

void write_to_driver(int fd) {
	int ret;
	/* Write to kernel space - see dmesg command*/
	strcpy(lkmdata.data, "This is from user application");
	lkmdata.len = 32;
	lkmdata.type = 'w';
	ret = ioctl(fd, IOCTL_PIIO_WRITE, &lkmdata);

	if (ret < 0) {
		printf("Function failed:%d\n", ret);
		exit(-1);
	}

}

void read_from_drvier(int fd) {
	int ret;

	/*Read from kernel space - see dmesg command*/
	strcpy(lkmdata.data, "");
	ret = ioctl(fd, IOCTL_PIIO_READ, &lkmdata);

	if (ret < 0) {
		printf("Function failed:%d\n", ret);
		exit(-1);
	}

	printf("Message from driver: %s\n", lkmdata.data);
}

int main(int argc, char *argv[]) {
	printf("User App\n");
	int fd, ret;
	char *msg = "Message passed by ioctl\n";

	fd = open("//dev//piiodev", O_RDWR);
	if (fd < 0) {
		printf("Can't open device file: %s\n", DEVICE_NAME);
		exit(-1);
	}

	if (argc > 1) {
		if (!strncmp(argv[1], "readmsg", 8)) {
			read_from_drvier(fd);

		}

		if (!strncmp(argv[1], "writemsg", 9)) {
			write_to_driver(fd);
		}

		if (!strncmp(argv[1], "readpin", 8)) {
			/*  Pass GPIO struct with IO control */
			memset(&apin, 0, sizeof(apin));
			strcpy(apin.desc, "Details");
			apin.pin = strtol(argv[2], NULL, 10);
			/* Pass 'apin' struct to 'fd' with IO control*/
			ret = ioctl(fd, IOCTL_PIIO_GPIO_READ, &apin);
			printf("READ: pin:%i - val:%i - desc:%s\n", apin.pin, apin.value,
					apin.desc);
		}

		if (!strncmp(argv[1], "writepin", 9)) {
			/*  Pass GPIO struct with IO control */
			memset(&apin, 0, sizeof(apin));
			apin.pin = strtol(argv[2], NULL, 10);
			apin.value = strtol(argv[3], NULL, 10);
			ret = ioctl(fd, IOCTL_PIIO_GPIO_WRITE, &apin);
			/* Pass 'apin' struct to 'fd' with IO control*/
			printf("WRITE: pin:%i - val:%i - desc:%s\n", apin.pin, apin.value,
					apin.desc);
		}

		if (!strncmp(argv[1], "blink", 6)) {
			/*  Pass GPIO struct with IO control */
			memset(&apin, 0, sizeof(apin));
			apin.pin = strtol(argv[2], NULL, 10);
			apin.value = strtol(argv[3], NULL, 10);
			int end = apin.value;
			apin.value = 1;
			while (--end > 0) {
				apin.value = !apin.value;
				ret = ioctl(fd, IOCTL_PIIO_GPIO_WRITE, &apin);
				printf("BLINK: pin:%i - val:%i - desc:%s\n", apin.pin,
						apin.value, apin.desc);
				sleep(1);
			}
			apin.value = 0;
			ret = ioctl(fd, IOCTL_PIIO_GPIO_WRITE, &apin);
			printf("BLINK: pin:%i - val:%i - desc:%s\n", apin.pin, apin.value,
					apin.desc);
		}
		if (!strncmp(argv[1], "toggle", 7)) { /*  Toggle the given pin. Better solution should be to use timers or interrupts */
			strcpy(apin.desc, "desc");
			apin.pin = strtol(argv[2], NULL, 10); /* GPIO Number */
			apin.value = strtol(argv[3], NULL, 10); /* Start value pin with High or Low */
			int times = strtol(argv[4], NULL, 10); /* Number of times to blink */
			int delay = strtol(argv[5], NULL, 10); /* Frequency to blink  */
			if (times >= 90000 || times <= 0)
				times = 10;
			if (delay >= 100000 * 10 || delay <= 0)
				delay = 100000;
			for (; (times--);) {
				/*printf("TOGGLE: pin:%i - val:%i - desc:%s\n", apin.pin,
				 apin.value, apin.desc);*/
				ret = ioctl(fd, IOCTL_PIIO_GPIO_WRITE, &apin);
				apin.value = !apin.value;
				usleep(delay);
			}

		}

	}

	close(fd);
	printf("Exit 0\n");

	return 0;
}

