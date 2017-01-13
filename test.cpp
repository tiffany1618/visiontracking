#include <opencv2/core/core.hpp>
#include <opencv2/highgui/highgui.hpp>
#include <opencv2/imgproc/imgproc.hpp>
#include <iostream>
#include <stdio.h>
#include <stdlib.h>

using namespace cv;
using namespace std;

Mat src; 
Mat red;
Mat blue;
vector<vector<Point>> contours_red;
vector<vector<Point>> contours_blue;
vector<vector<Point>> contours_finish;
int thresh = 100;
void contourFinder(Mat, vector<vector<Point>>&, int, void*);

int main(int argc, char** argv)
{

    src = imread("test.png", CV_LOAD_IMAGE_COLOR);

    inRange(src, Scalar(0, 0, 0), Scalar(0, 0, 255), red); 
    inRange(src, Scalar(0, 0, 0), Scalar(255, 0, 0), blue);

    if (!src.data)
    {
        cout << "stuff does not exist" << endl;
        return -1;
    }

    contourFinder(red, contours_red, 0, 0);
    contourFinder(blue, contours_blue,  0, 0); 

    for(int i = 0; i < contours_blue.size(); i++)
    {
        for(int j = 0; j < contours_red.size(); j++)
        {
            if((matchShapes(contours_blue[i], contours_red[j], CV_CONTOURS_MATCH_I1, 0)) <= 0.001) //0.0 = same contour; 0.001 = rotated contour
            {
                contours_finish.push_back(contours_blue[i]);
            }
        }
    }

    for(int i = 0; i < contours_finish.size(); i++)
    {
        drawContours( src, contours_finish, i, Scalar(0, 0, 0), 2, 8, noArray(), 0, Point() );
    }

    namedWindow("stuff", CV_WINDOW_AUTOSIZE);
    imshow("stuff", src);

    waitKey(0);

    return 0;
}

void contourFinder(Mat img, vector<vector<Point>> &contours, int, void*) 
{
    Mat canny_output;
    vector<Vec4i> hierarchy;

    Canny(img, canny_output, thresh, thresh*2, 3);
    findContours(canny_output, contours, hierarchy, CV_RETR_TREE, CV_CHAIN_APPROX_SIMPLE, Point(0,0));

}
