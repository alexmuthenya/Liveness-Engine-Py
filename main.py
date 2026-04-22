from fastapi import FastAPI
from pydantic import BaseModel
import cv2
import numpy as np
import base64
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

app = FastAPI()

#Initialize the Task Landmarker
base_options = python.BaseOptions(model_asset_path='face_landmarker.task')
options = vision.FaceLandmarkerOptions(base_options=base_options,
                                       output_face_blendshapes=True,
output_facial_transformation_matrixes=True,
                                       num_faces=1)
detector = vision.FaceLandmarker.create_from_options(options)

class ImagePayload(BaseModel):
    image: str
    challenge: str

def check_head_pose(image_data, challenge):
    # Decode image
    encoded_data = image_data.split(',')[1]
    nparr = np.frombuffer(base64.b64decode(encoded_data), np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    #Convert to MediaPipe Image object
    rgb_frame = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
    
    # Run detection
    detection_result = detector.detect(mp_image)

    if not detection_result.face_landmarks:
        return {"status": "failed", "message": "No face detected!"}

    #Extract Transformation Matrix for Yaw
    matrix = detection_result.facial_transformation_matrixes[0]    
    # Calculate Yaw (Left/Right) from the matrix
    yaw = np.arctan2(-matrix[0, 2], matrix[2, 2]) * (180 / np.pi)

    # Check proximity (face size in frame)
    face_landmarks = detection_result.face_landmarks[0]
    # Simple width check using eye distance
    dist = abs(face_landmarks[33].x - face_landmarks[263].x) 
    
    if dist < 0.2:
        return {"status": "failed", "message": "Move closer to the circle."}

    if challenge == "LOOK_LEFT" and yaw < -15:
        return {"status": "success", "message": "Good! Now looking left."}
    elif challenge == "LOOK_RIGHT" and yaw > 15:
        return {"status": "success", "message": "Good! Now looking right."}
    elif challenge == "CENTER" and -10 < yaw < 10:
        return {"status": "success", "message": "Face centered."}
    else:
        return {"status": "failed", "message": f"Please {challenge.replace('_', ' ').lower()}"}

@app.post("/verify-pose")
async def verify(payload: ImagePayload):
    return check_head_pose(payload.image, payload.challenge)


@app.get("/domain-expansion")
async def unlimited_void():
    return {
        "user": "Gojo Satoru",
        "technique": "Muryōkūsho (Unlimited Void)",
        "status": "VOID_ACTIVE",
        "perception": "Yowai mo.",
        "ping_result": "Survived the void."
    }
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)