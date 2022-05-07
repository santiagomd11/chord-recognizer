# Chord recognizer v.1.0

## This is a chord recognizer for natural chords (maj, min). The recognition proccess uses a CNN for the chord classification and a HMM for time of onset and offset  detection of each chord. The project have a interactive GUI for youtube songs classification.

---
## **Steps of use (using the terminal)**:

**YOU NEED FIRST PYTHON 3.8.10 (i use this version of python for the project)**

This can be downloaded from the official webpage of python: https://www.python.org/downloads/release/python-3810/


## For linux
You have to make a folder and open it in the terminal (using cd command), the you have to follow the next steps

* clone the respository in your folder with the following line


    ```bash

    git clone https://github.com/santiagomd11/chord-recognizer.git .

    ```

*  Download **[Here](https://drive.google.com/drive/folders/19NX9zFIGRTnaMxOJRTUrqHzicNxPMeMS?usp=sharing)** here the models for the project. Then copy the Models folder and place it in the same folder where you cloned the repo.

* Create a virtual enviroment for install dependecies without modifying your computer packages

    if you don't have vitualenv package installed run this command line:


    ```bash
    pip install virtualenv
    ```
    or 
    ```bash
    pip3 install virtualenv
    ```
    Then in the folder where you cloned the repo run this command line to create the virtualenv:

    ```bash
    virtualenv --python python3.8.10 venv
    ```

* Run the program

    First activate your virtual env

    ```bash
    source venv/bin/activate
    ```
    Then install the requirements of the project:
    ```bash
    python -m pip install -r requirements.txt
    ``` 

    Finally run the program

     ```bash
    cd "Scripts/recorded files"
    ``` 
    ```bash
    chmod +x gui.py recorded_files.py
    ``` 
    ```bash
    python3 gui.py
    ``` 

## For windows

Download ffmpeg for windows from this **[link](https://drive.google.com/drive/folders/1XcaDCQ4I0_MwtHclJ72JXfcqYf2MRr-U?usp=sharing)** and place it in a local disk of your computer (i place it in the C disk) and then follow the next steps for setting ffmpeg for windows:

* With the ffmpeg_windows file placed, go to the Edit the sytem enviroment variables and open it

![](/Images/step1.jpg)

*  Go to advanced system properties and click on eviroment variables

![](/Images/step2.JPG)

* Choose the path option on user vairbales and system variables and then click on edit

![](/Images/step3.jpg)

* Click on new
![](/Images/step4.jpg)

* And finally paste on the new entry the path in where you placed the ffmpeg_widows file
![](/Images/step5.jpg)



You have to make a folder(i made it in the C disk)and open it in the terminal (using cd command), then you have to follow the next steps

* clone the repository in your folder with the following line


    ```bash
    git clone https://github.com/santiagomd11/chord-recognizer.git .
    ```
*  Download **[Here](https://drive.google.com/drive/folders/19NX9zFIGRTnaMxOJRTUrqHzicNxPMeMS?usp=sharing)** here the models for the project. Then copy the Models folder and place it in the same folder where you cloned the repo.

* install microsoft build tools because madmom use Cython, run this command for the installation:
    ```bash
    vs_buildtools.exe --norestart --passive --downloadThenInstall --includeRecommended --add Microsoft.VisualStudio.Workload.NativeDesktop --add Microsoft.VisualStudio.Workload.VCTools --add Microsoft.VisualStudio.Workload.MSBuildTools
    ``` 

* Create a virtual enviroment for install dependecies without modifying your computer packages

    if you don't have vitualenv package installed run this command line:


    ```bash
    pip install virtualenv
    ```
    Then in the folder where you cloned the repo run this command line to create the virtualenv:

    ```bash
    python -m virtualenv --python python3.8.10 venv
    ```

* Run the program

    First activate your virtual env
    ```bash
    venv\Scripts\activate.bat
    ```
    Then install this packages to avoid errors in the installation
    ```bash
    python -m pip install Cython==0.29.14
    ```
    ```bash
    python -m pip install numpy==1.19.5
    ``` 
    Then install the requirements of the project:
    ```bash
    python -m pip install -r requirements.txt
    ``` 

    Finally run the program

     ```bash
    cd "Scripts\recorded files"
    ``` 
    ```bash
    python gui.py
    ``` 
---
## **GUI**:
![Gui chord recognizer v.1.0](/Images/gui_img.png)

* You have to insert a youtube link and then press enter (like the demo)
* You have play, stop, return buttons and a slider to move along the song.

---

## **Demo of chord-recognizer is** **[here](https://youtu.be/3b4xgkvJZRE)**


---
