from escpos.printer import Usb
import usb.core

# Test: Try to import Usb class from python-escpos
try:
    # Check if Usb class is available in escpos.printer
    print("Usb class import successful!")
except Exception as e:
    print(f"Error importing Usb: {e}")

# Test: Try to find a connected USB printer
try:
    # Replace with your printer's Vendor ID and Product ID (example values for Epson)
    usb_vendor_id = 0x04b8  # Example: Epson Vendor ID
    usb_product_id = 0x0202  # Example: Epson Product ID
    usb_interface = 0  # USB interface ID (usually 0)

    # Try initializing the printer
    printer = Usb(usb_vendor_id, usb_product_id, usb_interface)
    
    # Testing the printer (adjust to your printer's commands if necessary)
    printer.set(align='center', width=2, height=2)  # Removed 'text_type' for compatibility
    printer.text("Test Print\n")
    printer.cut()
    print("Printer initialized and printed successfully!")
except Exception as e:
    print(f"Error initializing or printing: {e}")

# Check if pyusb is able to find the printer
try:
    # Test finding the USB device using pyusb (this requires pyusb to be installed)
    dev = usb.core.find(idVendor=usb_vendor_id, idProduct=usb_product_id)
    if dev:
        print(f"Printer found: {dev}")
    else:
        print("Printer not found using pyusb.")
except Exception as e:
    print(f"Error finding printer using pyusb: {e}")
