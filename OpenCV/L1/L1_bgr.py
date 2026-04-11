import cv2

img = cv2.imread('image.png', 1)
B,G,R = cv2.split(img)

cv2.imshow('imgB', B)
cv2.imwrite('B_img.png', B)
cv2.waitKey(0)

cv2.imshow('imgG', G)
cv2.imwrite('G_img.png', G)
cv2.waitKey(0)

cv2.imshow('imgR', R)
cv2.imwrite('R_img.png', R)
cv2.waitKey(0)

cv2.destroyAllWindows()