loop(){
    SerialComm.streamData(pressure, temperature, scale)
    SerialComm.update(); // or the packet serial thing
    if(in extraction){
        while(heating){
            // heat but keep streaming data

        }
        motor.moveup();
        // after done
        while(actual extracting){
            update PID stuff
        }
    }
}