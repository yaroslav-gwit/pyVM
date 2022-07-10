#!/usr/local/bin/bash
COMMAND=$1
VM_NAME=$2

# CHECK IF OLD PID EXISTS AND REMOVE IT IF IT DOES
if [[ -f /var/run/${VM_NAME}.pid ]]; then
    rm /var/run/${VM_NAME}.pid
fi

# GET OWN PID AND WRITE IT INTO VM PID FILE
# echo "$$" > /var/run/${VM_NAME}.pid
echo "${BASHPID}" > /var/run/${VM_NAME}.pid

echo ""
echo "__NEW_START__"
echo "Time and date: $(date)"

echo ""
echo "This bhyve command was executed to start the VM:"
echo $COMMAND

echo ""
$COMMAND & sleep 2 && PARENT_PID=$$ && sleep 1 && CHILD_PID=$! && echo "PARENT_PID=${PARENT_PID}" && echo "CHILD_PID=${CHILD_PID}"

# echo ""
# PARENT_PID=$$
# CHILD_PID=$!
# echo "PARENT_PID=${PARENT_PID}"
# echo "CHILD_PID=${CHILD_PID}"
# echo ""


while [[ $? == 0 ]]
do
    echo ""
    echo "VM has been restarted at: $(date)"
    $COMMAND
    sleep 5
    echo ""
done

sleep 3

if [[ $(ifconfig | grep -c $VM_NAME) > 0 ]]
then
    echo ""
    hoster vm kill $VM_NAME
    echo ""
    
    if [[ -f /var/run/${VM_NAME}.pid ]]; then
        rm /var/run/${VM_NAME}.pid
    fi
fi

echo "The VM exited at $(date)"
echo ""