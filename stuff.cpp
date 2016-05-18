#include <opencv2/core/core.hpp>
#include <opencv2/highgui/highgui.hpp>
#include <opencv2/imgproc/imgproc.hpp>
#include <iostream>
#include <ctime>
#include <fstream>
#include <raspicam/raspicam_cv.h>
#include <stdio.h>
#include <stdlib.h>

using namespace cv;
using namespace std;
using namespace raspicam;

int main(int argc, char** argv) {

    Mat img;
    RaspiCam_Cv camera;
    cout << "hello sirs" << endl;

    if(!camera.open()) {
        cerr << "ouch" << endl;
    }

    namedWindow("stuff", CV_WINDOW_AUTOSIZE);

    cout << "sleeping" << endl;
    waitKey(3000);
    camera.grab();
    
    camera.retrieve(img);

    imshow("stuff", img);
    waitKey(0);

    return 0;
}
