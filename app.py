import streamlit as st
from pyftdi.ftdi import Ftdi
from pyftdi.i2c import I2cController, I2cNackError

# Set Streamlit to always run in wide mode
st.set_page_config(layout="wide")

# Add logo image with CSS margin adjustment to move it up
logo_path = r"C:\Users\GSMEOMAN\Pictures\Screenshots\logo.png"
st.markdown(
    f"""
    <style>
    .logo-container {{
        margin-bottom: -20px;
    }}
    </style>
    """,
    unsafe_allow_html=True
)
st.image(logo_path, width=350)

# Create an Ftdi object
ftdi = Ftdi()

# Open the first FT232H device
ftdi.open_bitbang_from_url('ftdi://ftdi:232h/1')

# Create an I2C controller instance and configure it
controller = I2cController()
controller.configure(url='ftdi://ftdi:232h/1')

# Define constants
I2C_ADDRESS_REGISTER_BANK = 0x7C
I2C_ADDRESS_SLAVE_MAIN = 0x2B
I2C_ADDRESS_STOP_MEMORY = 0x07  # Address for STOP MEMORY
STOP_MEMORY_DATA_1 = 0xFF  # Data to send when STOP MEMORY is active
STOP_MEMORY_DATA_0 = 0x00  # Data to send when STOP MEMORY is inactive
BINARY_NUMBERS = [format(i, '08b') for i in range(256)]
HEX_NUMBERS = [format(i, '02X') for i in range(256)]  # Hexadecimal range from 00 to FF
DECIMAL_NUMBERS = [str(i) for i in range(256)]  # Decimal range from 0 to 255

# Define SLAVE MAIN section
def display_slave_main_section():
    st.markdown(
        """
        <div style="background-color:#f0f6ff;padding:5px;border-radius:5px;margin-bottom:20px;">
        <h2 style="color:#0056b3;text-align:center;font-size:16px;font-weight:bold;">SLAVE MAIN</h2>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Display the select box for choosing the data type
    st.markdown('<h2 style="color:black;text-align:left;font-size:14px;">Select Data to Send:</h2>', unsafe_allow_html=True)
    selected_data_type = st.selectbox('', ['Binary', 'Hexadecimal', 'Decimal'], key='data_type')

    selected_data_slave_main = None
    if selected_data_type == 'Binary':
        selected_data_slave_main = st.selectbox('Select Data value:', BINARY_NUMBERS)
    elif selected_data_type == 'Hexadecimal':
        selected_data_slave_main = st.selectbox('Select Data value:', HEX_NUMBERS)
    elif selected_data_type == 'Decimal':
        selected_data_slave_main = st.selectbox('Select Data value:', DECIMAL_NUMBERS)

    # Add a "Send" button for SLAVE MAIN
    if st.button('Send Data'):
        if selected_data_type == 'Binary':
            data_to_send_slave_main = int(selected_data_slave_main, 2)
        elif selected_data_type == 'Hexadecimal':
            data_to_send_slave_main = int(selected_data_slave_main, 16)
        elif selected_data_type == 'Decimal':
            data_to_send_slave_main = int(selected_data_slave_main)
        try:
            controller.write(I2C_ADDRESS_SLAVE_MAIN, [data_to_send_slave_main])
            st.success('Data sent successfully to SLAVE MAIN ✔️')
        except I2cNackError as e:
            st.error(f"Error: {e}")

# Define REGISTER BANK section
def display_register_bank_section():
    st.markdown(
        """
        <div style="background-color:#f0f6ff;padding:5px;border-radius:5px;margin-bottom:20px;">
        <h2 style="color:#0056b3;text-align:center;font-size:16px;font-weight:bold;">REGISTER BANK</h2>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Display select boxes for three registers inside the register bank
    register_values = []
    for register_num in range(1, 4):  # Loop through registers 1, 2, and 3
        st.markdown(f'<h3 style="color:black;text-align:left;font-size:14px;">REGISTER {register_num}</h3>', unsafe_allow_html=True)
        
        # Display select box for selecting binary data for each register
        selected_register_data = st.selectbox(f'Select Data for REGISTER {register_num} (Binary):', BINARY_NUMBERS, key=f'register_bank_binary_{register_num}')
        register_values.append(selected_register_data)

    # Concatenate binary representations of all three registers into a single 24-bit string
    data_to_send_register_bank = ''.join(register_values)
    st.write("24-bit Binary Data:", data_to_send_register_bank)  # Display concatenated binary data

    # Convert the concatenated binary string to bytes
    bytes_to_send_register_bank = bytes([int(data_to_send_register_bank[i:i+8], 2) for i in range(0, len(data_to_send_register_bank), 8)])

    # Add a "Send" button for sending all registers at once
    if st.button('Send All Registers'):
        try:
            # Send the 24-bit data to the register bank
            controller.write(I2C_ADDRESS_REGISTER_BANK, bytes_to_send_register_bank)
            st.success('All registers data sent successfully to REGISTER BANK ✔️')
        except I2cNackError:
            pass  # No need to display an error message if NACK is received


# Define STOP MEMORY section
def display_stop_memory_section():
    st.markdown(
        """
        <div style="background-color:#f0f6ff;padding:5px;border-radius:5px;margin-bottom:20px;">
        <h2 style="color:#0056b3;text-align:center;font-size:16px;font-weight:bold;">STOP MEMORY</h2>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Set default value for STOP MEMORY data
    selected_stop_memory_data = st.selectbox('Select Data for STOP MEMORY:', ['11111111', '00000000'], index=1, key='stop_memory_data')
    stop_memory_data = int(selected_stop_memory_data, 2)

    # Add a "Send" button for sending data to STOP MEMORY
    if st.button('Send Data to STOP MEMORY'):
        try:
            controller.write(I2C_ADDRESS_STOP_MEMORY, [stop_memory_data])
            st.success(f'Data sent successfully to STOP MEMORY at address {hex(I2C_ADDRESS_STOP_MEMORY)} ✔️')
        except I2cNackError as e:
            st.error(f"Error: {e}")

# Display SLAVE MAIN, REGISTER BANK, and STOP MEMORY sections side by side
col1, col2, col3 = st.columns(3)
with col1:
    display_slave_main_section()

with col2:
    display_register_bank_section()

with col3:
    display_stop_memory_section()

# Custom CSS to change the selectbox arrow
st.markdown(
    """
    <style>
    /* Custom CSS to change the selectbox arrow */
    .selectbox .Select-arrow-zone, .selectbox .Select-arrow-zone:hover {
        background-color: transparent !important;
    }
    .selectbox .Select-arrow, .selectbox .Select-arrow:hover {
        border-top-color: #0056b3 !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)
