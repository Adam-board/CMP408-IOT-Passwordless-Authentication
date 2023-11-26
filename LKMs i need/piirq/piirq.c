#include <linux/module.h>
#include <linux/gpio.h>
#include <linux/interrupt.h>

static unsigned int Button = 15;
static unsigned int Irqnum = 0;
static unsigned int Counter = 0;

static irq_handler_t piirq_irq_handler(unsigned int irq, void *dev_id, struct pt_regs *regs){

   printk(KERN_INFO "button_press");
   Counter++;
   
   return (irq_handler_t) IRQ_HANDLED;
}

int __init piirq_init(void){
	int result = 0;
    pr_info("%s\n", __func__);
    //https://www.kernel.org/doc/Documentation/pinctrl.txt
	printk("piirq: IRQ Test");
    printk(KERN_INFO "piirq: Initializing driver\n");

    if (!gpio_is_valid(Button)){
    printk(KERN_INFO "piirq: invalid GPIO\n");
    return -ENODEV;}
	
	  
	   gpio_request(Button, "Button");
	   gpio_direction_input(Button);
	   gpio_set_debounce(Button, 200);
	   gpio_export(Button, false);


    Irqnum = gpio_to_irq(Button);
    printk(KERN_INFO "piirq: The button is mapped to IRQ: %d\n", Irqnum);

    result = request_irq(Irqnum,
		  (irq_handler_t) piirq_irq_handler, // pointer to the IRQ handler
		  IRQF_TRIGGER_RISING,
		  "piirq_handler",    // cat /proc/interrupts to identify
		  NULL);

    printk("piirq loaded\n");
    return 0;
}
void __exit piirq_exit(void){
   
   free_irq(Irqnum, NULL);
   gpio_unexport(Button);
   gpio_free(Button);
   printk("piirq unloaded\n");
}
module_init(piirq_init);
module_exit(piirq_exit);
MODULE_LICENSE("GPL");
MODULE_AUTHOR("Adam Board");
MODULE_DESCRIPTION("RPi Button Press detection");
MODULE_VERSION("0.5");
