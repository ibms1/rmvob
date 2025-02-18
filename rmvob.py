import streamlit as st
import cv2
import numpy as np
from ultralytics import YOLO
import tempfile
import os

# عنوان التطبيق
st.title("تطبيق إزالة الأشياء من الفيديو (بديل)")

# تحميل النموذج
@st.cache_resource
def load_model():
    return YOLO('yolov8n.pt')

yolo_model = load_model()

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

# إنشاء قناع (Mask) للأشياء المراد إزالتها
def generate_mask(frame, results):
    mask = np.zeros_like(frame[:, :, 0])
    for result in results:
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
            cv2.rectangle(mask, (x1, y1), (x2, y2), 255, -1)
    return mask

# التعبئة (Inpainting) باستخدام OpenCV
def inpaint_frame(frame, mask):
    return cv2.inpaint(frame, mask, inpaintRadius=3, flags=cv2.INPAINT_TELEA)

# تحويل الإطارات إلى فيديو
def frames_to_video(frames, output_path, fps):
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (frames[0].shape[1], frames[0].shape[0]))
    for frame in frames:
        out.write(frame)
    out.release()

# معالجة الفيديو
def process_video(video_path, output_path):
    frames = video_to_frames(video_path)
    processed_frames = []
    for frame in frames:
        results = yolo_model(frame)
        mask = generate_mask(frame, results)
        inpainted_frame = inpaint_frame(frame, mask)
        processed_frames.append(inpainted_frame)
    frames_to_video(processed_frames, output_path, 30)

# واجهة المستخدم
uploaded_file = st.file_uploader("قم بتحميل فيديو", type=["mp4", "mov", "avi"])
if uploaded_file:
    # حفظ الفيديو المؤقت
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_file:
        tmp_file.write(uploaded_file.read())
        video_path = tmp_file.name

    # عرض الفيديو الأصلي
    st.video(video_path)

    # معالجة الفيديو
    if st.button("إزالة الأشياء"):
        with st.spinner("جاري المعالجة..."):
            output_path = "output_video.mp4"
            process_video(video_path, output_path)
            st.success("تمت المعالجة بنجاح!")
            st.video(output_path)
            os.remove(output_path)  # حذف الفيديو المعالج بعد التحميل

    # حذف الفيديو المؤقت
    os.remove(video_path)