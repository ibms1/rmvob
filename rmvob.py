import streamlit as st
import numpy as np
import os
import tempfile
import cv2

def read_video_frames(video_bytes):
    """تحويل الفيديو إلى إطارات"""
    temp_path = "temp_input.mp4"
    try:
        with open(temp_path, "wb") as f:
            f.write(video_bytes)
        
        cap = cv2.VideoCapture(temp_path)
        frames = []
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            frames.append(frame)
        
        cap.release()
        return frames
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

def process_frame(frame, mask):
    """معالجة الإطار مع إخفاء المنطقة المحددة"""
    try:
        # نسخة من الإطار
        processed = frame.copy()
        
        # تطبيق التعتيم على المنطقة المحددة
        processed[mask > 0] = cv2.inpaint(
            frame,
            mask,
            3,
            cv2.INPAINT_TELEA
        )[mask > 0]
        
        return processed
    except Exception as e:
        st.error(f"خطأ في معالجة الإطار: {str(e)}")
        return None

def create_video_from_frames(frames, fps=30):
    """تحويل الإطارات إلى فيديو"""
    if not frames:
        return None
    
    temp_output = "temp_output.mp4"
    try:
        height, width = frames[0].shape[:2]
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(temp_output, fourcc, fps, (width, height))
        
        for frame in frames:
            if frame is not None:
                out.write(frame)
        
        out.release()
        
        with open(temp_output, 'rb') as f:
            video_bytes = f.read()
        
        return video_bytes
    finally:
        if os.path.exists(temp_output):
            os.remove(temp_output)

def create_selection_mask(frame, regions):
    """إنشاء قناع للمناطق المحددة"""
    mask = np.zeros(frame.shape[:2], dtype=np.uint8)
    for region in regions:
        x1, y1, x2, y2 = region
        cv2.rectangle(mask, (x1, y1), (x2, y2), 255, -1)
    return mask

def main():
    st.title("تطبيق إزالة الأشياء من الفيديو")
    
    uploaded_file = st.file_uploader("رفع فيديو", type=["mp4"])
    
    if uploaded_file is not None:
        # قراءة الفيديو
        video_bytes = uploaded_file.read()
        frames = read_video_frames(video_bytes)
        
        if not frames:
            st.error("لم يتم العثور على إطارات في الفيديو")
            return
        
        # عرض الإطار الأول للاختيار
        first_frame = frames[0]
        height, width = first_frame.shape[:2]
        
        # تحويل الإطار إلى صورة
        st.image(cv2.cvtColor(first_frame, cv2.COLOR_BGR2RGB), caption="اختر المناطق المراد إزالتها")
        
        # إدخال إحداثيات المناطق المراد إزالتها
        st.write("أدخل إحداثيات المناطق المراد إزالتها (x1,y1,x2,y2)")
        
        # قائمة لتخزين المناطق المحددة
        regions = []
        
        col1, col2 = st.columns(2)
        with col1:
            x1 = st.number_input("X1", 0, width, 0)
            y1 = st.number_input("Y1", 0, height, 0)
        with col2:
            x2 = st.number_input("X2", 0, width, 100)
            y2 = st.number_input("Y2", 0, height, 100)
        
        if st.button("إضافة منطقة"):
            regions.append((int(x1), int(y1), int(x2), int(y2)))
            st.success("تمت إضافة المنطقة")
        
        # عرض المناطق المحددة
        if regions:
            st.write("المناطق المحددة:")
            for i, region in enumerate(regions):
                st.write(f"المنطقة {i+1}: {region}")
        
        if regions and st.button("معالجة الفيديو"):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # إنشاء قناع للمناطق المحددة
            mask = create_selection_mask(first_frame, regions)
            
            # معالجة الإطارات
            status_text.text("جاري معالجة الإطارات...")
            processed_frames = []
            total_frames = len(frames)
            
            for i, frame in enumerate(frames):
                processed_frame = process_frame(frame, mask)
                if processed_frame is not None:
                    processed_frames.append(processed_frame)
                progress = (i + 1) / total_frames
                progress_bar.progress(progress)
            
            # إنشاء الفيديو النهائي
            status_text.text("جاري إنشاء الفيديو النهائي...")
            output_video_bytes = create_video_from_frames(processed_frames)
            
            if output_video_bytes:
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

if __name__ == "__main__":
    main()