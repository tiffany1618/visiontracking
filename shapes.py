#find horiz rect
for contour in contours:
    x,y,w,h = cv.boundingRect(contour)
    aspectRatio = float(h)/w
    if h > 10 and w > 20:
        if aspectRatio > 0.3 and aspectRatio < 0.6:
        	contoursFinal.append(contour)
#find square
