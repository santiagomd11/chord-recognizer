import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 
import tensorflow as tf
from tensorflow.keras.preprocessing.image import load_img, img_to_array
from numpy import asarray
import numpy as np
import tempfile
import librosa
import librosa.display
import time
import datetime
import matplotlib.pyplot as plt
from madmom.audio.chroma import DeepChromaProcessor
from madmom.features.chords import DeepChromaChordRecognitionProcessor
import youtube_dl
import warnings
import shutil
from pytube import YouTube
warnings.filterwarnings('ignore')

class RecordesFilesRecognition:
    def __init__(self, model_path_librosa, model_path_dcp, annotations_path):
        self.model_librosa = tf.keras.models.load_model(model_path_librosa)
        self.model_dcp = tf.keras.models.load_model(model_path_dcp)
        self.annotations_path = annotations_path
        self.song_annotatios_path = ''
    
    def downloand_wav(self, youtube_link):
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
                'prefer_ffmpeg': True
            }

            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download([youtube_link])
            
            download_state = True

        except Exception as e:
            print('Try again')
        
        return song_path, download_state
    
    def get_onsetframes(self, song_path):
        dcp = DeepChromaProcessor()
        decode = DeepChromaChordRecognitionProcessor()
        chroma = dcp(song_path)
        frames = list(decode(chroma))
        frames = [list(i) for i in frames]
        frames = [(element[0], element[1]) for element in frames]

        return frames, chroma.T

    def img_proccesing(self, img_path):
        img = load_img(img_path, color_mode='rgb', target_size=(224, 224))
        data = img_to_array(img)
        data = asarray(data)  
        data = data/255.0
        data = data.reshape(1, 224, 224, 3)

        return data

    def classification(self, y, sr, frames):
        chords = ['A#maj', 'A#min', 'Amaj', 'Amin', 'Bmaj', 'Bmin', 'C#maj', 'C#min', 'Cmaj', 'Cmin', 
                    'D#maj', 'D#min', 'Dmaj', 'Dmin', 'Emaj', 'Emin', 'F#maj', 'F#min', 'Fmaj', 'Fmin', 
                    'G#maj', 'G#min', 'Gmaj', 'Gmin', 'N']
        tempdir = tempfile.mkdtemp()
        counter = 0
        classification_list = []


        for element in frames:
            index_start = int(round(element[0] * sr))
            index_end = int(round(element[1] * sr))

            try:
                img_path = os.path.join(tempdir, f'{counter}.png')

                y_frame = y[index_start: index_end]

                tuning = librosa.estimate_tuning(y_frame, sr)
                chroma = librosa.feature.chroma_cens(y_frame, sr=sr, tuning=tuning)
                chroma_mag = librosa.magphase(chroma)[0] ** 4


                fig, ax = plt.subplots()
                img = librosa.display.specshow(chroma_mag, sr=sr, x_axis='time', ax=ax)
                plt.axis('off')
                plt.savefig(img_path, format='png',bbox_inches='tight', pad_inches=0)
                plt.close()

                img = self.img_proccesing(img_path)
                prediction = np.array(self.model_librosa(img)[0])
                index_chord = prediction.argmax()
                chord = chords[index_chord]

                time_start = element[0]
                time_end = element[1]
                
                classification_list.append((time_start, time_end, chord))
                counter += 1
            except IndexError:
                pass
        
        shutil.rmtree(tempdir)
        return classification_list
    
    def save_lab(self, classification_list, annotation_path):
        with open(annotation_path, "w") as f:
            for element in classification_list:
                f.write(f'{element[0]} {element[1]} {element[2]}\n')
    
    def name_parser(self, name):
        invalid_characters = '\ / : * ? " < > |'.split()
        for element in invalid_characters:
            if element in name:
                name = name.replace(element, '')
        return name

    
    def librosa_classify(self, song_path, youtube_link, rm_song_dir):
        song_name = self.name_parser(YouTube(youtube_link).title)
        self.song_annotatios_path = os.path.join(self.annotations_path, f"{song_name}.lab")
        print('---------- Proccesing features------------')
        y, sr = librosa.load(song_path)
        y_harmonic = librosa.effects.harmonic(y)

        frames, _ = self.get_onsetframes(song_path)

        print('------------classification  process------------')

        classification_list = self.classification(y_harmonic, sr, frames)

        print('------------ Saving annotations ---------')

        self.save_lab(classification_list, self.song_annotatios_path)

        if rm_song_dir:
            shutil.rmtree(song_path.replace('song.wav', ''))
    
    def dcp_classify(self, song_path, youtube_link, rm_song_dir):
        sr = 22050

        song_name = self.name_parser(YouTube(youtube_link).title)
        self.song_annotatios_path = os.path.join(self.annotations_path, f"{song_name}.lab")

        chords = ['A#maj', 'A#min', 'Amaj', 'Amin', 'Bmaj', 'Bmin', 'C#maj', 'C#min', 'Cmaj', 'Cmin', 
                    'D#maj', 'D#min', 'Dmaj', 'Dmin', 'Emaj', 'Emin', 'F#maj', 'F#min', 'Fmaj', 'Fmin', 
                    'G#maj', 'G#min', 'Gmaj', 'Gmin', 'N']
        

        tempdir = tempfile.mkdtemp()
        counter = 0
        classification_list = []

        print('---------- Proccesing features------------')

        frames, chroma = self.get_onsetframes(song_path)
        len_y = librosa.get_duration(filename=song_path) * sr
        step = int(round(len_y/chroma.shape[1]))
        c_s = int(round(sr/ step))

        print('------------classification  process------------')
        for element in frames:
            img_path = os.path.join(tempdir, f'{counter}.png')
            start = int(round(element[0] * c_s))
            end = int(round(element[1] * c_s))

            try:
                data = chroma[:, start: end]
                chroma_mag = librosa.magphase(data)[0] ** 4

                fig, ax = plt.subplots()
                img = librosa.display.specshow(chroma_mag, sr=sr, x_axis='time', ax=ax)
                plt.axis('off')
                plt.savefig(img_path, format='png',bbox_inches='tight', pad_inches=0)
                plt.close()

                img = self.img_proccesing(img_path)
                prediction = np.array(self.model_dcp(img)[0])
                index_chord = prediction.argmax()
                chord = chords[index_chord]

                time_start = element[0]
                time_end = element[1]
                
                classification_list.append((time_start, time_end, chord))
                counter += 1
            except IndexError:
                pass

        print('------------ Saving annotations ---------')
        self.save_lab(classification_list, self.song_annotatios_path)
        if rm_song_dir:
            shutil.rmtree(song_path.replace('song.wav', ''))
            
        shutil.rmtree(tempdir)
        
    
    def Main(self):
        end = False
        pp_dict = {1: "librosa", 2: "dcp"}
        
        while not end:
            user_input = input("Enter the youtube link of the song: ").strip()

            if user_input == "end":
                end = True
            else:
                print("----- Loading Audio from youtube ------")
                song_path, state = self.downloand_wav(user_input)
                if state:
                    try:
                        pp_option = int(input("Choose a preprocessing option(1-->librosa, 2-->dcp): ").strip())
                        pp_option = pp_dict[pp_option]
                        if pp_option == "librosa":
                            start_time = time.time()
                            self.librosa_classify(song_path, user_input, True)
                            end_time= time.time()
                            print(f"Required time: {datetime.timedelta(seconds=end_time - start_time)}")

                        elif pp_option == "dcp":
                            start_time = time.time()
                            self.dcp_classify(song_path, user_input, True)
                            end_time= time.time()
                            print(f"Required time: {datetime.timedelta(seconds=end_time - start_time)}")
                    except (KeyError, ValueError):
                        end = True
                        print("Insert a valid preprocess option")
                        shutil.rmtree(song_path.replace('song.wav', ''))
                else:
                    print("Try again")



if __name__ == '__main__':

    model_path_librosa = os.path.join("..", "..", "Models", "model_resnet50_librosa.h5")
    model_path_dcp = os.path.join("..", "..", "Models", "model_resnet50_dcp.h5")
    annotations_path = "Annotations"

    print('------ Loading models ----------')
    rfr = RecordesFilesRecognition(model_path_librosa, model_path_dcp, annotations_path)
    rfr.Main()