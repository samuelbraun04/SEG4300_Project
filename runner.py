test_mode = True

try:

    from AutomatedYoutube import *
    from datetime import datetime
    from google_images_search import GoogleImagesSearch
    from googleapiclient.errors import HttpError
    from math import ceil
    from moviepy import *
    from moviepy.video.tools.subtitles import SubtitlesClip
    from PIL import ImageFont
    from my_pushover import Pushover
    from PIL import Image
    from pprint import pprint
    from pydub import AudioSegment
    from time import time, sleep
    import googleapiclient.discovery
    import googleapiclient.errors
    import openai
    import os
    import random
    import re
    import shutil
    import traceback

    #main clients
    if test_mode == False:
        channel_name = sys.argv[1]
    else:
        channel_name = "History's Darkest Questions"
        

    # print(len(os.environ.get("OPENAI_KEY")))

    openai.api_key = os.environ.get("OPENAI_KEY")
    # client = openai.Client(os.environ.get("OPENAI_KEY"))
    # images_keys = (open(os.getcwd()+'\\googleimages_key.txt').readlines())
    # image_engine = GoogleImagesSearch(os.environ.get("IMAGES_KEY_API_KEY"), os.environ.get("IMAGES_KEY_SEARCH_ID"))

    
    notification = Pushover('adiwj3152youpxzkvg1h2r7df6tts8')
    notification.user('u5rjk8yhveh6uyeb8uz8u9s8zrrut2')
    current_time = datetime.now()
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

    channel_names = {
        "History's Darkest Questions" : 'casio.cdp.240r@gmail.com',
    }

    #get topic
    directory_path = os.path.join(os.getcwd(), channel_name)  # Path to the directory
    topics = open(os.path.join(directory_path, 'topics.txt'), 'r').readlines()
    topic = topics.pop(0)

    images_directory = os.path.join(os.getcwd(), channel_name, 'Images')
    uncropped_images_directory = os.path.join(os.getcwd(), channel_name, 'Uncropped Images')
    audio_directory = os.path.join(os.getcwd(), channel_name, 'Audio')
    music_directory = os.path.join(os.getcwd(), channel_name, 'Music')

    for filename in os.listdir(images_directory):
        file_path = os.path.join(images_directory, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f'Failed to delete {file_path}. Reason: {e}')


    for filename in os.listdir(uncropped_images_directory):
        file_path = os.path.join(uncropped_images_directory, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f'Failed to delete {file_path}. Reason: {e}')

    for filename in os.listdir(audio_directory):
        file_path = os.path.join(audio_directory, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f'Failed to delete {file_path}. Reason: {e}')

    if test_mode == False:
        # Check if the directory exists
        if not os.path.exists(directory_path):
            print(f"Directory not found: {directory_path}")
        else:
            # Iterate through files in the directory
            for filename in os.listdir(directory_path):
                if filename.endswith('.mp4'):
                    file_path = os.path.join(directory_path, filename)
                    try:
                        os.remove(file_path)
                        print(f"Deleted file: {file_path}")
                    except Exception as e:
                        print(f"Error deleting file {file_path}: {e}")

    #generate script using gpt
    counter = 0
    while(1):
        script_response = openai.chat.completions.create(
            model="gpt-4o-mini-2024-07-18",
            max_tokens=1000,
            messages=[
                {"role": "system", "content": "You will be writing a easy to understand, fact-driven essay about a specific given topic. Structure the essay as follows: an 'Introduction', three to four individual main paragraphs about explicitly different sub-topics of the main topic, and then a 'Conclusion'. The essay should be easy to understand, super detailed (with tons of specific facts scattered throughout the essay), and written as if a human wrote it. Refer to yourself as 'this video' and NOT 'this essay'. IMPORTANT: Format the output EXACTLY as follows:Introduction\n\n*Introduction paragraph*\n\n*Title of first main paragraph*\n\n*First main paragraph*\n\n*Title of second main paragraph*\n\n*Second main paragraph*\n\n...and so on, until the conclusion, which should be titled 'Conclusion' followed by the concluding paragraph. It is essential you format it in this way. Do not include the asterisks (*). There MUST be two carriage returns seperating each title and paragraph and each paragraph and title, not just one. Provide the essay only, with no added commentary, as the output will be fed directly into a program."},
                {"role": "user", "content": "Compose a fact-driven essay on the topic '"+topic+"'."}
            ]
        )

        starting_script = script_response.choices[0].message.content
        print("Starting essay: "+starting_script)

        lines = starting_script.split('\n')
        new_lines = []
        for i, line in enumerate(lines):
            new_lines.append(line)
            if i + 1 < len(lines) and line != '' and lines[i + 1] != '':
                new_lines.append('')
        starting_script = '\n'.join(new_lines)

        topics_and_paragraphs = starting_script.strip().split('\n\n')
        impossible_number_for_topic = 100
        topics_and_paragraphs = process_topics_and_paragraphs(topics_and_paragraphs, impossible_number_for_topic)

        if topics_and_paragraphs[0].strip() != 'Introduction' or any(len(item) < impossible_number_for_topic for index, item in enumerate(topics_and_paragraphs) if index % 2 != 0):
            if counter > 5:
                raise ValueError("Something's wrong with the paragraph generation")
            counter+=1
            continue
        else:
            break

    print("\n\nSplit essay: "+str(topics_and_paragraphs))

    final_script = []
    word_counter = 0
    for index, paragraph in enumerate(topics_and_paragraphs):

        if (index % 2 == 0):
            continue
    
        if topics_and_paragraphs[index-1].strip() != 'Introduction':

            script_response = openai.chat.completions.create(
                model="gpt-4o-mini-2024-07-18",
                max_tokens=200,
                messages=[
                    {"role": "system", "content": "You will be getting a paragraph about a specific topic and must turn it into a single paragraph of around 100 words. Make sure to include a lot of facts and details about the paragraphs specific subject.  You must stay focused to this paragraph's specific topic and not try to explain anything outside of it, because then you might explain something that's already been explained in another paragraph. This is to avoid repetition between the paragraphs. Make sure the paragraph is written as if a human wrote it, not an AI (don't be too wordy and be concise). You will be provided with the specific topic of the paragraph to expand, the topic of the entire essay, and what is so far in the essay so you know what to not repeat. IMPORTANT: Provide the paragraph only, with no added commentary, as the output will be fed directly into a program."},
                    {"role": "user", "content": "Expand the paragraph '"+topics_and_paragraphs[index]+"'. The paragraph is specifically about: '"+topics_and_paragraphs[index-1]+"'. The topic of the overall essay this paragraph is part of is: "+ topic+ ". This paragraph is a part of a larger essay, so to make sure we don't reiterate anything that's been said so far. Here is what is in the essay so far (make sure to not repeat anything that has already been said in the essay so far): "+str(final_script)}
                ]
            )

            print("Expanded paragraph: "+script_response.choices[0].message.content)

            paragraph_word_count = len((script_response.choices[0].message.content).split(' '))
            word_counter += paragraph_word_count

            print("Paragraph Word Counter: "+str(paragraph_word_count))
            print("Total Word Count: "+str(word_counter))

            sleep(15)

            final_script.append(topics_and_paragraphs[index-1])
            final_script.append(script_response.choices[0].message.content)

        else:

            intro_script_response = openai.chat.completions.create(
                model="gpt-4o-mini-2024-07-18",
                max_tokens=200,
                messages=[
                    {"role": "system", "content": "You will be given a paragraph and must shorten it to around 4 sentences (70-80 words). IMPORTANT: Provide the paragraph only, with no added commentary, as the output will be fed directly into a program."},
                    {"role": "user", "content": "Shorten the paragraph: '"+topics_and_paragraphs[index]}
                ]
            )

            final_script.append(topics_and_paragraphs[index-1])
            final_script.append(intro_script_response.choices[0].message.content)

    print("Script: "+ "".join(final_script))

    image_search_terms_response = openai.chat.completions.create(
        model="gpt-4o-mini-2024-07-18",
        messages=[
            {"role": "assistant", "content": "Your task is to identify the subject (not the topic) of a given script in as few words as possible (try for a maximum of 2-3). Examples: Torah and Bible, Chernobyl Disastser or Soviet Russia. IMPORTANT: You should only return the topic, as I will be feeding your output directly into a program."},
            {"role": "user", "content": "Script: "+starting_script+". Based on the revised instructions, identify the key topic of this script."}
        ]
    )

    print("Subjects: "+ image_search_terms_response.choices[0].message.content)

    precise_image_search_terms_response = openai.chat.completions.create(
        model="gpt-4o-mini-2024-07-18",
        messages=[
            {"role": "assistant", "content": "You will be converting a subject into around 6 concise search queries that I will use to find images for a script about that subject. Each search query should be different. IMPORTANT: Your output must be a comma-separated list with no numbering or line breaks. IMPORTANT: Return must be in the following format: 'term 1, term 2, term 3,'."},
            {"role": "user", "content": "Turn this subject into 6 search queries: "+image_search_terms_response.choices[0].message.content+". Each search query has to mention at least one of the words from the subject and contain the words 'black and white' and 'history'."}
        ]
    )

    print("Image terms: "+ precise_image_search_terms_response.choices[0].message.content)

    final_script = process_topics_and_paragraphs(final_script, impossible_number_for_topic)
    print("final_script: "+str(final_script))
    introduction_topic_file = ""
    filenames_to_topics = {}
    voice_model = random.choice(['alloy', 'echo', 'fable', 'onyx', 'shimmer'])

    for index, line_to_tts in enumerate(final_script):

        response = openai.audio.speech.create(
            model="tts-1-hd",
            voice=voice_model,
            input=line_to_tts[0:4096]
        )

        if (index % 2 == 0):
            filename = str(index)+'_'+str(time()).replace('.', '')+'_Topic.flac'
            if index == 0:
                continue
            filenames_to_topics[filename] = line_to_tts
        else:
            filename = str(index)+'_'+str(time()).replace('.', '')+'_Paragraph.flac'

        full_filename = os.path.join(audio_directory, filename)
        try:
            response.with_streaming_response.method(full_filename)
        except Exception:
            print("with_streaming_response.method() failed")
            response.stream_to_file(full_filename)

    flac_files = []
    for file in os.listdir(audio_directory):
        if '.flac' in file:
            flac_files.append(file)
    sorted_flac_files = sorted(flac_files, key=extract_initial_number)
    print('sorted: '+str(sorted_flac_files))

    concatenated_audio = AudioSegment.empty()
    time_counter = 0
    title_time_stamps = []

    for filename in sorted_flac_files:

        new_filename = os.path.join(audio_directory, filename)
        current_audio = AudioSegment.from_file(new_filename)
        
        if '_Topic' in new_filename:
            temp_counter = time_counter
            silence = AudioSegment.silent(duration=3000)
            current_audio = current_audio + silence
            time_counter += len(current_audio)
            title_time_stamps.append([filenames_to_topics[filename], temp_counter, time_counter])
        elif '_Paragraph' in new_filename:
            silence = AudioSegment.silent(duration=1000)
            current_audio = current_audio + silence
            time_counter += len(current_audio)
        else:
            time_counter += len(current_audio)

        concatenated_audio += current_audio

    print(str(title_time_stamps))
    concatenated_audio.export(os.path.join(audio_directory, 'script.flac'), format="flac", bitrate="192k")

    # Transcribe the audio file using Whisper
    with open(os.path.join(audio_directory, 'script.flac'), "rb") as f:
        response = openai.audio.transcriptions.create(model="whisper-1", file=f, response_format='srt')
        open(os.path.join(audio_directory, 'subtitles.srt'), "w", encoding='utf-8').write(response)

    #add empty subtitle line at the end because of moviepy bug THIS IS BROKEN THIS IS BROKEN THIS IS BROKEN THIS IS BROKEN THIS IS BROKEN THIS IS BROKEN THIS IS BROKEN THIS IS BROKEN THIS IS BROKEN THIS IS BROKEN THIS IS BROKEN THIS IS BROKEN THIS IS BROKEN THIS IS BROKEN THIS IS BROKEN THIS IS BROKEN THIS IS BROKEN THIS IS BROKEN THIS IS BROKEN THIS IS BROKEN THIS IS BROKEN THIS IS BROKEN THIS IS BROKEN THIS IS BROKEN THIS IS BROKEN THIS IS BROKEN THIS IS BROKEN 
    with open(os.path.join(audio_directory, 'subtitles.srt'), 'r+', encoding='utf-8') as file:
        lines = file.readlines()

        # Find the last subtitle number and time
        last_number = 0
        last_time = None
        for line in lines[::-1]:
            if line.strip().isdigit():
                last_number = int(line.strip())
            if '-->' in line:
                last_time = line.strip().split(' --> ')[1]
                break

        if last_number and last_time:
            # Calculate new times
            hours, minutes, seconds = map(int, last_time.split(',')[0].split(':'))
            milliseconds = int(last_time.split(',')[1])
            milliseconds += 500  # Increase by 500 milliseconds

            # Adjust for overflow in milliseconds, seconds, and minutes
            if milliseconds >= 1000:
                milliseconds -= 1000
                seconds += 1
            if seconds >= 60:
                seconds -= 60
                minutes += 1
            if minutes >= 60:
                minutes -= 60
                hours += 1

            # Format the new times
            new_start_time = f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"
            new_end_time = f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds + 500:03}"
            
            # Define the new subtitle entry
            new_subtitle_number = last_number + 1
            new_subtitle_entry = f"\n{new_subtitle_number}\n{new_start_time} --> {new_end_time}\nEnd\n\n"

            # Append the new subtitle
            file.write(new_subtitle_entry)

    #scrape the images from the web
    images = precise_image_search_terms_response.choices[0].message.content 
    images = images.split(',')
    for image in images:
        if image.strip() != '':
            search_and_download(image.strip(), os.environ.get("IMAGES_KEY_API_KEY"), os.environ.get("IMAGES_KEY_SEARCH_ID"), download_dir=images_directory)

    #remove all gifs if any exist
    for root, dirs, files in os.walk(images_directory):
            for file in files:
                if file.endswith('.gif'):
                    os.remove(os.path.join(root, file))
                    print(f"Deleted: {os.path.join(root, file)}")
        
    #find and delete all duplicates
    image_hashes = {}
    for filename in os.listdir(images_directory):
        if filename.endswith(('.jpg', '.png', '.jpeg', '.gif', '.bmp')):
            filepath = os.path.join(images_directory, filename)
            try:
                with Image.open(filepath) as img:
                    image_hash = dhash(img)
                    # Compare with existing hashes
                    for existing_hash in image_hashes:
                        if hashes_are_similar(image_hash, existing_hash, tolerance=5):
                            print(f"Similar image found: {filename} is similar to {image_hashes[existing_hash]}")
                            os.remove(filepath)
                    else:
                        image_hashes[image_hash] = filename
            except Exception as e:
                print(f"Error processing {filename}: {e}")
                try:
                    os.remove(filepath)
                except Exception:
                    pass

    clean_directory(images_directory, uncropped_images_directory)
    process_images_in_directory(images_directory)

    #shorten the subtitles
    filename = os.path.join(audio_directory, 'subtitles.srt')
    with open(filename, 'r', encoding='mbcs') as file:
        lines = file.readlines()

    counter = 1
    new_lines = []
    for line in lines:
        # Remove white spaces and carriage returns at the end
        line = line.rstrip()
        
        try:
            if counter == int(line):
                if (counter != 1):
                    new_lines.append('\n')
                counter+=1
        except ValueError:
            pass

        # If it's a time code or sequence number, keep it as is
        if '-->' in line or line.isnumeric():
            new_lines.append(line)
            new_lines.append('\n')  # Add a new line after each processed line
            continue

        if line:  # Add remaining text, if any
            new_lines.append(line)
            new_lines.append('\n')  # Add a new line after each processed line

    # Write the processed lines back into the file
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(''.join(new_lines).rstrip())  # Remove trailing new line 

    filename = topic.strip()
    replacements = {
        ":": "_COLON_",
        "#": "_POUND_",
        "%": "_PERCENT_",
        "&": "_AMPERSAND_",
        "{": "_LEFT_CURLY_BRACKET_",
        "}": "_RIGHT_CURLY_BRACKET_",
        "\\": "_BACK_SLASH_",
        "<": "_LEFT_ANGLE_BRACKET_",
        ">": "_RIGHT_ANGLE_BRACKET_",
        "*": "_ASTERISK_",
        "?": "_QUESTION_MARK_",
        "/": "_FORWARD_SLASH_",
        "$": "_DOLLAR_SIGN_",
        "!": "_EXCLAMATION_POINT_",
        "'": "_SINGLE_QUOTE_",
        "\"": "_DOUBLE_QUOTES_",
        "@": "_AT_SIGN_",
        "+": "_PLUS_SIGN_",
        "`": "_BACKTICK_",
        "|": "_PIPE_",
        "=": "_EQUAL_SIGN_"
    }

    for char, replacement in replacements.items():
        filename = filename.replace(char, replacement)
    output_path = os.path.join(directory_path, filename+'.mp4')

    #overlay music
    flac_file = AudioSegment.from_file(os.path.join(audio_directory, 'script.flac'))
    # music_file = AudioSegment.from_file(os.path.join(music_directory, random.choice(os.listdir(music_directory))))
    # music_file -= 11
    # result = flac_file.overlay(music_file, loop=True)
    # result.export(os.path.join(audio_directory, 'script.flac'), format="flac")

    # Load the audio file
    audio_clip = AudioFileClip(os.path.join(audio_directory, 'script.flac'))
    image_files = sorted([f"{images_directory}/{img}" for img in os.listdir(images_directory) if img.endswith(('.png', '.jpg', '.jpeg'))])

    clips = [ImageClip(m).with_duration(10) for m in image_files]

    while len(clips) * 10 < audio_clip.duration:
        for m in image_files:
            if len(clips) * 10 >= audio_clip.duration:
                break
            clips.append(ImageClip(m).with_duration(10))

    video_duration = audio_clip.duration

    # #if video too short
    # if video_duration < 480:
    #     print("Video not long enough. Adding "+str(ceil(480-video_duration)+2)+' seconds.')
    #     ending = TextClip("Thanks for watching!\n\nDon't forget to like, comment, and subscribe.", size=(1920,1080), font_size=70, bg_color='black', color='white')
    #     ending = ending.with_audio(AudioFileClip(os.path.join(directory_path, 'outro.mp3')))
    #     ending = ending.with_duration(ceil(480-video_duration)+2)
    #     clips.append(ending)

    concat_clip = concatenate_videoclips(clips, method="compose")
    concat_clip = concat_clip.with_audio(audio_clip)
    concat_clip = concat_clip.with_duration(audio_clip.duration)
    concat_clip = concat_clip.with_fps(30)

    # random_font = random.choice(['Georgia-Regular', 'Times-New-Roman', 'Rockwell', 'Sylfaen', 'Arial'])

    generator = lambda text: TextClip(os.path.join(directory_path, "arial.ttf"), text=text, font_size=32, color='white')
    subtitle_clip = SubtitlesClip(os.path.join(audio_directory, 'subtitles.srt'), make_textclip=generator, encoding='utf-8')

    # Add audio and subtitles
    concat_clip.audio = audio_clip
    final_clips = [concat_clip, subtitle_clip.with_position(("center", 1020))]

    # Generate black canvas with text for each timestamp
    for line in title_time_stamps:
        text, start_time_milliseconds, end_time_milliseconds = line
        text_clip = TextClip(os.path.join(directory_path, "arial.ttf"), text=text, font_size=90, color='white', bg_color='black')
        title_duration = ((end_time_milliseconds-start_time_milliseconds)/1000.0) + 0.3
        black_background = ColorClip(size=(1920, 1080), color=(0,0,0), duration=title_duration)
        text_on_black = CompositeVideoClip([black_background, text_clip.with_position('center')]).with_start(start_time_milliseconds/1000.0).with_duration(title_duration)
        final_clips.append(text_on_black)

    # Create the final composite video with all clips
    final = CompositeVideoClip(final_clips)

    # Save the final video
    final = final.with_fps(30)
    final.write_videofile(output_path, codec="libx264")
    final_video = VideoFileClip(output_path)

    if test_mode == False:

        #get video ready
        print("\n\n\n\nXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX\n\n")
        print(topic+'\n\n\n')
        print(((open(os.path.join(directory_path, 'description.txt'), encoding='utf-8').read()).strip()).replace("VIDEO_TITLE", topic).replace("CHANNEL_NAME", channel_name)+'\n')
        print("\n\n\n\nXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX\n\n")

        print("Getting current working directory...")
        current_working_directory = os.getcwd()
        print(f"Current working directory: {current_working_directory}")

        # print("Listing subdirectories excluding .git and __pycache__...")
        # subdirectories = [name for name in os.listdir(current_working_directory) 
        #                   if os.path.isdir(os.path.join(current_working_directory, name)) 
        #                   and (name != '.git') and (name != '__pycache__') and (name != '.vscode')]
        # print("List of subdirectories:", subdirectories)

        # for directory in subdirectories:

        full_directory = directory_path
        directory = channel_name
        print(f"Full path of the directory: {full_directory}")

        print("Loading or authenticating YouTube channel...")
        youtube = load_or_authenticate_channel(directory, r"C:\Users\samlb\Documents\Projects\VideoGenerator-v2\client_secret_643590692955-v30jg61vqaue6odc2km5vipni0aopnej.apps.googleusercontent.com.json", full_directory)

        print("Listing .mp4 files in the directory...")
        mp4_files = [filename for filename in os.listdir(full_directory) if filename.endswith('.mp4')]
        print("List of .mp4 files:", mp4_files)

        if mp4_files:
            mp4_file = mp4_files[0]
            title = os.path.splitext(mp4_file)[0]
            print(f"Getting title... ({title})")
        else:
            print("No .mp4 files found.")
            raise Exception("No mp4 file found")

        print("Applying replacements to the title...")
        replacements = {
            ":": "_COLON_", "#": "_POUND_", "%": "_PERCENT_", "&": "_AMPERSAND_",
            "{": "_LEFT_CURLY_BRACKET_", "}": "_RIGHT_CURLY_BRACKET_", "\\": "_BACK_SLASH_",
            "<": "_LEFT_ANGLE_BRACKET_", ">": "_RIGHT_ANGLE_BRACKET_", "*": "_ASTERISK_",
            "?": "_QUESTION_MARK_", "/": "_FORWARD_SLASH_", "$": "_DOLLAR_SIGN_",
            "!": "_EXCLAMATION_POINT_", "'": "_SINGLE_QUOTE_", "\"": "_DOUBLE_QUOTES_",
            "@": "_AT_SIGN_", "+": "_PLUS_SIGN_", "`": "_BACKTICK_", "|": "_PIPE_", "=": "_EQUAL_SIGN_"
        }
        reversed_replacements = {v: k for k, v in replacements.items()}
        for replacement, char in reversed_replacements.items():
            title = title.replace(replacement, char)
        title = title.title()
        title = title.replace("'S", "'s")
        print(f"Modified video title: {title}")

        body={
            "snippet": {
                "categoryId": "27",
                "description": (((open(os.path.join(full_directory, 'description.txt'), encoding='utf-8').read()).strip()).replace("VIDEO_TITLE", title).replace("CHANNEL_NAME", directory)+'\n'),
                "title": title
            },
            "status": {
                "privacyStatus": "public",
                "selfDeclaredMadeForKids": False,
            }
        }

        print("Preparing request for video upload...")
        request = youtube.videos().insert(
            part=",".join(body.keys()),
            body=body,
            media_body=googleapiclient.http.MediaFileUpload(full_directory + '\\' + mp4_file, chunksize=-1, resumable=True)
        )

        print(f"Video uploaded.")

        thumbnail_file = generate_thumbnail(topic, directory_path)

        if ('Darkest Questions' in channel_name) or ('Alternate' in channel_name):
           thumbnail_file = False

        if thumbnail_file == False:
            status, response = request.next_chunk()
            files = os.listdir(full_directory + '\\Uncropped Images')
            if not files:
                files = os.listdir(full_directory + '\\Images')
            image_files = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
            image_files.sort(key=lambda x: os.path.getctime(os.path.join(full_directory + '\\Uncropped Images', x)))

            for image_file in image_files:
                image = Image.open(os.path.join(uncropped_images_directory, image_file))
                text = pytesseract.image_to_string(image)

                if (text.strip() == "") or (len(os.listdir(uncropped_images_directory)) == 1):
                    thumbnail = os.path.join(full_directory + '\\Uncropped Images', image_file)
                    break
                else:
                    os.remove(os.path.join(uncropped_images_directory, image_file))

            video_id = response.get('id')
            print(f"Processing thumbnail for video ID: {video_id}")

            if os.path.getsize(thumbnail) > 2000000:
                print("Reducing thumbnail size...")
                max_size_bytes = 2 * 1024 * 1024
                img = Image.open(thumbnail)
                quality = 85

                if img.mode == 'RGBA':
                    img = img.convert('RGB')

                original_extension = os.path.splitext(thumbnail)[1]
                temp_path = os.path.join(os.path.dirname(thumbnail), "temporary" + str(time()) + original_extension)
                img.save(temp_path, quality=quality, optimize=True)

                while os.path.getsize(temp_path) > max_size_bytes:
                    quality -= 5
                    img.save(temp_path, quality=quality, optimize=True)

                    if quality <= 10:
                        break

                thumbnail = temp_path
            
            thumbnail = zoom_and_crop_to_aspect_ratio(thumbnail)
            thumbnail = enhance_image_with_vignette(thumbnail)

            print(f"Thumbnail file path: {thumbnail}")

            thumbnail_request = youtube.thumbnails().set(
                videoId=video_id,
                media_body=googleapiclient.http.MediaFileUpload(thumbnail)
            )
            thumbnail_response = thumbnail_request.execute()

            print(f"Thumbnail uploaded. Response: {thumbnail_response}")
        else:            
            try:
                status, response = request.next_chunk()
                if 'id' in response:
                    print(f"Video id '{response['id']}' was successfully uploaded.")

                    video_id = response['id']
                    if os.path.getsize(thumbnail_file) > 2000000:
                        thumbnail_file = reduce_image_size(thumbnail_file, directory_path)

                    convert_image_to_1920x1080(thumbnail_file, thumbnail_file)

                    thumbnail_request = youtube.thumbnails().set(
                        videoId=video_id,
                        media_body=googleapiclient.http.MediaFileUpload(thumbnail_file)
                    )
                    thumbnail_response = thumbnail_request.execute()
                    print(f"Thumbnail set for video id '{video_id}'")
                else:
                    print(f"The upload failed with an unexpected response: {response}")
            except HttpError as e:
                print(f"An HTTP error {e.resp.status} occurred:\n{e.content}")
                response = request.execute()

            print(f"Thumbnail uploaded. File: {thumbnail_file}")

        open(os.path.join(directory_path, 'topics.txt'), 'w').writelines(topics)
        topics = open(os.path.join(os.getcwd(), directory, 'topics.txt'), 'r').readlines()

        send_notification(notification, 'VIDEO UPLOADED: '+channel_name, title+'. Number of topics left: '+str(len(topics)))

        open(r"C:\Users\samlb\Documents\Projects\main_log.txt", 'a+', encoding='utf-8').write(str(datetime.now())+'\n'+str(locals())+'\n\n\n\n')

except Exception as e:
    if test_mode == False:
        open(r"C:\Users\samlb\Documents\Projects\main_log.txt", 'a+', encoding='utf-8').write(str(datetime.now())+'\n'+traceback.format_exc()+'\n\n'+str(locals())+'\n\n\n\n')
        send_notification(notification, 'VIDEO ERROR: '+channel_name, traceback.format_exc())
    else:
        print(traceback.format_exc())