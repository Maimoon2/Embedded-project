Planting Bot – How to Run

This project lets you generate robot movement commands from an image and convert them into ESP32-compatible code.

🚀 Step-by-Step Guide
1️⃣ Run the Controller Script

Start by running:

python planter_controller.py --image demo.jpg

👉 This will open the selected image.

2️⃣ Select Points on Image
Click on the image to select planting points 🌿
Choose all required positions
Once done, press q to continue
3️⃣ Generate Command File

After pressing q, the program will:

Process your selected points
Create a file named:
sample_command.txt

👉 This file contains movement instructions for the robot.

4️⃣ Generate ESP32 Code

Now run:

python esp32_code_generator.py sample_command.txt

👉 This will generate Arduino-compatible code.

5️⃣ Upload to ESP32
Open the generated file in Arduino IDE
Connect your ESP32 board
Upload the code

🎯 Your robot is now ready to execute the planting commands!
