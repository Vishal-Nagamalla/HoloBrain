HoloBrain: 

Interactive 3D MRI Analysis with a Gesture-Controlled Hologram

Bringing Medical Imaging to Life: Diagnose, Detect, and Visualize

Inspiration
Our friends working in radiology had a common problem—the inefficiency of diagnosing MRI scans by eye. The human brain's complexity and how MRSs are displayed posed a difficult challenge for radiologists, as they had to go through multiple slices of the brain, diagnosing each to sort healthy ones from possible problematic ones. When we met, we realized he had an exciting skill set that could be combined to create a solution, with knowledge of Python and Unity, to help better those in the medical field and leverage the power of AI in making their work more efficient.

What it does
HoloBrain does two things. First, there is a CNN model that can distinguish healthy brains from diseased or problematic ones. From there, you can take the diseased brain, upload it as an asset, and view it through the Dynamic HUD. In doing so, doctors can better visualize, locate, and hopefully treat any brain abnormality before it gets too late much more effectively. This HUD also uses gesture control, meaning that by using your hands in front of a camera, doctors and students can move and zoom around the brain, better showing each part, entirely controlled by the user for what they want.

How we built it
To build the CNN model, we used PyTorch and loaded folders of healthy and unhealthy brains into the model. From there, we trained it on what to look for and achieved a 97% success rate in identifying problematic brains. We incorporated a little of our robotics experience for the Dynamic HUD to build the hardware to host the 3D image. Using Plexiglass sheets, light from a display refracts into the HUD and creates a virtual 3d image that can be viewed inside the HUD. From there, we used Unity and C# to host the assets and set their behavior. To add gesture Control, we used OpenCV and Google's MediaPipe to track hands. From there, we built custom gestures that would be used to control the 3d image.

Challenges we ran into
Connecting our Python script to our Unity script proved our ultimate challenge. Up until then, we had a decent idea of how to create this project, but in this step, we had no idea. As we read through Unity's API and Docs, we learned that we could make a Python Host and set Unity as the receiver to take the inputs from the Python Script and map them onto the bindings we created to move and control the image.

Accomplishments that we're proud of
There's a lot to be proud of in this creation, as it is our first time incorporating Unity and a Python script, our first time creating an image recognition model this complex, and our first time using gesture control to move and manipulate 3D images in real-time.

What we learned
We learned much about machine learning algorithms and how they should be implemented in our project. We also learned so much about the life science aspect of what we made. I had no idea how MRIs worked and what they looked like, so this project opened my eyes to what a lot of doctors face.

What's next for HoloBrain
Next, we would like to add more features to the HUD, including pinging possible spots of interest for doctors to see, making their jobs a little easier in diagnosing. We would also like to add more to make this a seamless user experience, as doctors might not be the most technologically sound. Finally, the most significant update would be to combine the two aspects of this project so that bad brains are automatically sent to the HUD to be seen. And in terms of our database, we would partner with hospitals to increase our dataset so that the model can predict better and in more cases.

Built With
c#
cnn
mediapipe
opencv
python
unity
