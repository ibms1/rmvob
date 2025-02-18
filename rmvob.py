import streamlit as st
import numpy as np
import os
from io import BytesIO

try:
    import cv2
except ImportError:
    st.error("يرجى تثبيت opencv-python-headless بدلاً من opencv-python")
    st.stop()

def video_to_frames(video_bytes):
    """تحويل الفيديو إلى إطارات من البيانات الثنائية"""
    # تحويل البيانات الثنائية إلى مصفوفة NumPy
    video_np = np.frombuffer(video_bytes, np.uint8)
    
    # قراءة الفيديو من الذاكرة
    cap = cv2.VideoCapture()
    cap.open(cv2.CAP_OPENCV_MJPEG)
    cap.write(video_np)
    
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

def frames_to_video(frames, fps=30):
    """تحويل الإطارات إلى فيديو في الذاكرة"""
    if not frames:
        return None
    
    try:
        height, width = frames[0].shape
        
        # إنشاء buffer في الذاكرة
        output_buffer = BytesIO()
        
        # إنشاء VideoWriter يكتب إلى الذاكرة
        fourcc = cv2.VideoWriter_fourcc(*'avc1')
        out = cv2.VideoWriter('temp.mp4', fourcc, fps, (width, height), isColor=False)
        
        # كتابة الإطارات
        for frame in frames:
            if frame is not None:
                out.write(frame)
        
        out.release()
        
        # قراءة البيانات من الملف المؤقت
        with open('temp.mp4', 'rb') as f:
            video_bytes = f.read()
        
        # حذف الملف المؤقت
        os.remove('temp.mp4')
        
        return video_bytes
    except Exception as e:
        st.error(f"خطأ في تحويل الإطارات إلى فيديو: {str(e)}")
        return None

def main():
    st.title("معالجة الفيديو")
    
    uploaded_file = st.file_uploader("رفع فيديو (أقصى مدة 30 ثانية)", type=["mp4"])
    
    if uploaded_file is not None:
        try:
            # عرض شريط التقدم
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # قراءة بيانات الفيديو المرفوع
            video_bytes = uploaded_file.read()
            
            status_text.text("جاري تحويل الفيديو إلى إطارات...")
            frames = video_to_frames(video_bytes)
            progress_bar.progress(0.3)
            
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
                progress = 0.3 + (i / total_frames * 0.4)
                progress_bar.progress(progress)
            
            # تحويل الإطارات إلى فيديو
            status_text.text("جاري إنشاء الفيديو النهائي...")
            output_video_bytes = frames_to_video(processed_frames)
            
            if output_video_bytes:
                progress_bar.progress(1.0)
                status_text.text("تم معالجة الفيديو بنجاح!")
                
                # عرض الفيديو
                st.video(output_video_bytes)
                
                # زر التحميل
                st.download_button(
                    label="تحميل الفيديو الناتج",
                    data=output_video_bytes,
                    file_name="processed_video.mp4",
                    mime="video/mp4"
                )
            
        except Exception as e:
            st.error(f"حدث خطأ: {str(e)}")

if __name__ == "__main__":
    main()