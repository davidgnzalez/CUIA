import cv2

def test_cameras():
    print("🎥 Detectando cámaras disponibles...")
    
    available_cameras = []
    camera_info = {}
    
    # Probar índices del 0 al 10
    for i in range(11):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                height, width = frame.shape[:2]
                resolution = width * height
                camera_info[i] = {'width': width, 'height': height, 'resolution': resolution}
                available_cameras.append(i)
                print(f"📹 Cámara {i}: {width}x{height} ({resolution} píxeles)")
                
                # Mostrar preview por 2 segundos
                cv2.imshow(f"Camera {i} Preview", frame)
                cv2.waitKey(2000)
                cv2.destroyAllWindows()
            cap.release()
        else:
            print(f"❌ Cámara {i}: NO DISPONIBLE")
    
    print(f"\n✅ Cámaras disponibles: {available_cameras}")
    
    # 🎯 MOSTRAR QUÉ CÁMARA SELECCIONARÍA EL SISTEMA
    if available_cameras:
        if 2 in available_cameras:
            selected = 2
            reason = "DroidCam detectado en índice 2 (PRIORIDAD)"
        elif len(available_cameras) > 1:
            non_zero = [i for i in available_cameras if i != 0]
            if non_zero:
                selected = max(non_zero, key=lambda x: camera_info[x]['resolution'])
                reason = f"mayor resolución ({camera_info[selected]['resolution']} píxeles)"
            else:
                selected = 0
                reason = "única opción disponible"
        else:
            selected = available_cameras[0]
            reason = "única cámara disponible"
        
        print(f"🎯 ARCar Showroom usará: Cámara {selected} ({reason})")
        
        if selected == 2:
            print("✅ PERFECTO: DroidCam será usada automáticamente")
        else:
            print("⚠️ NOTA: DroidCam no detectada, usando fallback")
    
    return available_cameras

if __name__ == "__main__":
    test_cameras()