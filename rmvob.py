import streamlit as st
import numpy as np
import os
from io import BytesIO

try:
    import cv2
except ImportError:
    st.error("يرجى تثبيت opencv-python-headless بدلاً من opencv-python")
    st.stop()

def read_video_frames(video_bytes):
    """تحويل الفيديو إلى إطارات من البيانات الثنائية"""
    # كتابة البيانات إلى ملف مؤقت
    temp_path = "temp_input.mp4"
    try:
        with open(temp_path, "wb") as f:
            f.write(video_bytes)
        
        # قراءة الفيديو
        cap = cv2.VideoCapture(temp_path)
        frames = []
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            frames.append(frame)
        
        cap.release()
        return frames
    
    except Exception as e:
        st.error(f"خطأ في قراءة الفيديو: {str(e)}")
        return []
    
    finally:
        # تنظيف الملف المؤقت
        if os.path.exists(temp_path):
            os.remove(temp_path)

def process_frame(frame):
    """معالجة الإطارات - مثال: تحويل إلى تدرج رمادي"""
    try:
        processed_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        return processed_frame
    except Exception as e:
        st.error(f"خطأ في معالجة الإطار: {str(e)}")
        return None

def create_video_from_frames(frames, fps=30):
    """تحويل الإطارات إلى فيديو"""
    if not frames:
        return None
    
    temp_output = "temp_output.mp4"
    try:
        height, width = frames[0].shape
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(temp_output, fourcc, fps, (width, height), isColor=False)
        
        for frame in frames:
            if frame is not None:
                out.write(frame)
        
        out.release()
        
        # قراءة الفيديو كبيانات ثنائية
        with open(temp_output, 'rb') as f:
            video_bytes = f.read()
        
        return video_bytes
    
    except Exception as e:
        st.error(f"خطأ في إنشاء الفيديو: {str(e)}")
        return None
    
    finally:
        # تنظيف الملف المؤقت
        if os.path.exists(temp_output):
            os.remove(temp_output)

def main():
    st.title("معالجة الفيديو")
    
    uploaded_file = st.file_uploader("رفع فيديو (أقصى مدة 30 ثانية)", type=["mp4"])
    
    if uploaded_file is not None:
        try:
            # عرض شريط التقدم
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # قراءة بيانات الفيديو
            video_bytes = uploaded_file.read()
            
            status_text.text("جاري تحويل الفيديو إلى إطارات...")
            frames = read_video_frames(video_bytes)
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
            output_video_bytes = create_video_from_frames(processed_frames)
            
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