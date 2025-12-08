#!/bin/bash
# multi-session-training.sh
# Example: Managing multiple GPU sessions for parallel experiments
#
# This script demonstrates how to:
# - Create multiple named sessions with different GPU types
# - Run experiments in parallel across sessions
# - Collect results and cleanup
#
# Requirements:
# - Colab Pro for multiple concurrent sessions (Free tier: 1 session only)
# - lecoder-cgpu installed and authenticated

set -e

echo "=== Multi-Session Training Example ==="
echo ""

# Configuration
SESSIONS=("experiment-1" "experiment-2" "experiment-3")
GPU_TYPES=("T4" "T4" "V100")
EXPERIMENTS=("lr=0.001" "lr=0.01" "lr=0.1")

# Create sessions
echo "Creating sessions..."
for i in "${!SESSIONS[@]}"; do
    session="${SESSIONS[$i]}"
    gpu="${GPU_TYPES[$i]}"
    
    echo "  Creating session: $session with GPU: $gpu"
    lecoder-cgpu connect --gpu "$gpu" --name "$session" || {
        echo "  Warning: Could not create session $session (may have hit tier limit)"
        continue
    }
done

echo ""
echo "Active sessions:"
lecoder-cgpu sessions list

# Run experiments in parallel
echo ""
echo "Starting experiments..."

run_experiment() {
    local session=$1
    local experiment=$2
    local output_file="results_${session}.json"
    
    echo "  Running experiment in $session: $experiment"
    
    # Switch to session and run
    lecoder-cgpu sessions switch "$session"
    
    # Run training with JSON output
    lecoder-cgpu run --kernel --json "
import torch
import time
import json

# Simulate training with different hyperparameters
${experiment}
epochs = 5
losses = []

for epoch in range(epochs):
    loss = 1.0 / (epoch + 1) * (1 / lr)  # Fake loss that decreases
    losses.append(loss)
    time.sleep(0.1)  # Simulate training time

result = {
    'session': '$session',
    'experiment': '$experiment',
    'final_loss': losses[-1],
    'gpu': torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'
}
print(json.dumps(result))
" > "$output_file" 2>/dev/null
    
    echo "    Results saved to $output_file"
}

# Run experiments (sequential for demo, could be parallelized)
for i in "${!SESSIONS[@]}"; do
    session="${SESSIONS[$i]}"
    experiment="${EXPERIMENTS[$i]}"
    run_experiment "$session" "$experiment" &
done

# Wait for all experiments
wait
echo ""
echo "All experiments completed!"

# Aggregate results
echo ""
echo "=== Results ==="
for session in "${SESSIONS[@]}"; do
    if [ -f "results_${session}.json" ]; then
        echo "Session $session:"
        cat "results_${session}.json" | jq '.'
    fi
done

# Cleanup
echo ""
echo "Cleaning up sessions..."
for session in "${SESSIONS[@]}"; do
    lecoder-cgpu sessions close "$session" 2>/dev/null || true
done

echo ""
echo "Done!"
