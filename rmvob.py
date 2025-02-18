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
        fourcc = cv2.VideoWriter_fourcc(*'avc1')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height), isColor=False)
        
        for frame in frames:
            if frame is not None:
                out.write(frame)
        
        out.release()
        return True
    except Exception as e:
        st.error(f"خطأ في تحويل الإطارات إلى فيديو: {str(e)}")
        return False

def main():
    st.title("معالجة الفيديو")
    
    uploaded_file = st.file_uploader("رفع فيديو (أقصى مدة 30 ثانية)", type=["mp4"])
    
    if uploaded_file is not None:
        # تهيئة المتغيرات للملفات المؤقتة
        temp_video_path = "temp_video.mp4"
        output_video_path = "output_video.mp4"
        video_bytes = None  # متغير لتخزين بيانات الفيديو
        
        try:
            # عرض شريط التقدم
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # حفظ الفيديو المؤقت
            with open(temp_video_path, "wb") as f:
                f.write(uploaded_file.read())
            
            status_text.text("جاري تحويل الفيديو إلى إطارات...")
            frames = video_to_frames(temp_video_path)
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
            
            if frames_to_video(processed_frames, output_video_path):
                progress_bar.progress(0.9)
                status_text.text("جاري تحضير الفيديو للعرض...")
                
                # قراءة الفيديو في الذاكرة قبل حذف الملف
                try:
                    with open(output_video_path, 'rb') as video_file:
                        video_bytes = video_file.read()
                    
                    progress_bar.progress(1.0)
                    status_text.text("تم معالجة الفيديو بنجاح!")
                    
                    # عرض الفيديو من الذاكرة
                    st.video(video_bytes)
                    
                    # زر التحميل
                    st.download_button(
                        label="تحميل الفيديو الناتج",
                        data=video_bytes,
                        file_name="processed_video.mp4",
                        mime="video/mp4"
                    )
                except Exception as e:
                    st.error(f"خطأ في تحضير الفيديو: {str(e)}")
            
        except Exception as e:
            st.error(f"حدث خطأ: {str(e)}")
        
        finally:
            # تنظيف الملفات المؤقتة بعد التأكد من قراءة الفيديو
            for file_path in [temp_video_path, output_video_path]:
                if os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                    except Exception as e:
                        st.warning(f"تعذر حذف الملف المؤقت {file_path}: {str(e)}")

if __name__ == "__main__":
    main()