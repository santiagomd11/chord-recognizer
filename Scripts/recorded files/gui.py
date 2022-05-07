from tkinter import GROOVE, HORIZONTAL, Button, Label, PhotoImage, Tk, ttk, LEFT
import tkinter as tk
import os
from recorded_files import RecordesFilesRecognition
import librosa
import shutil
import pygame
import time
import tempfile
import youtube_dl

class GUI(RecordesFilesRecognition):
    def __init__(self, model_path_librosa, model_path_dcp, annotations_path):
        super().__init__(model_path_librosa, model_path_dcp, annotations_path)
        self.song_path_classification = ''
        self.song_path_playing = ''
        self.state = False
        self.counter = 1
        self.user_input = None
        self.root = None
        self.status_bar = None
        self.chord_label = None
        self.guitar_label = None
        self.piano_label = None
        self.image_on_canvas_guitar = None
        self.image_on_canvas_piano = None
        self.guitar_image = None
        self.piano_image = None
        self.song_duration = None
        self.converted_song_time = None
        self.my_slider = None
        self.tap_play_counter = 0
        self.is_paused = False
        self.current_time = 0
        self.diff_time = 0
        self.slider_pos_user = 0 
        self.is_classifying= False
        self.slider_pos_on_pause = 0
        self.slider_moving_on_pause = False
        self.chord = ''

    def reset_values(self):
        self.my_slider['state'] = 'disabled'
        self.my_slider.config(value=0)
        self.status_bar.config(text='')
        self.chord_label.config(text='')
        self.chord = ''
        self.state = False
        self.tap_play_counter = 0
        self.diff_time =  0
        self.current_time = 0
        self.is_paused = True
        self.is_classifying = True
        self.slider_pos_user = -1
        pygame.mixer.music.stop()

        self.guitar_image = tk.PhotoImage(file=os.path.join('images','guitar_chords', 'N.png'))
        self.piano_image = tk.PhotoImage(file=os.path.join('images', 'piano_chords', 'N.png'))

        self.guitar_label.itemconfig(self.image_on_canvas_guitar, image=self.guitar_image)
        self.piano_label.itemconfig(self.image_on_canvas_piano, image=self.piano_image)

        self.root.update()

    def callable_hook(self, response=None):
        if response:
            if response["status"] == "downloading":
                self.chord_label.config(text=f'Downloading audio from youtube \n {response["_eta_str"]} remaining')
                self.root.update()
    
    def downloand_wav_2(self, youtube_link):
        tempdir = tempfile.mkdtemp()
        song_path = os.path.join(tempdir, 'song.wav')
        download_state = False
        try:
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': f'{song_path}',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'wav',
                    'preferredquality': '192'
                }],
                'postprocessor_args': [
                    '-ar', '16000'
                ],
                'prefer_ffmpeg': True,
                "progress_hooks": [self.callable_hook]
            }

            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download([youtube_link])
            
            download_state = True

        except Exception as e:
            print('Try again')

        return song_path, download_state

    def download_song(self):
        self.song_path_classification, self.state = self.downloand_wav_2(self.user_input.get().strip())

        #self.chord_label.config(text="Preparing audio for recognition")
        self.song_path_playing = self.song_path_classification.replace("song.wav", "") + "song_p.mp3"
        os.system(f"ffmpeg -i {self.song_path_classification} -f mp3 -ar 22050 {self.song_path_playing}")

    def classify(self, event=None):
        try:
            shutil.rmtree(self.song_path_classification.replace("song.wav", ""))
        except FileNotFoundError:
            pass
        finally:

            self.reset_values()
            self.download_song()
            
            try:
                self.song_duration = librosa.get_duration(filename=self.song_path_classification)
                self.converted_song_time = time.strftime('%H:%M:%S', time.gmtime(self.song_duration))

                self.chord_label.config(text="Extracting chords \n from song")
                self.dcp_classify(self.song_path_classification, self.user_input.get().strip(), False)
                print(self.song_annotatios_path)
                
                self.my_slider.config(to=self.song_duration)
                print(self.song_duration)

                pygame.mixer.music.load(self.song_path_playing)
                self.counter = 1
                self.chord_label.config(text="Ready to Play")
                self.root.mainloop()
                
            except Exception:
                self.chord_label.config(text="Try again")
    
    def display_chord(self, chord):
        self.guitar_image = tk.PhotoImage(file=os.path.join('images', 'guitar_chords', f'{chord}.png'))
        self.piano_image = tk.PhotoImage(file=os.path.join('images','piano_chords', f'{chord}.png'))

        self.guitar_label.itemconfig(self.image_on_canvas_guitar, image=self.guitar_image)
        self.piano_label.itemconfig(self.image_on_canvas_piano, image=self.piano_image)


    def get_chord(self, time):
        with open(self.song_annotatios_path, 'r') as f:
            lines = f.readlines()
            for line in lines:
                line = line.split()
                if float(line[0]) <= time <= float(line[1]):
                    self.chord = line[2]

    def player_time(self):
        self.current_time = pygame.mixer.music.get_pos() / 1000
        self.current_time += self.diff_time
        #print(self.current_time)

        converted_current_time = time.strftime('%H:%M:%S', time.gmtime(self.current_time))

        if self.is_classifying:
            pass

        elif self.slider_pos_user >= 0:
            
            self.get_chord(self.slider_pos_user)
            self.display_chord(self.chord)
            self.chord_label.config(text=self.chord)
            self.diff_time = self.slider_pos_user
            self.slider_pos_user = -1
            self.is_paused = False   

        elif int(self.current_time)  >= int(self.song_duration) and not self.slider_moving_on_pause:
            self.is_paused = True
            self.get_chord(self.song_duration)
            self.display_chord(self.chord)
            self.chord_label.config(text=self.chord)
            self.status_bar.config(text=f'Time Elapsed: {self.converted_song_time} of {self.converted_song_time}')
            self.my_slider.config(value=self.song_duration)

        elif self.slider_pos_user == -1  and not self.is_paused:
            self.get_chord(self.current_time)
            self.display_chord(self.chord)
            self.chord_label.config(text=self.chord)
            self.my_slider.config(value=self.current_time)
            self.status_bar.config(text=f'Time Elapsed: {converted_current_time} of {self.converted_song_time}')
            
        self.status_bar.after(125, self.player_time)
            
    def play_again(self):
        if not self.is_classifying:
            self.my_slider.config(value=0)
            self.diff_time = 0
            self.is_paused = False
            if self.state:
                pygame.mixer.music.load(self.song_path_playing)
                pygame.mixer.music.play(loops=0)
            #print(self.is_paused)

    def play(self):
        self.tap_play_counter += 1
        
        if self.tap_play_counter == 1:
            self.player_time()
            self.is_classifying = False
            self.my_slider['state'] = 'normal'
            self.is_paused = False

            if self.state and self.counter == 1:
                pygame.mixer.music.play(loops=0)
                self.counter += 1

            elif self.state and self.counter > 1:
                pygame.mixer.music.unpause()
        else:
            pass
        
        #print(self.is_paused)
        
    def pause(self):
        self.is_paused = True
        self.tap_play_counter = 0 
        pygame.mixer.music.pause()
        #print(self.is_paused)

    def on_closing(self):
        if tk.messagebox.askokcancel("Quit", "Do you want to quit?"):
            try:
                shutil.rmtree(self.song_path_classification.replace("song.wav", ""))
            except Exception:
                pass
            finally:
                self.chord_label.config(text="Bye!")
                #self.root.update()
                time.sleep(1)
                self.root.destroy()
    
    def slide(self, x=None):
        if self.state and not self.is_classifying:

            self.slider_pos_user = self.my_slider.get()
            pygame.mixer.music.play(loops=0, start=self.slider_pos_user)
            self.is_paused = False
            self.slider_moving_on_pause = False

    def get_pos_on_pause(self):
        if self.is_paused:
            self.slider_pos_on_pause = self.my_slider.get()
            converted_slider_pos = time.strftime('%H:%M:%S', time.gmtime(self.slider_pos_on_pause))
            self.status_bar.config(text=f'Time Elapsed: {converted_slider_pos} of {self.converted_song_time}')
            self.status_bar.after(100, self.get_pos_on_pause)

    def pause_for_slide(self, event=None):
        self.is_paused = True
        self.get_pos_on_pause()
        self.slider_moving_on_pause = True
        pygame.mixer.music.pause()

    def run_gui(self):
        self.root = Tk()
        self.root.title('Chord recognizer')
        self.root.geometry("400x400")
        self.root.resizable(0, 0)

        pygame.mixer.pre_init(frequency=22050)
        pygame.mixer.init()

        self.chord_label = tk.Label(self.root, text='', fg="white", bg="black", font="Helvetica 14 bold italic", width=60, height=2)
        self.chord_label.pack(pady=0)

        chords_frame = tk.Frame(self.root)
        chords_frame.pack()
        
        self.guitar_label = tk.Canvas(chords_frame, bg="black", width=200, height=200, highlightthickness=0)
        self.piano_label = tk.Canvas(chords_frame, bg='black',width=200, height=200, highlightthickness=0)

        self.guitar_label.pack(side=LEFT)
        self.piano_label.pack(side=LEFT)

        self.guitar_image = tk.PhotoImage(file=os.path.join('images', 'guitar_chords', 'N.png'))
        self.piano_image = tk.PhotoImage(file=os.path.join('images', 'piano_chords', 'N.png'))

        self.image_on_canvas_guitar = self.guitar_label.create_image(100, 100, image=self.guitar_image)
        self.image_on_canvas_piano = self.piano_label.create_image(100, 110, image=self.piano_image)
        

        tk.Label(self.root, text="Paste yt link of the song: ", font="Helvetica 12 normal italic").pack()

        play_btn_img = tk.PhotoImage(file=os.path.join('images', 'buttons', 'play.png'))
        pause_btn_img = tk.PhotoImage(file=os.path.join('images', 'buttons', 'pause.png'))
        back_btn_img = tk.PhotoImage(file=os.path.join('images', 'buttons', 'back.png'))

        self.status_bar = Label(self.root, text='', bd=1, font="Helvetica 12 normal italic", relief=GROOVE, anchor="center")
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM, ipady=0)

        self.user_input = tk.Entry(self.root)
        self.user_input.bind('<Return>', self.classify)
        self.user_input.pack()
        
        controls_frame = tk.Frame(self.root)
        controls_frame.pack()


        play_btn = Button(controls_frame, image=play_btn_img, borderwidth=0, height=50, width=50, command=self.play)
        pause_btn = Button(controls_frame, image=pause_btn_img, borderwidth=0, height=50, width=50, command=self.pause)
        back_btn = Button(controls_frame, image=back_btn_img, borderwidth=0, height=50, width=50, command=self.play_again)

        style = ttk.Style()
        style.configure("TScale", background="black", sliderlength=10)
        self.my_slider = ttk.Scale(self.root, from_= 0, to=self.song_duration, orient=HORIZONTAL, value=0, length=160, style="TScale")

        self.my_slider.bind("<ButtonRelease-1>", self.slide)
        self.my_slider.bind("<Button-1>", self.pause_for_slide)

        self.my_slider['state'] = 'disabled'

        self.my_slider.pack(pady=10)


        play_btn.grid(row=0, column=0)
        pause_btn.grid(row=0, column=1)
        back_btn.grid(row=0, column=2)

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

if __name__ == '__main__':
    model_path_librosa = os.path.join("..", "..", "Models", "model_resnet50_librosa.h5")
    model_path_dcp = os.path.join("..", "..", "Models", "model_resnet50_dcp.h5")
    annotations_path = "Annotations"

    Gui = GUI(model_path_librosa, model_path_dcp, annotations_path)

    Gui.run_gui()