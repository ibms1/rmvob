# app.py
import streamlit as st
import numpy as np
import os
from io import BytesIO
try:
    import cv2
except ImportError:
    st.error("يرجى تثبيت opencv-python-headless بدلاً من opencv-python")
    st.stop()

def video_to_frames(video_path):
    """تحويل الفيديو إلى إطارات"""
    cap = cv2.VideoCapture(video_path)
    frames = []
    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            frames.append(frame)
    finally:
        cap.release()
    return frames

def process_frame(frame):
    """معالجة الإطارات - مثال: تحويل إلى تدرج رمادي"""
    try:
        processed_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        return processed_frame
    except Exception as e:
        st.error(f"خطأ في معالجة الإطار: {str(e)}")
        return None

def frames_to_video(frames, output_path, fps=30):
    """تحويل الإطارات إلى فيديو"""
    if not frames:
        return False
    
    try:
        height, width = frames[0].shape
        fourcc = cv2.VideoWriter_fourcc(*'avc1')  # Using H.264 codec instead of mp4v
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height), isColor=False)
        
        for frame in frames:
            if frame is not None:
                out.write(frame)
        
        out.release()
        return True
    except Exception as e:
        st.error(f"خطأ في تحويل الإطارات إلى فيديو: {str(e)}")
        return False

def delete_temp_files(*file_paths):
    """حذف الملفات المؤقتة"""
    for file_path in file_paths:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            st.warning(f"تعذر حذف الملف المؤقت {file_path}: {str(e)}")

def main():
    st.title("معالجة الفيديو")
    
    uploaded_file = st.file_uploader("رفع فيديو (أقصى مدة 30 ثانية)", type=["mp4"])
    
    if uploaded_file is not None:
        try:
            # عرض شريط التقدم
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # حفظ الفيديو المؤقت
            temp_video_path = "temp_video.mp4"
            with open(temp_video_path, "wb") as f:
                f.write(uploaded_file.read())
            
            status_text.text("جاري تحويل الفيديو إلى إطارات...")
            frames = video_to_frames(temp_video_path)
            progress_bar.progress(33)
            
            if not frames:
                st.error("لم يتم العثور على إطارات في الفيديو")
                return
                
            # معالجة الإطارات
            status_text.text("جاري معالجة الإطارات...")
            processed_frames = []
            total_frames = len(frames)
            
            for i, frame in enumerate(frames):
                processed_frame = process_frame(frame)
                if processed_frame is not None:
                    processed_frames.append(processed_frame)
                progress_bar.progress(33 + (i / total_frames * 33))
            
            # تحويل الإطارات إلى فيديو
            status_text.text("جاري إنشاء الفيديو النهائي...")
            output_video_path = "output_video.mp4"
            
            if frames_to_video(processed_frames, output_video_path):
                progress_bar.progress(100)
                status_text.text("تم معالجة الفيديو بنجاح!")
                
                # عرض الفيديو الناتج
                video_file = open(output_video_path, 'rb')
                video_bytes = video_file.read()
                video_file.close()
                
                st.video(video_bytes)
                
                # زر التحميل
                st.download_button(
                    label="تحميل الفيديو الناتج",
                    data=video_bytes,
                    file_name="output_video.mp4",
                    mime="video/mp4"
                )
            
            # حذف الملفات المؤقتة
            delete_temp_files(temp_video_path, output_video_path)
            
        except Exception as e:
            st.error(f"حدث خطأ: {str(e)}")
            # حذف الملفات المؤقتة في حالة حدوث خطأ
            delete_temp_files(temp_video_path, output_video_path)

if __name__ == "__main__":
    main()