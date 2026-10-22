import cv2

image = cv2.imread("foodsafe_qr.png")

if image is None:
    print("QR image not found. Check the image path.")

else:
    detector = cv2.QRCodeDetector()


data, points, _ = detector.detectAndDecode(image)

if data:
    print("QR Code successfully scanned!")
    print("Detected URL:", data)
else:
    print("QR code could not be detected.")

