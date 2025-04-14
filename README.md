# lilco_space_shooter
A Game developed on python and demonstrate the NEs emulator in Arduinon

This is a small demonstration of a small interconnection between Arduino and Raspberry Pi. A deonstration of Synergy. 

The ARduino code is written for a Arduino Game Controller Shield that generates a signal everytime a button on it is pressed. The Shield has 7 buttons. 
Similar to a NES it has 'A', 'B', 'C', 'D', 'E', 'F' and 'K'.
Unlike NES controller, instead of Up/down, left/right button, this game controller shield has a Joystick. The Joystick values are sent like a X-Y coordinate axis value. The values are sent every 100 milliseconds. The format of the signal is like this:
"X: X_VALUE", "Y: Y_VALUE" 
The X_VALUE and Y_VALUE is between ß and 1023 yhere the value ditermine as follows. 

For X axis: Neutral Position 490-520
            Right: 521-1023
            Left: 0-489

For Y-Axis:  Neutral Position: 490-520
            Up: 521-1023
            Down: 0-489

And on pressing the buttons, the characters corrsponding to the button is sent 



On the Raspberry Pi side, we use Raspbery Pi 5 and load it with Raspberry Pi OS.
We built the simple space shooter game on VS Code with Python Extension. 

command to install VS Code
sudo apt install code. 

The space shooter game consists of a triangle representing a spaceship on a dark background. 
The spaceship moves in a confided window left right top and down based on the Joystick reading. We put optional keyboard reading to make it simple. 

The small bullets are fired with key "A" from the joystick or SPACE_BAR from keyboard. 
The big bullets are fired using "B" from the Arduino Game Controller Shield or key b on the keyboard. 

The game levels up making the speed faster and desnity of the astroids increases. the default speed of the game is 60
