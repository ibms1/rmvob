import streamlit as st
import cv2
import numpy as np
from moviepy.editor import VideoFileClip
import os
from io import BytesIO

# تحقق من طول الفيديو
def check_video_duration(video_path):
    clip = VideoFileClip(video_path)
    duration = clip.duration
    if duration > 30:  # إذا كان الفيديو أطول من 30 ثانية
        return False
    return True

# تحويل الفيديو إلى إطارات
def video_to_frames(video_path):
    cap = cv2.VideoCapture(video_path)
    frames = []
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        frames.append(frame)
    cap.release()
    return frames

# معالجة الإطارات (هنا يمكنك استبدال هذا الجزء بنموذج الإزالة الفعلي)
def process_frame(frame):
    # مثال: تحويل الإطار إلى تدرج رمادي (يمكن استبدال هذا بالمعالجة الفعلية)
    processed_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    return processed_frame

# تحويل الإطارات إلى فيديو
def frames_to_video(frames, output_path, fps=30):
    height, width = frames[0].shape
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height), isColor=False)
    for frame in frames:
        out.write(frame)
    out.release()

# حذف الملفات المؤقتة
def delete_temp_files(*file_paths):
    for file_path in file_paths:
        if os.path.exists(file_path):
            os.remove(file_path)

# واجهة Streamlit
st.title("إزالة الأشياء من الفيديو")
uploaded_file = st.file_uploader("رفع فيديو (أقصى مدة 30 ثانية)", type=["mp4", "avi"])

if uploaded_file is not None:
    # حفظ الفيديو المؤقت
    temp_video_path = "temp_video.mp4"
    with open(temp_video_path, "wb") as f:
        f.write(uploaded_file.read())

    # التحقق من طول الفيديو
    if not check_video_duration(temp_video_path):
        st.error("الفيديو يجب ألا يتجاوز 30 ثانية!")
        delete_temp_files(temp_video_path)  # حذف الفيديو المؤقت
    else:
        st.success("الفيديو مقبول!")

        # تحويل الفيديو إلى إطارات
        frames = video_to_frames(temp_video_path)

        # معالجة الإطارات
        processed_frames = []
        for frame in frames:
            processed_frame = process_frame(frame)
            processed_frames.append(processed_frame)

        # تحويل الإطارات إلى فيديو
        output_video_path = "output_video.mp4"
        frames_to_video(processed_frames, output_video_path)

        # عرض الفيديو الناتج
        st.video(output_video_path)

        # تحميل الفيديو الناتج
        with open(output_video_path, "rb") as f:
            video_bytes = f.read()
        st.download_button(
            label="تحميل الفيديو الناتج",
            data=video_bytes,
            file_name="output_video.mp4",
            mime="video/mp4"
        )

        # حذف الملفات المؤقتة بعد الانتهاء
        delete_temp_files(temp_video_path, output_video_path)