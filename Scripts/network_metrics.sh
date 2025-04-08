#!/bin/bash

# InfluxDB Configuration
INFLUXDB_URL="http://localhost:8086/write?db=network_metrics"
INTERFACE="ogstun"

# Thresholds
CPU_THRESHOLD=90
RAM_THRESHOLD=90

# Function to get CPU and RAM usage
get_system_usage() {
    CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | awk '{print $2 + $4}')
    RAM_USAGE=$(free | awk '/Mem/ {printf "%.2f", $3/$2 * 100}')

    # Ensure numeric values are properly formatted
    CPU_USAGE=$(echo "$CPU_USAGE" | tr ',' '.')
    RAM_USAGE=$(echo "$RAM_USAGE" | tr ',' '.')

    echo "CPU Usage: $CPU_USAGE%"
    echo "RAM Usage: $RAM_USAGE%"
}

# Function to measure latency and jitter using iperf3
measure_latency() {
    IPERF_OUTPUT=$(iperf3 -c 192.168.43.128 -u -b 1M -t 10 -J)
    
    # Extract jitter (ensure it's a valid number)
    JITTER=$(echo "$IPERF_OUTPUT" | jq -r '.end.sum.jitter_ms // 0')
    if [[ ! "$JITTER" =~ ^[0-9]+(\.[0-9]+)?$ ]]; then
        JITTER=0
    fi
    
     # Measure round-trip latency to the server (192.168.43.128)
    PING_OUTPUT=$(ping -c 4 192.168.43.128)  # Server IP
    LATENCY=$(echo "$PING_OUTPUT" | tail -n 1 | awk -F'/' '{print $5}')  # Extract average latency (in ms)

    if [[ ! "$LATENCY" =~ ^[0-9]+(\.[0-9]+)?$ ]]; then
        LATENCY=0
    fi
    
    echo "Network Latency: $LATENCY ms"
    echo "Jitter: $JITTER ms"
}

# Function to send data to InfluxDB
send_to_influxdb() {
    CPU_USAGE=$1
    RAM_USAGE=$2
    JITTER=$3
    LATENCY=$4

    # Construct InfluxDB line protocol
    DATA="cpu_usage,interface=$INTERFACE value=$CPU_USAGE"
    curl -i -XPOST "$INFLUXDB_URL" --data-binary "$DATA"

    DATA="ram_usage,interface=$INTERFACE value=$RAM_USAGE"
    curl -i -XPOST "$INFLUXDB_URL" --data-binary "$DATA"

    DATA="jitter,interface=$INTERFACE value=$JITTER"
    curl -i -XPOST "$INFLUXDB_URL" --data-binary "$DATA"
    
     DATA="network_latency,interface=$INTERFACE value=$LATENCY"
    curl -i -XPOST "$INFLUXDB_URL" --data-binary "$DATA"
}

# Run the monitoring functions
get_system_usage
measure_latency
send_to_influxdb "$CPU_USAGE" "$RAM_USAGE" "$JITTER" "$LATENCY"
