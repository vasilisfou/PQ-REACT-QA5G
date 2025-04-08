#!/bin/bash

# Navigate to UERANSIM/build directory
cd /home/vasileios/UERANSIM/build || { echo "Directory UERANSIM/build not found!"; exit 1; }

# Function to handle script termination
cleanup() {
    echo "Stopping all UEs..."
    pkill -f "./nr-ue"
    exit 0
}

# Trap Ctrl+C to execute cleanup function
trap cleanup SIGINT

# Loop from 1 to 50 to start UEs sequentially
for i in {1..50}; do
    config_file="../config/open5gs-ue${i}.yaml"

    # Check if config file exists
    if [[ -f "$config_file" ]]; then
        echo "Starting UE $i: sudo ./nr-ue -c $config_file"
        sudo ./nr-ue -c "$config_file" &  # Run in background
        sleep 10  # Wait before starting the next UE
    else
        echo "Config file $config_file not found, skipping..."
    fi
done

# Keep script running to prevent termination
echo "All UEs started successfully! Press Ctrl+C to stop."
while true; do
    sleep 60  # Keep the script alive indefinitely
done
