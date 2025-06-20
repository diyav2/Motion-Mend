import websocket
import csv
import time
import signal
import sys

# Replace with the actual IP address of your ESP32
ws_url = "ws://192.168.1.106:81"
run_counter = 1  # Counter to create separate files for each run
collecting_data = True  # Data collection state


# Define the function to handle incoming messages
def on_message(ws, message):
    global run_counter, collecting_data

    if message == "Data collection started.":
        print("Data collection started.")
    elif message == "NEWFILE":
        print("Starting a new file.")
        run_counter += 1
    elif message == "STOP":
        print("STOP command received. Ending data collection.")
        collecting_data = False
        ws.close()
    else:
        # Save data to CSV
        file_name = f"run_{run_counter}.csv"
        with open(file_name, 'a', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            if csvfile.tell() == 0:
                csv_writer.writerow(["X_Accel", "Y_Accel", "Z_Accel", "X_Gyro", "Y_Gyro", "Z_Gyro"])
            data = message.split(",")
            csv_writer.writerow(data)
        print(f"Data saved to {file_name}")


# Define the function to handle WebSocket open
def on_open(ws):
    print("WebSocket connected.")
    ws.send("START")  # Send START command to initiate data collection


# Define the function to handle WebSocket close
def on_close(ws, close_status_code, close_msg):
    print("WebSocket closed.")


# Signal handler for graceful shutdown
def signal_handler(sig, frame):
    print("\nSignal received. Closing WebSocket gracefully...")
    ws.close()  # Gracefully close the WebSocket
    sys.exit(0)


# Register the signal handler
signal.signal(signal.SIGINT, signal_handler)  # Handles Ctrl+C
signal.signal(signal.SIGTERM, signal_handler)  # Handles termination signal


# Create and run the WebSocket client
def run():
    global ws
    ws = websocket.WebSocketApp(ws_url,
                                on_message=on_message,
                                on_open=on_open,
                                on_close=on_close)
    ws.run_forever()


if __name__ == "__main__":
    run()
